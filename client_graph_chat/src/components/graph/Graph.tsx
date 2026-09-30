import { useState, useCallback } from "react";
import { ReactFlow, Background, MiniMap, applyEdgeChanges, applyNodeChanges, addEdge } from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import styles from "./Graph.module.css"

const initialNodes = [
    {id: "A", position: {x:0, y:0}, data: {label: "Node A"}},
    {id: "B", position: {x:100, y:100}, data: {label: "Node B"}}];
const initialEdges = [{id: "A-B", source: "A", target: "B", type:"step"}];
 
export function Graph() {
  const [nodes, setNodes] = useState(initialNodes);
  const [edges, setEdges] = useState(initialEdges);

  const onNodesChange = useCallback((changes) => setNodes((nodesSnapshot) => applyNodeChanges(changes, nodesSnapshot)), []);
  const onEdgesChange = useCallback((changes) => setEdges((edgesSnapshot) => applyEdgeChanges(changes, edgesSnapshot)), []);
  const onConnect = useCallback((params) => setEdges((edgesSnapshot) => addEdge(params, edgesSnapshot)), []);

  return (
    <div className={styles["graph"]}>
      <div className={styles["graph-container"]}>
        <div className={styles["graph-view"]}>
          <ReactFlow nodes={nodes} edges={edges} onNodesChange={onNodesChange} onEdgesChange={onEdgesChange} onConnect={onConnect} colorMode="system">
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
