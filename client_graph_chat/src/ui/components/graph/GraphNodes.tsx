import { Position, Handle } from "@xyflow/react"
import { useClientState } from "@/ui/hooks/useClientState"
import type { Node, NodeProps, XYPosition } from "@xyflow/react"
import { type NodeID, fromNodeID , nodeIDToString } from "@/types"
import styles from "./GraphNodes.module.css"

type PromptNode = Node<{}, "promptNode">;
type FullNode = Node<{ nodeID: NodeID }, "fullNode">;
export type GraphNode = FullNode | PromptNode;

export function createPromptNode(position: XYPosition): PromptNode {
  return {
    id: "Prompt",
    type: "promptNode",
    position: position,
    deletable: false,
    data: {},
  };
}

export function createFullNode(position: XYPosition, nodeID: NodeID): FullNode {
  return {
    id: nodeID,
    type: "fullNode",
    position: position,
    deletable: false,
    data: { nodeID: nodeID },
  };
}

export function promptNodeView({ data }: NodeProps<PromptNode>) {
  const [clientState, ] = useClientState();
  const prompt = clientState.prompt;
  return(
    <div className={styles["node"]}>
      <div>Prompt: {prompt.content.slice(0, 3)}</div>
      <Handle type="target" position={Position.Top} />
    </div>
  );
}

export function fullNodeView({ data }: NodeProps<FullNode>) {
  const [, reactClient] = useClientState();
  const node = reactClient.getNodeByID(data.nodeID);
  const hasUpstream = (node.upstream.length !== 0);

  return(
    <div className={styles["node"]}>
      <div>ID: {nodeIDToString(data.nodeID)}</div>
      <Handle type="source" position={Position.Bottom} />
      { hasUpstream && (<Handle type="target" isConnectable={false} position={Position.Top} />) }
    </div>
  );
}
