import { useContext, useSyncExternalStore } from "react"
import { ReactClient, type ClientState } from "@/client-driver/ReactClient"
import { RCContext } from "@/ui/context/ReactClientContext"

function useRCContext(): ReactClient {
  const reactClient = useContext(RCContext);
  if (!reactClient) {
    throw new Error("ReactClient does not exist: useRCContext under ReactClientContext.");
  }
  return reactClient;
}

export function useClientState(): [ClientState, ReactClient] {
  const reactClient = useRCContext();
  const clientState = useSyncExternalStore(reactClient.clientStateSubscribe, reactClient.getClientStateSnapshot);
  return [clientState, reactClient];
}
