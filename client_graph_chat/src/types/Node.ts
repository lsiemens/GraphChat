import { Vec2 } from "./Vec2"
import type { NodeID } from "./NodeID"
import type { ModelName } from "./ModelName"

interface NodeArgs {
  id: NodeID,
  upstream: NodeID[],
  request: string,
  reply: string,
  model: ModelName,
  costUSD: number | null,
  position?: Vec2,
}

export class Node {
  readonly id: NodeID;
  readonly upstream: readonly NodeID[];
  readonly request: string;
  readonly reply: string;
  readonly model: ModelName;
  readonly costUSD: number | null;
  public position: Vec2;

  constructor(args: NodeArgs) {
    this.id = args.id;
    this.upstream = args.upstream;
    this.request = args.request;
    this.reply = args.reply;
    this.model = args.model;
    this.costUSD = args.costUSD;

    if (args.position === undefined) {
      this.position = new Vec2();
    } else {
      this.position = args.position;
    }
  }
}
