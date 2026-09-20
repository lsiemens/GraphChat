import type { NodeData, NodeRequest } from "@/types";
import { ChatNode } from "./ChatNode";

interface Props {
  nodes: NodeData[];
};

export function ChatChain({ nodes }: Props) {
  return (
    <>
      {nodes.map((node) => (
        <ChatNode key={node.id} node={node} />
      ))}
    </>
  );
}
