export interface Prompt {
  model: string;
  upstream: string[];
  timestamp: string;
  content: string;
}

export interface NodeData {
  id: string;
  upstream: string[];
  request: string;
  reply: string;
  model: string;
  costUSD: number | null;
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function isStringArray(value: unknown): value is string[] {
  return Array.isArray(value) && value.every((element) => typeof element === "string");
}

export function isNodeData(value: unknown): value is NodeData {
  if (!isRecord(value)) return false;

  return (
    typeof value.id === "string" &&
    isStringArray(value.upstream) &&
    typeof value.request === "string" &&
    typeof value.reply === "string" &&
    typeof value.model === "string" &&
    typeof value.costUSD === "number" || typeof value.costUSD === null
  );
}
