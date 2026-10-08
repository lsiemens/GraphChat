import { Prompt, Node, type NodeID, type ModelName, type ViewName } from "@/types"
import type { EngineAPI } from "./api/EngineAPI"

export class ClientDriver {
  private readonly api: EngineAPI;

  public prompt: Prompt;
  public nodes: Map<NodeID, Node>;
  public models: ModelName[];
  public views: ViewName[];

  constructor(api: EngineAPI, model: ModelName) {
    this.api = api;

    this.models = [model];
    this.views = [];
    this.prompt = new Prompt({model: model, upstream:[], context:[], content:""});
    this.nodes = new Map<NodeID, Node>();
  }

  async initialize(): Promise<void> {
    this.models = await this.api.getModels();
    this.views = await this.api.getViews();

    if (this.models.length === 0) {
      throw new Error("Failed to initialize ClientDriver: The models list is empty.")
    }

    if (this.views.length === 0) {
      throw new Error("Failed to initialize ClientDriver: The views list is empty.")
    }

    this.nodes = new Map<NodeID, Node>();
    const nodeIDs = await this.api.getNodeIDs();
    for (const nodeID of nodeIDs) {
      const node = await this.api.getNode(nodeID);

      this.nodes.set(nodeID, node);
    }

    /*
    console.log("------ClientDriver Initialized---------");

    console.log("Models: " + this.models);
    console.log("Views: " + this.views);
    if (nodeIDs.length === 0) {
      console.log("NodeIDs: []")
    } else {
      console.log("NodeIDs: " + nodeIDs);
    }
    for (const nodeID of nodeIDs) {
      console.log("  Node: " + this.nodes.get(nodeID)!);
    }

    const prompt = new Prompt({model:this.models[0]!, upstream:[], context:[], content:"This is a prompt"});
    console.log(prompt);
    const node = await this.api.sendPrompt(prompt);
    const contexts = await this.api.computeView(this.views[0]!, [node.id]);
    console.log(node);
    */
  }
}
