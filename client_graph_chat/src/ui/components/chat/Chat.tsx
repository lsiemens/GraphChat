import { useClient } from "@/ui/hooks/useClient"
import { ChatChain } from "./ChatChain";
import { ChatInput } from "./ChatInput";
import styles from "./Chat.module.css"

function StatusBar() {
  const { state } = useClient();

  if (!state.status.message) {
    return null;
  }

  return (
    <div className={styles["status-bar"]}>
      <span>{state.status.message}</span>
      {state.status.details && (
        <div className={styles["status-tooltip"]}>
          {state.status.details}
        </div>
      )}
    </div>
  );
}

export function Chat() {
  return (
    <div className={styles["chat"]}>
      <ChatChain />
      <StatusBar />
      <ChatInput />
    </div>
  );
}
