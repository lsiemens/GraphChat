import { ChatChain } from "./ChatChain";
import { ChatInput } from "./ChatInput";
import styles from "./Chat.module.css"

export function Chat() {
  return (
    <div className={styles["chat"]}>
      <ChatChain />

      {/*error && (<div>{error}</div>)*/}

      <ChatInput />
    </div>
  );
}
