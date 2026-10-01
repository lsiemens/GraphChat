import { useChat } from "@/ui/hooks/useChat";
import { ChatChain } from "./ChatChain";
import { ChatInput } from "./ChatInput";
import styles from "./Chat.module.css"

export function Chat() {
  const {nodes, sendNode, isSending, error} = useChat();

  return (
    <div className={styles["chat"]}>
      <ChatChain nodes={nodes} />

      {error && (<div>{error}</div>)}

      <ChatInput onSend={sendNode} disabled={isSending} />
    </div>
  );
}
