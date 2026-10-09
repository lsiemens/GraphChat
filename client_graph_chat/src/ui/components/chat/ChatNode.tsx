import type { NodeID } from "@/types"
import { useClientState } from "@/ui/hooks/useClientState"
import styles from "./ChatNode.module.css"

interface Props {
  nodeID: NodeID;
};

export function ChatNode({ nodeID }: Props) {
  const [, reactClient] = useClientState();

  const node = reactClient.getNodeByID(nodeID);

  return (
    <div className={styles["node"]}>
      <div className={styles["request"]}>
        {node.request}
      </div>

      {node.reply !== null && (
        <div className={styles["reply"]}>
          {node.reply}
        </div>
      )}
    </div>
  );
}
