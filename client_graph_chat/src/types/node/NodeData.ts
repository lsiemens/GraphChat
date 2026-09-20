export interface NodeData {
  id: string;
  model: string;
  upstream: string[];
  request: NodeRequest;
  reply: NodeReply | null;
}

export interface NodeRequest {
  timestamp: string;
  content: string;
}

export interface NodeReply {
  timestamp: string;
  content: string;
  status: string;
  usage: NodeUsage;
}

export interface NodeUsage {
  promptTokens: number;
  completionTokens: number;
  costUSD?: number | null;
}
