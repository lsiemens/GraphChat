import { useState } from "react";
import type { Prompt } from "@/types";
import styles from "./ChatInput.module.css"

interface Props {
  onSend: (prompt: Prompt) => Promise<void>;
  disabled?: boolean;
}

export function ChatInput({ onSend, disabled = false }: Props) {
  const [text, setText] = useState("");

  function handleSubmit() {
    const trimmed = text.trim();

    if (!trimmed) {
      return;
    }

    const prompt: Prompt = {
      model: "model",
      upstream: [],
      timestamp: new Date().toISOString(),
      content: trimmed,
    };

    onSend(prompt);
    setText("");
  }

  function handleKeyDown(event: React.KeyboardEvent<HTMLTextAreaElement>) {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      handleSubmit();
    }
  }

  // TODO add proper handling of disabled
  return (
    <div className={styles.input}>
      <div className={styles.textarea}>
        <textarea
          value={text}
          onChange={(event) => setText(event.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask anything"
          rows={3}
          disabled={disabled}
        />
      </div>

      <div className={styles.controls}>
        <button type="button" disabled={disabled}>
          Settings 
        </button>
        <button type="button" onClick={handleSubmit} disabled={!text.trim()}>
          Send
        </button>
      </div>
    </div>
  );
}
