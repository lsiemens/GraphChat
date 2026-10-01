import { useState } from "react";
import type { Prompt, NodeData } from "@/client-driver/api/NodeData";
import { sendMessage } from "@/client-driver/api/chatAPI";

const testNodes: NodeData[] = [];

export function useChat() {
  const [nodes, setNodes] = useState<NodeData[]>(testNodes);
  const [isSending, setIsSending] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSend(prompt: Prompt) {
    setError(null);
    setIsSending(true);

    try {
      const lastNode = nodes[nodes.length - 1];

      // # TODO properly set the context
      if (lastNode === undefined) {
        prompt.upstream = [];
      } else {
        prompt.upstream = [ lastNode.id ];
      }
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
