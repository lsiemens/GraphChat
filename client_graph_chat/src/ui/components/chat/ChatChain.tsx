import { useClientState } from "@/ui/hooks/useClientState"
import { ChatNode } from "./ChatNode"
import styles from "./ChatChain.module.css"

export function ChatChain() {
  const [clientState] = useClientState();

  const context = clientState.prompt.context;
  return (
    <div className={styles["nodes"]}>
      {context.map((nodeID) => (
        <ChatNode key={nodeID} nodeID={nodeID} />
      ))}
    </div>
  );
}
