export interface Prompt {
  model: string;
  upstream: string[];
  timestamp: string;
  content: string;
}

export interface NodeData {
  id: string;
  model: string;
  upstream: string[];
  request: NodeRequest;
  reply: NodeReply;
}

export interface NodeRequest {
  timestamp: string;
  content: string;
}

export interface NodeReply {
  timestamp: string;
  content: string;
  finishReason: string;
  usage: NodeUsage;
}

export interface NodeUsage {
  cachedPromptTextTokens: number;
  promptTokens: number;
  reasoningTokens: number;
  completionTokens: number;
  costUSD: number | null;
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function isStringArray(value: unknown): value is string[] {
  return Array.isArray(value) && value.every((element) => typeof element === "string");
}

export function isNodeUsage(value: unknown): value is NodeUsage {
  if (!isRecord(value)) return false;

  return (
    typeof value.cachedPromptTextTokens === "number" &&
    typeof value.promptTokens === "number" &&
    typeof value.reasoningTokens === "number" &&
    typeof value.completionTokens === "number" &&
    typeof value.costUSD === null || typeof value.costUSD === "number"
  );
}

export function isNodeReply(value: unknown): value is NodeReply {
  if (!isRecord(value)) return false;

  return (
    typeof value.timestamp === "string" &&
    typeof value.content === "string" &&
    typeof value.status === "string" &&
    isNodeUsage(value.usage)
  );
}

export function isNodeRequest(value: unknown): value is NodeRequest {
  if (!isRecord(value)) return false;

  return (
    typeof value.timestamp === "string" &&
    typeof value.content === "string"
  );
}

export function isNodeData(value: unknown): value is NodeData {
  if (!isRecord(value)) return false;

  return (
    typeof value.id === "string" &&
    typeof value.model === "string" &&
    isStringArray(value.upstream) &&
    isNodeRequest(value.request) &&
    isNodeReply(value.reply)
  );
}
