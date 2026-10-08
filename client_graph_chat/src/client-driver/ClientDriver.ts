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
  }

  async submitPrompt(): Promise<void> {
    const node = await this.api.sendPrompt(this.prompt);
    this.nodes.set(node.id, node);
    this.prompt = new Prompt({model: node.model, upstream:[node.id], context:[...node.context, node.id], content:""});
  }

  async computeView(viewName: viewName, upstream: NodeID[]): Promise<NodeID[]> {
    return await this.api.computeView(viewName, upstream);
  }
}
