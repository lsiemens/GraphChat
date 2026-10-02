import { Prompt, Node, type NodeID, type ModelName } from "@/types"
import type { EngineAPI } from "./api/EngineAPI"

export class ClientDriver {
  private readonly api: EngineAPI;

  public prompt: Prompt;
  public nodes: Map<NodeID, Node>;
  public models: ModelName[];

  constructor(api: EngineAPI, model: ModelName) {
    this.api = api;

    this.models = [model];
    this.prompt = new Prompt({model: model});
    this.nodes = new Map<NodeID, Node>();
    console.log("Temp Models: " + this.models);
  }

  async initialize(): Promise<void> {
    this.models = await this.api.getModels();
    console.log("Models: " + this.models);

    this.nodes = new Map<NodeID, Node>();

    const NodeIDs = await this.api.getNodeIDs();
    if (NodeIDs.length === 0) {
      console.log("NodeIDs: []")
    } else {
      console.log("NodeIDs: " + NodeIDs);
    }
    for (const NodeID of NodeIDs) {
      const node = await this.api.getNode(NodeID);

      this.nodes.set(NodeID, node);
      console.log("  Node: " + node.id);
    }
  }
}
