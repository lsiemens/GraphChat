import { Vec2 } from "./Vec2"
import type { NodeID } from "./NodeID"
import type { ModelName } from "./ModelName"

interface PromptArgs {
  model: ModelName,
  upstream?: NodeID[],
  content?: string,
  position?: Vec2,
}

export class Prompt {
  public model: ModelName;
  public upstream: NodeID[];
  public content: string;
  public position: Vec2;

  constructor(args: PromptArgs) {
    this.model = args.model;

    if (args.upstream === undefined) {
      this.upstream = [];
    } else {
      this.upstream = args.upstream;
    }

    if (args.content === undefined) {
      this.content = "";
    } else {
      this.content = args.content;
    }

    if (args.position === undefined) {
      this.position = new Vec2();
    } else {
      this.position = args.position;
    }
  }
}
