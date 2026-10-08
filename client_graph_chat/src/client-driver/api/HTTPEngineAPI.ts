import { Prompt, Node, type NodeID, type ModelName, fromNodeID, fromViewName } from "@/types"
import type { EngineAPI } from "./EngineAPI"
import { apiToNode, apiFromPrompt, apiToNodeIDs, apiToModelNames, apiToViewNames, apiFromViewUpstream, apiToViewContext } from "./APITypes"

interface HTTPEngineAPIArgs {
  host: string,
  port: string,
  apiBase: string,
}

export class HTTPEngineAPI implements EngineAPI {
  private readonly API_URL;

  constructor(args: HTTPEngineAPIArgs) {
    const portPattern = /^[1-9]\d{0,4}$/;
    if (!portPattern.test(args.port)) {
      throw new Error(`Invalid port \"${args.port}\", it must be a positive integer`);
    }
    if (Number(args.port) > 65535) {
      throw new Error(`Invalid port \"${args.port}\", the maximum port number is 65535`);
    }
    this.API_URL = `${args.host}:${args.port}${args.apiBase}`;
  }

  async sendPrompt(prompt: Prompt): Promise<Node> {
    const promptAPI = apiFromPrompt(prompt);

    const URL = `${this.API_URL}/graphs/0/nodes`;
    const request = {
      method: "POST",
      headers: { "Content-Type":"application/json" },
      body: JSON.stringify(promptAPI),
    };

    const reply = await fetch(URL, request);

    if (!reply.ok) {
      throw new Error(`Failed to send the prompt to the GraphChat engine: ${reply.status}`);
    }

    const raw: unknown = await reply.json();

    try {
      return apiToNode(raw);
    } catch (err) {
      throw new Error("Failed to parse the HTTP reply from the GraphChat engine", {cause: err});
    }
  }

  async getNodeIDs(): Promise<NodeID[]> {
    const URL = `${this.API_URL}/graphs/0/nodes`;
    const request = {
      method: "GET",
    };

    const reply = await fetch(URL, request);

    if (!reply.ok) {
      throw new Error(`Failed to get the list of node ids from the GraphChat engine: ${reply.status}`);
    }

    const raw: unknown = await reply.json();

    try {
      return apiToNodeIDs(raw);
    } catch (err) {
      throw new Error("Failed to parse the HTTP reply from the GraphChat engine", {cause: err});
    }
  }

  async getNode(nodeID: NodeID): Promise<Node> {
    const URL = `${this.API_URL}/graphs/0/nodes/${fromNodeID(nodeID)}`;
    const request = {
      method: "GET",
    };

    const reply = await fetch(URL, request);

    if (!reply.ok) {
      throw new Error(`Failed to get the Node from the GraphChat engine: ${reply.status}`);
    }

    const raw: unknown = await reply.json();

    try {
      return apiToNode(raw);
    } catch (err) {
      throw new Error("Failed to parse the HTTP reply from the GraphChat engine", {cause: err});
    }
  }

  async getViews(): Promise<ViewName[]> {
    const URL = `${this.API_URL}/graphs/0/views`;
    const request = {
      method: "GET",
    };

    const reply = await fetch(URL, request);

    if (!reply.ok) {
      throw new Error(`Failed to get the list of view names from the GraphChat engine: ${reply.status}`);
    }

    const raw: unknown = await reply.json();

    try {
      return apiToViewNames(raw);
    } catch (err) {
      throw new Error("Failed to parse the HTTP reply from the GraphChat engine", {cause: err});
    }
  }

  async computeView(viewName: ViewName, upstream: NodeID[]): Promise<NodeID[]> {
    const viewUpstreamAPI = apiFromViewUpstream(upstream);

    const URL = `${this.API_URL}/graphs/0/views/${fromViewName(viewName)}`;
    const request = {
      method: "POST",
      headers: { "Content-Type":"application/json" },
      body: JSON.stringify(viewUpstreamAPI),
    };

    const reply = await fetch(URL, request);

    if (!reply.ok) {
      throw new Error(`Failed to send the view upstream to the GraphChat engine: ${reply.status}`);
    }

    const raw: unknown = await reply.json();

    try {
      return apiToViewContext(raw);
    } catch (err) {
      throw new Error("Failed to parse the HTTP reply from the GraphChat engine", {cause: err});
    }
  }

  async getModels(): Promise<ModelName[]> {
    const URL = `${this.API_URL}/system/models`;
    const request = {
      method: "GET",
    };

    const reply = await fetch(URL, request);

    if (!reply.ok) {
      throw new Error(`Failed to get the list of model names from the GraphChat engine: ${reply.status}`);
    }

    const raw: unknown = await reply.json();

    try {
      return apiToModelNames(raw);
    } catch (err) {
      throw new Error("Failed to parse the HTTP reply from the GraphChat engine", {cause: err});
    }
  }
}
