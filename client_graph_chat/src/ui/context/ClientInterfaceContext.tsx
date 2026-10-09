import type { ModelName } from "@/types"
import type { EngineAPI } from "@/client-driver/api/EngineAPI"

import { useState, useEffect, createContext } from "react"
import { ClientInterface } from "@/client-driver/ClientInterface"

interface Props {
  children: React.ReactNode;
  api: EngineAPI;
  model: ModelName;
};

export const CIContext = createContext<ClientInterface | null>(null);

export function ClientInterfaceContext({ children, api, model }: Props) {
  const [clientInterface] = useState(() => new ClientInterface(api, model));

  useEffect(() => {
    clientInterface.initialize();
  }, [clientInterface]);

  return (
    <CIContext value={clientInterface}>
      {children}
    </CIContext>);
}
