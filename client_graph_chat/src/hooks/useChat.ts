import { useState } from "react";
import type { Prompt, NodeData } from "@/types";
import { sendMessage } from "../api/chatAPI";

const testNodes: NodeData[] = [
  {
    id: "1",
    model: "mock",
    upstream: [],
    request: {timestamp: "time request", content: "Test message"},
    reply: null
  },
];

export function useChat() {
  const [nodes, setNodes] = useState<NodeData[]>(testNodes);
  const [isSending, setIsSending] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSend(prompt: Prompt) {
    setError(null);
    setIsSending(true);

    try {
      const newNode = await sendMessage(prompt);

      setNodes((current) => [...current, newNode]);
    } catch (error) {
      console.error("Graph Chat failed to send node: ", error);
      setError("Unable to send message. Please try again.");
    } finally {
      setIsSending(false);
    }
  }

  return {nodes, sendNode: handleSend, isSending, error};
}
