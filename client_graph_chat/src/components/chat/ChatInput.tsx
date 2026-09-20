import { useState } from "react";
import type { NodeData, NodeRequest } from "@/types";

interface Props {
  onSend: (node: NodeData) => void;
}

export function ChatInput({ onSend }: Props) {
  const [text, setText] = useState("");

  function handleSubmit() {
    const trimmed = text.trim();

    if (!trimmed) {
      return;
    }

    const newNodeData: NodeData = {
      id: "temp-" + crypto.randomUUID(),
      model: "model",
      upstream: [],
      request: {timestamp: new Date().toISOString(), content: trimmed},
      reply: null
    };

    onSend(newNodeData);
    setText("");
  }

  function handleKeyDown(event: React.KeyboardEvent<HTMLTextAreaElement>) {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      handleSubmit();
    }
  }

  return (
    <div>
      <textarea
        value={text}
        onChange={(event) => setText(event.target.value)}
        onKeyDown={handleKeyDown}
        placeholder="Ask anything"
        rows={3}
      />

      <div>
        <button type="button">
          Settings 
        </button>
        <button type="button" onClick={handleSubmit} disabled={!text.trim()}>
          Send
        </button>
      </div>
    </div>
  );
}
