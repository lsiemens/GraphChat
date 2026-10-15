import { Prompt, Node, type NodeID, fromNodeID, ClientError } from "@/types"

interface Graph {
  readonly prompt: Prompt,
  readonly nodes: ReadonlyMap<NodeID, Node>,
};

interface Vec2 {
  x: number,
  y: number,
};

interface LayeredNode {
  upstream: Set<string>;
  downstream: Set<string>;
  depth: number;
};

export class GraphLayout {
  public nodeHeight = 20;
  public nodeWidth = 250;
  public layerHeight: number;

  public layoutMethod: (promptID: string, graph: Graph) => ReadonlyMap<string, Vec2>;

  public sugiyamaMaxRelaxationSteps = 5;

  constructor() {
    this.layerHeight = 3*this.nodeHeight;
    this.layoutMethod = this.sugiyamaGraph;
  }

  public getLayout(promptID: string, graph: Graph): ReadonlyMap<string, Vec2> {
    return this.layoutMethod(promptID, graph);
  }

  private sugiyamaLayeredNodes(promptID: string, graph: Graph): ReadonlyMap<string, LayeredNode> {
    const layeredNodes = new Map<string, LayeredNode>();

    const completed = new Set<string>();
    const active = new Set<string>();

    // --- First pass: Construct empty objects --- //
    for (const [nodeID, node] of graph.nodes) {
      const nodeData = {
        upstream: new Set(node.upstream),
        downstream: new Set<NodeID>(),
        depth: Number.NEGATIVE_INFINITY,
      };

      if (nodeData.upstream.size === 0) {
        active.add(fromNodeID(nodeID));
      }
      layeredNodes.set(fromNodeID(nodeID), nodeData);
    }
    const promptData = {
      upstream: new Set(graph.prompt.upstream),
      downstream: new Set<NodeID>(),
      depth: Number.NEGATIVE_INFINITY,
    };
    if (promptData.upstream.size === 0) {
      active.add(promptID);
    }
    layeredNodes.set(promptID, promptData);


    // --- Second pass: Construct downstream --- //
    for (const [nodeID, node] of layeredNodes) {
      for (const upstreamNodeID of node.upstream) {
        const upstreamNode = layeredNodes.get(upstreamNodeID);
        if (upstreamNode === undefined) {
          throw new ClientError("Layout Failure", `Failed to construct downstream, the node ${upstreamNodeID} not found in the graph`);
        }
        upstreamNode.downstream.add(nodeID);
      }
    }


    // --- Third pass: Find depth --- //
    function visit(activeID: string): boolean {
      const activeNode = layeredNodes.get(activeID);
      if (activeNode === undefined) {
        throw new ClientError("Layout Failure", `Active node not found in the graph: ${activeID}`);
      }

      for (const upstreamNodeID of activeNode.upstream) {
        if (!completed.has(upstreamNodeID)) {
          return false;
        }
      }

      for (const upstreamNodeID of activeNode.upstream) {
        const upstreamNode = layeredNodes.get(upstreamNodeID);
        if (upstreamNode === undefined) {
          throw new ClientError("Layout Failure", "Upstream layered node not found in the graph");
        }
        if (upstreamNode.depth < 0) {
          throw new ClientError("Layout Failure", "Upstream layered node has undefined depth");
        }

        activeNode.depth = Math.max(activeNode.depth, 1 + upstreamNode.depth);
      }
      activeNode.depth = Math.max(activeNode.depth, 0);

      for (const downstreamNodeID of activeNode.downstream) {
        active.add(downstreamNodeID)
      }
      completed.add(activeID);
      active.delete(activeID);
      return true;
    }

    while (active.size > 0) {
      let updated = false;
      for (const activeID of active) {
        if (visit(activeID)) {
          updated = true;
        }
      }

      if (!updated) {
        throw new ClientError("Layout Failure", "Failed to find any updatable nodes in active, this is likely due to a cycle");
      }
    }

    if (completed.size !== layeredNodes.size) {
      throw new ClientError("Layout Failure", "Not all nodes where completed");
    }

    return layeredNodes;
  }

