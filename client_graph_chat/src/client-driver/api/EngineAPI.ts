import { Prompt, Node, type NodeID, type ModelName } from "@/types"

export interface EngineAPI {
  sendPrompt(prompt: Prompt): Promise<Node>;
  getNodeIDs(): Promise<NodeID[]>;
  getNode(nodeID: NodeID): Promise<Node>;

  getViews(): Promise<ViewName[]>;
  computeView(viewName: ViewName, upstream: NodeID[]): Promise<NodeID[]>;

  getModels(): Promise<ModelName[]>;
}
