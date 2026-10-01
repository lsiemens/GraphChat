import { useState, useCallback } from "react";
import { ReactFlow, Background, MiniMap, applyEdgeChanges, applyNodeChanges, addEdge } from "@xyflow/react";
import type { Node, Edge, OnNodesChange, OnEdgesChange, OnConnect } from "@xyflow/react";
import { PromptNode, createPromptNode, FullNode, createFullNode } from "./GraphNodes"
import "@xyflow/react/dist/style.css";
import styles from "./Graph.module.css"

const initialNodes: Node[] = [
  createFullNode({x:0, y:0}, {id: "A", upstream: [], request: "request", reply: "reply", model: "Grok-4.20", costUSD: null}),
  createFullNode({x:-100, y:100}, {id: "C", upstream: [], request: "request", reply: "reply", model: "Grok-4.20", costUSD: null}),
  createFullNode({x:-100, y:200}, {id: "D", upstream: [], request: "request", reply: "reply", model: "Grok-4.30", costUSD: null}),
  createPromptNode({x:100, y:100}, {model: "Grok", upstream: [], timestamp: "", content: "This prompt"}),
];
const initialEdges: Edge[] = [{id: "C-D", deletable: false, source: "C", target: "D"}];
 
export function Graph() {
  const [nodes, setNodes] = useState<Node[]>(initialNodes);
  const [edges, setEdges] = useState<Edge[]>(initialEdges);

  const onNodesChange: OnNodesChange = useCallback((changes) => setNodes((nodesSnapshot) => applyNodeChanges(changes, nodesSnapshot)), []);
  const onEdgesChange: OnEdgesChange = useCallback((changes) => setEdges((edgesSnapshot) => applyEdgeChanges(changes, edgesSnapshot)), []);
  const onConnect: OnConnect = useCallback((params) => setEdges((edgesSnapshot) => addEdge(params, edgesSnapshot)), []);

  const nodeTypes = { promptNode: PromptNode, fullNode: FullNode };

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
