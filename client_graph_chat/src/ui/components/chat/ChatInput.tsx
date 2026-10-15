import { useState, useRef } from "react"
import { fromModelName, toModelName } from  "@/types"
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

  return (
    <div className={styles["input"]}>
      <div className={styles["textarea"]}>
        <textarea
          ref={textareaRef}
          value={state.prompt.content}
          onChange={(event) => client.updatePromptContent(event.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask anything"
          rows={3}
          disabled={disabled}
        />
      </div>

      <div className={styles["controls"]}>
        {(state.prompt.model !== null) && (
          <select id="models"
            value={fromModelName(state.prompt.model)}
            onChange={(event) => client.updatePromptModel(toModelName(event.target.value))}
            disabled={disabled}
          >
            {state.models.map((model) => (
              <option key={model} value={fromModelName(model)}>{fromModelName(model)}</option>
            ))}
          </select>
        )}
        <button type="button" onClick={handleSubmit} disabled={isEmpty || disabled}>
          Send
        </button>
      </div>
    </div>
  );
}
