import { Node } from "@/types/Node"
import { Prompt } from "@/types/Prompt"

export class ClientDriver {
  public prompt: Prompt;
  public nodes: Map<string, Node>;

  constructor() {
    // TODO initialize ClientDriver
    this.prompt = new Prompt("Model");
    this.nodes = new Map<string, Node>();
  }

  setModel(model: string): void {
    this.prompt.model = model;
  }
}
