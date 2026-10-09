import { type Status, ClientError } from "@/types"
import { Prompt, Node, type NodeID, type ModelName, type ViewName } from "@/types"
import type { EngineAPI } from "./api/EngineAPI"

export class ClientDriver {
  private readonly api: EngineAPI;

  public prompt: Prompt;
  public nodes: Map<NodeID, Node>;
  public models: ModelName[];
  public views: ViewName[];
  public status: Status;

  constructor(api: EngineAPI) {
    this.api = api;

    this.models = [];
    this.views = [];
    this.prompt = new Prompt({model: null, upstream:[], context:[], content:""});
    this.nodes = new Map<NodeID, Node>();
    this.status = {
      message:"Uninitialized",
      details:"",
    };
  }

  async initialize(): Promise<void> {
    let failedInitialization = false;

    try {
      this.models = await this.api.getModels();
    } catch (error) {
      failedInitialization = true;
      console.error("Model initialization failed:", error);
      if (error instanceof ClientError) {
        this.status = error.status;
      } else if (error instanceof Error) {
        this.status = {
          message: "Model initialization failed",
          details: `Exception: ${error}`,
        };
      }
    } finally {
      if (this.models.length === 0) {
        failedInitialization = true;
        this.status = {
          message:"No models found",
          details:"",
        };
        console.error("Failed to initialize ClientDriver: The models list is empty.")
      }
    }


    try {
      this.views = await this.api.getViews();
    } catch (error) {
      failedInitialization = true;
      console.error("View initialization failed:", error);
      if (error instanceof ClientError) {
        this.status = error.status;
      } else if (error instanceof Error) {
        this.status = {
          message: "View initialization failed",
          details: `Exception: ${error}`,
        };
      }
    } finally {
      if (this.views.length === 0) {
        failedInitialization = true;
        this.status = {
          message:"No views found",
          details:"",
        };
        console.error("Failed to initialize ClientDriver: The views list is empty.")
      }
    }

    const model = this.models.at(0);
    if (model !== undefined) {
      this.prompt = new Prompt({model: model, upstream:[], context:[], content:""});
    } else {
      this.prompt = new Prompt({model: null, upstream:[], context:[], content:""});
    }

    this.nodes = new Map<NodeID, Node>();
    try {
      const nodeIDs = await this.api.getNodeIDs();
      for (const nodeID of nodeIDs) {
        const node = await this.api.getNode(nodeID);

        this.nodes.set(nodeID, node);
      }
    } catch (error) {
      failedInitialization = true;
      console.error("Graph initialization failed:", error);
      if (error instanceof ClientError) {
        this.status = error.status;
      } else if (error instanceof Error) {
        this.status = {
          message: "Failed to load graph",
          details: `Exception: ${error}`,
        };
      }
    }

    if (!failedInitialization) {
      this.clearStatus();
    }
  }

  async submitPrompt(): Promise<void> {
    try {
      const node = await this.api.sendPrompt(this.prompt);
      this.nodes.set(node.id, node);
      this.prompt = new Prompt({model: node.model, upstream:[node.id], context:[...node.context, node.id], content:""});
      this.clearStatus();
    } catch (error) {
      console.error("Failed to submit prompt:", error);
      if (error instanceof ClientError) {
        this.status = error.status;
      } else if (error instanceof Error) {
        this.status = {
          message: "Error: prompt",
          details: `Exception: ${error}`,
        };
      }
    }
  }

  async computeView(viewName: ViewName, upstream: readonly NodeID[]): Promise<NodeID[] | null> {
    try {
      const context = await this.api.computeView(viewName, upstream);
      this.clearStatus();
      return context;
    } catch (error) {
      console.error("Failed to compute view:", error);
      if (error instanceof ClientError) {
        this.status = error.status;
      } else if (error instanceof Error) {
        this.status = {
          message: "Error: view",
          details: `Exception: ${error}`,
        };
      }
    }
    return null;
  }

  private clearStatus() {
    this.status = {
      message:"",
      details:"",
    }
  }
}
