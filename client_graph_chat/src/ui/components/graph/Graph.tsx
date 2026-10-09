import { useCallback, useEffect } from "react";
import { PROMPT_ID, NODE_TYPES, type GraphNode } from "./GraphNode"
import { type NodeID, fromNodeID, toNodeID } from "@/types"
import { ReactFlow, Background, MiniMap, useNodesState, useEdgesState, applyEdgeChanges } from "@xyflow/react";
import type { Edge, OnConnect, OnEdgesChange } from "@xyflow/react"
import { type ClientState, ClientInterface } from "@/client-driver/ClientInterface"
import { useClient } from "@/ui/hooks/useClient"
import { createPromptNode, createDataNode } from "./GraphNode"
import "@xyflow/react/dist/style.css";
import styles from "./Graph.module.css"

function createEdge(sourceID: string, targetID: string, deletable: boolean): Edge {
  return {
    id: `${sourceID} -> ${targetID}`,
    source: sourceID,
    target: targetID,
    deletable: deletable,
  };
}

function reconcileNodes(current: readonly GraphNode[], nodeIDs: ReadonlySet<NodeID>): GraphNode[] {
  const next = current.filter(node => (node.id === PROMPT_ID) || nodeIDs.has(toNodeID(node.id)));

  const filteredIDs = new Set(next.map(node => node.id));
  for (const nodeID of nodeIDs) {
    if (!filteredIDs.has(fromNodeID(nodeID))) {
      next.push(createDataNode({x:Math.random()*500, y:Math.random()*500}, nodeID));
    }
  }
  return next;
}

function reconcileEdges(nodeIDs: ReadonlySet<NodeID>, state: ClientState, client: ClientInterface): Edge[] {
  const next: Edge[] = [];

  for (const targetID of nodeIDs) {
    const targetNode = client.getNodeByID(targetID);
    for (const sourceID of targetNode.upstream) {
      next.push(createEdge(fromNodeID(sourceID), fromNodeID(targetID), false));
    }
  }

  for (const sourceID of state.prompt.upstream) {
    next.push(createEdge(fromNodeID(sourceID), PROMPT_ID, true));
  }
  return next;
}

export function Graph() {
  const { state, client } = useClient();

  const [nodes, setNodes, onNodesChange] = useNodesState<GraphNode>([createPromptNode({x:0, y:0})]);
  const [edges, setEdges] = useEdgesState<Edge>([]);

  const nodeIDs = state.nodeIDs;

  useEffect(() => {
    setNodes(current => reconcileNodes(current, nodeIDs));
    setEdges(() => reconcileEdges(nodeIDs, state, client));
    }, [nodeIDs, state, client, setNodes, setEdges]);

  const onConnect: OnConnect = useCallback(async (connection) => {
    if (connection.source == null || connection.target !== PROMPT_ID) {
      return;
    }

    const sourceID = toNodeID(connection.source);
    const prompt = state.prompt;
    if (prompt.upstream.includes(sourceID)) {
      return;
    }

    const newUpstream = [...prompt.upstream, sourceID];
    await client.updatePromptUpstream(newUpstream);
  }, [state, client]);

  const onEdgesChange: OnEdgesChange = useCallback(async (changes) => {
    for (const change of changes) {
      if (change.type === "remove") {
        const edge = edges.find(edge => edge.id === change.id);

        if (edge === undefined) {
          throw new Error("Failed to find edge for removal.");
        }

        const sourceID = toNodeID(edge.source);
        const prompt = state.prompt;

        const newUpstream = prompt.upstream.filter(nodeID => nodeID !== sourceID);
        await client.updatePromptUpstream(newUpstream);
      }
    }

    setEdges(current => applyEdgeChanges(changes, current));
  }, [edges, setEdges, state, client]);



  return (
    <div className={styles["graph"]}>
      <div className={styles["graph-container"]}>
        <div className={styles["graph-view"]}>
          <ReactFlow
              nodes={nodes}
              edges={edges}
              nodeTypes={NODE_TYPES}
              onNodesChange={onNodesChange}
              onEdgesChange={onEdgesChange}
              onConnect={onConnect}
              colorMode="system">
            <MiniMap position="bottom-left" zoomable pannable/>
            <Background />
          </ReactFlow>
        </div>
        <div className={styles["graph-info"]}>
          INFO BAR
        </div>
      </div>
    </div>
  );
}
