import { useState } from "react";
import type { NodeData, NodeRequest } from "@/types";
import { ChatChain } from "./ChatChain";
import { ChatInput } from "./ChatInput";

const testChain: NodeData[] = [
  {
    id: "1",
    model: "mock",
    upstream: [],
    request: {timestamp: "time request", content: "Test message"},
    reply: {timestamp: "time reply",
            content: "Test reply",
            status: "finished",
            usage: {promptTokens: 1, completionTokens: 2}},
  }
];

export function Chat() {
  const [nodeChain, setNodeChain] = useState<NodeData[]>(testChain);

  function handleSend(node: NodeData) {
    setNodeChain((current) => [...current, node]);
  }

  return (
    <div>
      <header>
        <h2>Chat</h2>
      </header>
      
      <ChatChain nodes={nodeChain} />
      <ChatInput onSend={handleSend} />
    </div>
  );
}
