import type { Prompt, NodeData } from "@/types";
import {isNodeData} from "../types/node/NodeData"

const API_URL = "http://localhost:8000";

export async function sendMessage(prompt: Prompt): Promise<NodeData> {
  console.log("OUT: " + JSON.stringify(prompt))
  const reply = await fetch(`${API_URL}/graphchat`, {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify(prompt),
  });

  if (!reply.ok) {
    throw new Error(`Graph Chat request failed: ${reply.status}`);
  }

  let txt = await reply.text()
  console.log("IN: " + txt)

  const raw: unknown = await reply.json();

  if (!isNodeData(raw)) {
    throw new Error("Graph Chat response JSON did not match NodeData");
  }

  return data;
}
