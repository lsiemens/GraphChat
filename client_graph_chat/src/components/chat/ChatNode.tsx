import type { NodeData, NodeRequest, NodeReply } from "@/types";
import styles from "./ChatNode.module.css"

interface Props {
  node: NodeData;
};

export function ChatNode({ node }: Props) {
  return (
    <div className={styles.node}>
      <div className={styles.request}>
        {node.request.content}
      </div>

      {node.reply !== null && (
        <div className={styles.reply}>
          {node.reply.content}
        </div>
      )}
    </div>
  );
}
