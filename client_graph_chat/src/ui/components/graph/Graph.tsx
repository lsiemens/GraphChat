import { useState, useCallback, useEffect } from "react";
import type { NodeID } from "@/types"
import { ReactFlow, Background, MiniMap, useNodesState, useEdgesState, applyEdgeChanges } from "@xyflow/react";
import type { Node, Edge, OnConnect, OnEdgesChange } from "@xyflow/react"
import { type ClientState, ReactClient } from "@/client-driver/ReactClient"
import { useClientState } from "@/ui/hooks/useClientState"
import { createPromptNode, createFullNode, promptNodeView, fullNodeView, type GraphNode } from "./GraphNodes"
import "@xyflow/react/dist/style.css";
import styles from "./Graph.module.css"

function createEdge(sourceID: NodeID, targetID: NodeID, deletable: boolean): Edge {
  return {
    id: `${sourceID} -> ${targetID}`,
    source: sourceID,
    target: targetID,
    deletable: deletable,
  };
}

function reconcileNodes(current: GraphNode[], nodeIDs: ReadonlySet<NodeID>): GraphNode[] {
  const next = current.filter(node => (node.type === "promptNode") || nodeIDs.has(node.id as NodeID));

  const filteredIDs = new Set(next.map(node => node.id as NodeID));
  for (const nodeID of nodeIDs) {
    if (!filteredIDs.has(nodeID)) {
      next.push(createFullNode({x:Math.random()*500, y:Math.random()*500}, nodeID));
    }
  }
  return next;
}

function reconcileEdges(current: Edge[], nodeIDs: ReadonlySet<NodeID>, clientState: ClientState, reactClient: ReactClient): Edge[] {
  const next: Edge[] = [];

  for (const targetID of nodeIDs) {
    const targetNode = reactClient.getNodeByID(targetID);
    for (const sourceID of targetNode.upstream) {
      next.push(createEdge(sourceID, targetID, false));
    }
  }

  for (const sourceID of clientState.prompt.upstream) {
    next.push(createEdge(sourceID, "Prompt", true));
  }
  return next;
}

export function Graph() {
  const [clientState, reactClient] = useClientState();

  const [nodes, setNodes, onNodesChange] = useNodesState<GraphNode>([createPromptNode({x:0, y:0})]);
  const [edges, setEdges] = useEdgesState([]);

  const nodeIDs = clientState.nodeIDs;

  useEffect(() => {
    setNodes(current => reconcileNodes(current, nodeIDs));
    setEdges(current => reconcileEdges(current, nodeIDs, clientState, reactClient));
    }, [nodeIDs, clientState, reactClient, setNodes, setEdges]);

  const onConnect: OnConnect = useCallback(async (connection) => {
    if (connection.source == null || connection.target !== "Prompt") {
      return;
    }

    const sourceID = connection.source as NodeID;
    const prompt = clientState.prompt;
    if (prompt.upstream.includes(sourceID)) {
      return;
    }

    const newUpstream = [...prompt.upstream, sourceID];
    await reactClient.updatePromptUpstream(newUpstream);
  }, [clientState, reactClient]);

  const onEdgesChange: OnEdgesChange = useCallback(async (changes) => {
    for (const change of changes) {
      if (change.type === "remove") {
        const edge = edges.find(edge => edge.id === change.id);

        const sourceID = edge.source as NodeID;
        const prompt = clientState.prompt;

        const newUpstream = prompt.upstream.filter(nodeID => nodeID !== sourceID);
        await reactClient.updatePromptUpstream(newUpstream);
      }
    }

    setEdges(current => applyEdgeChanges(changes, current));
  }, [edges, setEdges, clientState, reactClient]);


  const nodeTypes = { promptNode: promptNodeView, fullNode: fullNodeView };

  return (
    <div className={styles["graph"]}>
      <div className={styles["graph-container"]}>
        <div className={styles["graph-view"]}>
          <ReactFlow
              nodes={nodes}
              edges={edges}
              nodeTypes={nodeTypes}
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
