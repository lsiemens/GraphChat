import { useState, useRef } from "react"
import { Prompt } from  "@/types"
import { useClient } from "@/ui/hooks/useClient"
import styles from "./ChatInput.module.css"

export function ChatInput() {
  const { state, client } = useClient();
  const [isSending, setIsSending] = useState(false);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  let disabled = isSending;
  const isEmpty = !state.prompt.content.trim();

  async function handleSubmit() {
    if (isEmpty) {
      return;
    }

    setIsSending(true);
    await client.submitPrompt();
    setIsSending(false);

    // use a timer to some setup in the browser before focus can be returned
    setTimeout(() => {
      textareaRef.current?.focus();
    }, 0);
  }

  function handleKeyDown(event: React.KeyboardEvent<HTMLTextAreaElement>): void {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      handleSubmit();
    }
  }

  function onChange(event: React.ChangeEvent<HTMLTextAreaElement>): void {
    const prompt = state.prompt;
    const newPrompt = new Prompt({
        model: prompt.model,
        upstream: prompt.upstream,
        context: prompt.context,
        content: event.target.value,
    });
    client.updatePrompt(newPrompt);
  }

  return (
    <div className={styles["input"]}>
      <div className={styles["textarea"]}>
        <textarea
          ref={textareaRef}
          value={state.prompt.content}
          onChange={onChange}
          onKeyDown={handleKeyDown}
          placeholder="Ask anything"
          rows={3}
          disabled={disabled}
        />
      </div>

      <div className={styles["controls"]}>
        <button type="button" disabled={disabled}>
          Settings 
        </button>
        <button type="button" onClick={handleSubmit} disabled={isEmpty || disabled}>
          Send
        </button>
      </div>
    </div>
  );
}
