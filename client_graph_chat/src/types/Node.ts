import { type NodeID, NodeIDToString } from "./NodeID"
import type { ModelName } from "./ModelName"

interface NodeArgs {
  id: NodeID,
  upstream: NodeID[],
  context: NodeID[],
  request: string,
  reply: string,
  model: ModelName,
  costUSD: number | null,
}

export class Node {
  readonly id: NodeID;
  readonly upstream: readonly NodeID[];
  readonly context: readonly NodeID[];
  readonly request: string;
  readonly reply: string;
  readonly model: ModelName;
  readonly costUSD: number | null;

  constructor(args: NodeArgs) {
    this.id = args.id;
    this.upstream = args.upstream;
    this.context = args.context;
    this.request = args.request;
    this.reply = args.reply;
    this.model = args.model;
    this.costUSD = args.costUSD;
  }

  public toString(): string {
    return `Node(id=${NodeIDToString(this.id)}, context.length=${this.context.length}, reply="${this.reply}")`;
  }
}