  private getRelaxLayer(layeredNodes: ReadonlyMap<string, LayeredNode>, nodePositions: Map<string, Vec2>) {
    //const updateLocation = this.getBarycenter(nodePositions);
    const updateLocation = this.getEffectiveBarycenter(nodePositions);

    function relaxLayer(layer: Set<string>, useUpstream: boolean) {
      /* --- Get horizonal positions using updateLocation --- */
      let data: [string, number][] = [];
      let depth = Number.NEGATIVE_INFINITY;
      for (const nodeID of layer) {
        const node = layeredNodes.get(nodeID);
        if (node === undefined) {
          throw new ClientError("Layout Failure", "Failed to get node from layer");
        }

        if (depth === Number.NEGATIVE_INFINITY) {
          depth = node.depth;
        }

        if (node.depth !== depth) {
          throw new ClientError("Layout Failure", "When relaxing a layer all nodes must be at the same depth");
        }

        if (useUpstream) {
          data.push([nodeID, updateLocation(nodeID, node.upstream)]);
        } else {
          data.push([nodeID, updateLocation(nodeID, node.downstream)]);
        }
      }

      data.sort((a, b) => a[1] - b[1]);

      /* --- Enforce a fixed offset from the left and right --- */
      let push_right = new Array(data.length).fill(0);
      for (let i = 0; i < data.length; i++) {
        const dataCurrent = data.at(i);
        if (dataCurrent === undefined) {
          throw new ClientError("Layout Failure", "Failed to correct node spacing");
        }
        const xCurrent = dataCurrent[1];
        const xAdjacent = push_right.at(i - 1);

        if ((xAdjacent === undefined) || (i === 0)) {
          push_right[i] = xCurrent;
        } else {
          push_right[i] = Math.max(xCurrent, xAdjacent + 1);
        }
      }

      let push_left = new Array(data.length).fill(0);
      for (let i = data.length - 1; i >= 0; i--) {
        const dataCurrent = data.at(i);
        if (dataCurrent === undefined) {
          throw new ClientError("Layout Failure", "Failed to correct node spacing");
        }
        const xCurrent = dataCurrent[1];
        const xAdjacent = push_left.at(i + 1);

        if ((xAdjacent === undefined) || (i === data.length - 1)) {
          push_left[i] = xCurrent;
        } else {
          push_left[i] = Math.min(xCurrent, xAdjacent - 1);
        }
      }

      /* --- Update positions using a symmetric enforcement of the offset between nodes --- */
      for (let i = 0; i < data.length; i++) {
        const data_i = data.at(i);
        const left = push_left.at(i);
        const right = push_right.at(i);
        if ((data_i === undefined) || (left === undefined) || (right === undefined)) {
          throw new ClientError("Layout Failure", "Failed to correct the node spacing");
        }

        const nodeID = data_i[0];
        const position = {
          x: (left + right)/2,
          y: depth,
        };
        nodePositions.set(nodeID, position);
      }
    }
    return relaxLayer;
  }

  public getBarycenter(nodePositions: ReadonlyMap<string, Vec2>): (nodeID: string, upstream: Set<string>) => number {
    function barycenter(nodeID: string, upstream: Set<string>): number {
      if (upstream.size === 0) {
        const position_0 = nodePositions.get(nodeID);
        if (position_0 === undefined) {
          throw new ClientError("Layout Failure", "Failed to get node position");
        }

        return position_0.x;
      }

      let center = 0;
      for (const nodeID of upstream) {
        const position = nodePositions.get(nodeID);
        if (position === undefined) {
          throw new ClientError("Layout Failure", "Failed to calculate the barycenter of upstream nodes");
        }
        center += position.x;
      }
      return center/upstream.size;
    }
    return barycenter;
  }

  public getEffectiveBarycenter(nodePositions: ReadonlyMap<string, Vec2>): (nodeID: string, upstream: Set<string>) => number {
    function effectiveBarycenter(nodeID: string, upstream: Set<string>): number {
      const position_0 = nodePositions.get(nodeID);
      if (position_0 === undefined) {
        throw new ClientError("Layout Failure", "Failed to get node position");
      }

      if (upstream.size === 0) {
        return position_0.x;
      }

      let center = 0;
      for (const nodeID of upstream) {
        const position = nodePositions.get(nodeID);
        if (position === undefined) {
          throw new ClientError("Layout Failure", "Failed to calculate the barycenter of upstream nodes");
        }
        const n = Math.abs(position.y - position_0.y);
        center += (position.x + (n - 1)*position_0.x)/n;
      }
      return center/upstream.size;
    }
    return effectiveBarycenter;
  }

  private sugiyamaRelaxGraph(layeredNodes: ReadonlyMap<string, LayeredNode>): Map<string, Vec2> {
    /* --- Get the layers --- */
    let nLayers = 0;
    for (const node of layeredNodes.values()) {
      nLayers = Math.max(nLayers, node.depth + 1);
    }

    const layers = Array.from({ length: nLayers }, () => new Set<string>());
    for (const [nodeID, node] of layeredNodes) {
      const layer = layers.at(node.depth);
      if (layer === undefined) {
        throw new ClientError("Layout Failure", "Failed to get layer for node");
      }

      layer.add(nodeID);
    }

    /* --- Set initial node positions --- */
    const nodePositions = new Map<string, Vec2>();
    for (const layer of layers) {
      const nodeIDs = Array.from(layer);
      nodeIDs.forEach((nodeID, index) => {
        const node = layeredNodes.get(nodeID);
        if (node === undefined) {
          throw new ClientError("Layout Failure", "Failed to get node from layer");
        }
        const position = {x: index, y: node.depth};
        nodePositions.set(nodeID, position);
      });
    }

    /* --- Relax the layers --- */
    // Propagate the up and down the layers, flipping direction at the
    // first/last layer
    const relaxLayer = this.getRelaxLayer(layeredNodes, nodePositions);
    let useUpstream = true;
    for (let i = 0; i < this.sugiyamaMaxRelaxationSteps; i++) {
      if (useUpstream) {
        for (const layer of layers) {
          relaxLayer(layer, useUpstream);
        }
      } else {
        for (const layer of [...layers].reverse()) {
          relaxLayer(layer, useUpstream);
        }
      }
      useUpstream = !useUpstream;
    }
    return nodePositions;
  }

  private sugiyamaGraph(promptID: string, graph: Graph): ReadonlyMap<string, Vec2> {
    const layeredNodes = this.sugiyamaLayeredNodes(promptID, graph);

    const nodePositions = this.sugiyamaRelaxGraph(layeredNodes);

    for (const [nodeID, position] of nodePositions) {
      nodePositions.set(nodeID, {
        x: position.x*this.nodeWidth,
        y: position.y*this.layerHeight,
      });
    }
    return nodePositions;
  }
}
