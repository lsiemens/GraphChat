import type { NodeID } from "./NodeID"
import type { ModelName } from "./ModelName"

interface PromptArgs {
  readonly model: ModelName | null,
  readonly upstream: readonly NodeID[],
  readonly context: readonly NodeID[],
  readonly content: string,
}

export class Prompt {
  readonly model: ModelName | null;
  readonly upstream: readonly NodeID[];
  readonly context: readonly NodeID[];
  readonly content: string;

  constructor(args: PromptArgs) {
    this.model = args.model;
    this.upstream = args.upstream;
    this.context = args.context;
    this.content = args.content;
  }

  public toString(): string {
    return `Prompt(context.length=${this.context.length}, content="${this.content}")`;
  }
}
