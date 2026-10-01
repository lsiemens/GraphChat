import { Prompt, Node, type NodeID } from "@/types"

export interface EngineAPI {
  sendPrompt(prompt: Prompt): Promise<Node>;
  getNodeIDs(): Promise<NodeID[]>;
  getNode(nodeID: NodeID): Promise<Node>;
}
