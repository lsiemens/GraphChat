import { Position, Handle } from "@xyflow/react"
import type { Node, NodeProps, XYPosition, NodeTypes } from "@xyflow/react"
import { type NodeID, fromNodeID , nodeIDFingerprint } from "@/types"
import { useClientState } from "@/ui/hooks/useClientState"
import styles from "./GraphNode.module.css"

export const PROMPT_ID = "PROMPT_ID";

type PromptNode = Node<{}, "PromptNode">;
type DataNode = Node<{ nodeID: NodeID }, "DataNode">;
export type GraphNode = PromptNode | DataNode;

export const NODE_TYPES = {
    PromptNode: promptNodeView,
    DataNode: dataNodeView
} satisfies NodeTypes;

export function createPromptNode(position: XYPosition): PromptNode {
  return {
    id: PROMPT_ID,
    type: "PromptNode",
    position: position,
    deletable: false,
    data: {},
  };
}

export function createDataNode(position: XYPosition, nodeID: NodeID): DataNode {
  return {
    id: fromNodeID(nodeID),
    type: "DataNode",
    position: position,
    deletable: false,
    data: { nodeID: nodeID },
  };
}

function promptNodeView({ }: NodeProps<PromptNode>) {
  const [clientState, ] = useClientState();
  const prompt = clientState.prompt;
  return(
    <div className={styles["node"]}>
      <div>Prompt: {prompt.content.slice(0, 3)}</div>
      <Handle type="target" position={Position.Top} />
    </div>
  );
}

function dataNodeView({ data }: NodeProps<DataNode>) {
  const [, reactClient] = useClientState();
  const node = reactClient.getNodeByID(data.nodeID);
  const hasUpstream = (node.upstream.length !== 0);

  return(
    <div className={styles["node"]}>
      <div>ID: {nodeIDFingerprint(data.nodeID)}</div>
      <Handle type="source" position={Position.Bottom} />
      { hasUpstream && (<Handle type="target" isConnectable={false} position={Position.Top} />) }
    </div>
  );
}

