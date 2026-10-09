import { useClient } from "@/ui/hooks/useClient"
import { ChatNode } from "./ChatNode"
import styles from "./ChatChain.module.css"

export function ChatChain() {
  const { state } = useClient();

  const context = state.prompt.context;
  return (
    <div className={styles["nodes"]}>
      {context.map((nodeID) => (
        <ChatNode key={nodeID} nodeID={nodeID} />
      ))}
    </div>
  );
}
