import type { NodeID } from "@/types"
import { useClient } from "@/ui/hooks/useClient"
import styles from "./ChatNode.module.css"

interface Props {
  nodeID: NodeID;
};

export function ChatNode({ nodeID }: Props) {
  const { client } = useClient();

  const node = client.getNodeByID(nodeID);

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
