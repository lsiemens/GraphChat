import { useContext, useSyncExternalStore } from "react"
import { ClientInterface, type ClientState } from "@/client-driver/ClientInterface"
import { CIContext } from "@/ui/context/ClientInterfaceContext"

function useCIContext(): ClientInterface {
  const clientInterface = useContext(CIContext);
  if (!clientInterface) {
    throw new Error("ClientInterface does not exist, ClientInterfaceContext may be missing.");
  }
  return clientInterface;
}

interface Client {
    state: ClientState,
    client: ClientInterface,
};

export function useClient(): Client {
  const clientInterface = useCIContext();
  const clientState = useSyncExternalStore(clientInterface.clientStateSubscribe, clientInterface.getClientStateSnapshot);
  return { state: clientState, client: clientInterface };
}
