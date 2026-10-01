import { Position, Handle } from "@xyflow/react";
import type { Node, NodeProps, XYPosition } from "@xyflow/react";
import type { Prompt, NodeData } from "@/types"
import styles from "./GraphNodes.module.css"

type PromptNode = Node<{ prompt: Prompt }, "promptNode">;
type FullNode = Node<{ nodeData: NodeData }, "fullNode">;

export function createFullNode(position: XYPosition, nodeData: NodeData): FullNode {
  return {
    id:nodeData.id,
    type:"fullNode",
    position: position,
    deletable: false,
    data: { nodeData: nodeData },
  };
}

export function createPromptNode(position: XYPosition, prompt: Prompt): PromptNode {
  return {
    id:"Prompt",
    type:"promptNode",
    position: position,
    deletable: false,
    data: { prompt: prompt },
  };
}

export function PromptNode({ data }: NodeProps<PromptNode>) {
  return(
    <div className={styles["node"]}>
      <div>Prompt: {data.prompt.content.slice(0, 3)}</div>
      <Handle type="target" position={Position.Top} />
    </div>
  );
}

export function FullNode({ data }: NodeProps<FullNode>) {
  return(
    <div className={styles["node"]}>
      <div>ID: {data.nodeData.id.slice(0, 3)}</div>
      <Handle type="source" position={Position.Bottom} />
      <Handle type="target" isConnectable={false} position={Position.Top} />
    </div>
  );
}

