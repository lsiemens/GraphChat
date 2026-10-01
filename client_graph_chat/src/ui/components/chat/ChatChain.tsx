import type { NodeData } from "@/client-driver/api/NodeData";
import { ChatNode } from "./ChatNode";
import styles from "./ChatChain.module.css"

interface Props {
  nodes: NodeData[];
};

export function ChatChain({ nodes }: Props) {
  return (
    <div className={styles["nodes"]}>
      {nodes.map((node) => (
        <ChatNode key={node.id} node={node} />
      ))}
    </div>
  );
}
