import { Prompt, Node, type NodeID, type ModelName, type ViewName, fromNodeID, fromViewName } from "@/types"
import type { EngineAPI } from "./EngineAPI"
import { apiToNode, apiFromPrompt, apiToNodeIDs, apiToModelNames, apiToViewNames, apiFromViewUpstream, apiToViewContext, apiToServerError } from "./APITypes"

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
    const JSON_body = JSON.stringify(promptAPI);

    return await sendPOST(URL, JSON_body, apiToNode);
  }

  async getNodeIDs(): Promise<NodeID[]> {
    const URL = `${this.API_URL}/graphs/0/nodes`;
    return await sendGET(URL, apiToNodeIDs);
  }

  async getNode(nodeID: NodeID): Promise<Node> {
    const URL = `${this.API_URL}/graphs/0/nodes/${fromNodeID(nodeID)}`;
    return await sendGET(URL, apiToNode);
  }

  async getViews(): Promise<ViewName[]> {
    const URL = `${this.API_URL}/graphs/0/views`;
    return await sendGET(URL, apiToViewNames);
  }

  async computeView(viewName: ViewName, upstream: readonly NodeID[]): Promise<NodeID[]> {
    const viewUpstreamAPI = apiFromViewUpstream(upstream);

    const URL = `${this.API_URL}/graphs/0/views/${fromViewName(viewName)}`;
    const JSON_body = JSON.stringify(viewUpstreamAPI);

    return await sendPOST(URL, JSON_body, apiToViewContext);
  }

  async getModels(): Promise<ModelName[]> {
    const URL = `${this.API_URL}/system/models`;
    return await sendGET(URL, apiToModelNames);
  }
}

/*  Manage HTTP Requests  */
async function sendGET<T>(URL: string, parser: (input: unknown) => T): Promise<T> {
  const request = {
    method: "GET",
  } satisfies RequestInit;

  return await sendHTTPRequest(URL, request, parser);
}

async function sendPOST<T>(URL: string, JSON_body: string, parser: (input: unknown) => T): Promise<T> {
  const request = {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON_body,
  } satisfies RequestInit;

  return sendHTTPRequest(URL, request, parser);
}

async function sendHTTPRequest<T>(URL: string, request: RequestInit, parser: (input: unknown) => T): Promise<T> {
  const reply = await fetch(URL, request);

  if (!reply.ok) {
    let serverError;
    try {
      const raw_error: unknown = await reply.json();
      serverError = apiToServerError(raw_error);
    } catch (err) {
      console.warn("Failed to parse the error message from the GraphChat engine");
      throw new Error(`HTTP request sent to GraphChat failed. ${reply.status}: ${reply.statusText}`);
    }

    throw serverError;
  }


  try {
    const raw: unknown = await reply.json();
    return parser(raw);
  } catch (err) {
    throw new Error("Failed to parse the HTTP reply from the GraphChat engine", {cause: err});
  }
}
