import { Prompt, Node, type NodeID } from "@/types"
import type { EngineAPI } from "./api/EngineAPI"

export class ClientDriver {
  private readonly api: EngineAPI;

  public prompt: Prompt;
  public nodes: Map<NodeID, Node>;

  constructor(api: EngineAPI) {
    this.api = api;

    // TODO get model
    const model = "Grok-4.20";

    this.prompt = new Prompt({model: model});
    this.nodes = new Map<NodeID, Node>();
  }

  async initialize(): Promise<void> {
    this.nodes = new Map<NodeID, Node>();

    const NodeIDs = await this.api.getNodeIDs();
    console.log("NodeIDs: " + NodeIDs);
    for (const NodeID of NodeIDs) {
      const node = await this.api.getNode(NodeID);

      this.nodes.set(NodeID, node);
      console.log("  Node: " + node.id);
    }
  }
}
