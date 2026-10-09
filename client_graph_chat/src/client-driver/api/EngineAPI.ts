import { Prompt, Node, type NodeID, type ModelName, type ViewName } from "@/types"

export interface EngineAPI {
  sendPrompt(prompt: Prompt): Promise<Node>;
  getNodeIDs(): Promise<NodeID[]>;
  getNode(nodeID: NodeID): Promise<Node>;

  getViews(): Promise<ViewName[]>;
  computeView(viewName: ViewName, upstream: readonly NodeID[]): Promise<NodeID[]>;

  getModels(): Promise<ModelName[]>;
}
