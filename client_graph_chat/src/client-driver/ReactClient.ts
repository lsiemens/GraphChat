import { Prompt, Node, type NodeID, type ModelName, type ViewName } from "@/types"
import { ClientDriver } from "./ClientDriver"
import type { EngineAPI } from "./api/EngineAPI"

type VoidFunc = () => void;
type Listener = VoidFunc;

export interface ClientState {
  readonly models: readonly ModelName[],
  readonly views: readonly ViewName[],
  readonly prompt: Prompt,
  readonly nodeIDs: ReadonlySet<NodeID>,
}

export class ReactClient {
  private clientDriver: ClientDriver;

  /* useSyncExternalStore ClientState */
  private clientStateSnapshot: ClientState | null = null;
  private clientStateListeners = new Set<Listener>();

  constructor(api: EngineAPI, model: ModelName) {
    this.clientDriver = new ClientDriver(api, model);
  }

  public updatePromptContent(content: string) {
    const prompt = this.getClientStateSnapshot().prompt;
    const newPrompt = new Prompt({
      model: prompt.model,
      upstream: prompt.upstream,
      context: prompt.context,
      content: content,
    });
    this.updatePrompt(newPrompt);
  }

  async updatePromptUpstream(upstream: NodeID[]) {
    const clientState = this.getClientStateSnapshot();
    const prompt = clientState.prompt;

    const viewName = clientState.views.at(0);
    if (viewName === undefined) {
      throw new Error("Views is empty");
    }

    const context = await this.clientDriver.computeView(viewName, upstream);

    const newPrompt = new Prompt({
      model: prompt.model,
      upstream: upstream,
      context: context,
      content: prompt.content,
    });
    this.updatePrompt(newPrompt);
  }

  public updatePrompt(prompt: Prompt) {
    this.clientDriver.prompt = prompt;
    this.invalidateClientState();
  }

  async submitPrompt(): Promise<void> {
    await this.clientDriver.submitPrompt();
    this.invalidateClientState();
  }

  async initialize(): Promise<void> {
    await this.clientDriver.initialize();
    this.invalidateClientState();
  }

  public getNodeByID(nodeID: NodeID): Node {
    const node = this.clientDriver.nodes.get(nodeID);

    if (!node) {
      throw new Error(`Node ${nodeID} does not exist in clientDriver`);
    }

    return node;
  }

  public invalidateClientState() {
    this.clientStateSnapshot = null;
    this.notifyClientState();
  }

  /* useSyncExternalStore ClientState */
  clientStateSubscribe = (listener: Listener): VoidFunc => {
    this.clientStateListeners.add(listener);
    const clientStateUnsubscribe = () => {
      this.clientStateListeners.delete(listener);
    };
    return clientStateUnsubscribe;
  };

  getClientStateSnapshot = (): ClientState => {
    if (this.clientStateSnapshot === null) {
      this.clientStateSnapshot = {
        models: this.clientDriver.models,
        views: this.clientDriver.views,
        prompt: this.clientDriver.prompt,
        nodeIDs: new Set(this.clientDriver.nodes.keys()),
      };
    }

    return this.clientStateSnapshot;
  };

  private notifyClientState(): void {
    for (const listener of this.clientStateListeners) {
      listener();
    }
  }
}
