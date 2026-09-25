import { useChat } from "../../hooks/useChat";
import type { NodeData } from "@/types";
import { ChatChain } from "./ChatChain";
import { ChatInput } from "./ChatInput";
import styles from "./Chat.module.css"

export function Chat() {
  const {nodes, sendNode, isSending, error} = useChat();

  return (
    <div className={styles.chat}>
      <header>
        <h2>Chat</h2>
      </header>
      
      <ChatChain nodes={nodes} />

      {error && (<div>{error}</div>)}

      <ChatInput onSend={sendNode} disable={isSending} />
    </div>
  );
}
