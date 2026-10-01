import { Prompt, Node, type NodeID, toNodeID, toNodeIDs, fromNodeIDs } from "@/types"

/* API Interfaces */

interface NodeAPI {
  id: string;
  upstream: string[];
  request: string;
  reply: string;
  model: string;
  costUSD: number | null;
}

interface PromptAPI {
  model: string;
  upstream: string[];
  timestamp: string;
  content: string;
}

interface NodeIDsAPI {
  ids: string[];
}

/* Type Validation */

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function isStringArray(value: unknown): value is string[] {
  return Array.isArray(value) && value.every((element) => typeof element === "string");
}

function isNodeAPI(value: unknown): value is NodeAPI {
  if (!isRecord(value)) return false;

  return (
    typeof value["id"] === "string" &&
    isStringArray(value["upstream"]) &&
    typeof value["request"] === "string" &&
    typeof value["reply"] === "string" &&
    typeof value["model"] === "string" &&
    typeof value["costUSD"] === "number" || value["costUSD"] === null
  );
}

function isNodeIDsAPI(value: unknown): value is NodeIDsAPI {
  if (!isRecord(value)) return false;

  return isStringArray(value["ids"]);
}

/* Internal Type Conversion */

function toNodeAPI(input: unknown): NodeAPI {
  if (!isNodeAPI(input)) {
    throw new Error("Input data did match NodeAPI");
  }

  return input;
}

function toNodeIDsAPI(input: unknown): NodeIDsAPI {
  if (!isNodeIDsAPI(input)) {
    throw new Error("Input data did not match NodeIDsAPI");
  }

  return input;
}

/* Type Convsion */

export function apiToNode(input: unknown): Node {
  const nodeAPI = toNodeAPI(input);

  const data  = {
    id: toNodeID(nodeAPI.id),
    upstream: toNodeIDs(nodeAPI.upstream),
    request: nodeAPI.request,
    reply: nodeAPI.reply,
    model: nodeAPI.model,
    costUSD: nodeAPI.costUSD,
  };
  return new Node(data);
}

export function apiFromPrompt(prompt: Prompt): PromptAPI {
  const data = {
    model: prompt.model,
    upstream: fromNodeIDs(prompt.upstream),
    timestamp: new Date().toISOString(),
    content: prompt.content,
  };

  return data;
}

export function apiToNodeIDs(input: unknown): NodeID[] {
  const nodeIDsAPI = toNodeIDsAPI(input);

  return toNodeIDs(nodeIDsAPI.ids);
}
