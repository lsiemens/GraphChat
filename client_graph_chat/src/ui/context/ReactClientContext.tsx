import type { ModelName } from "@/types"
import type { EngineAPI } from "@/client-driver/api/EngineAPI"

import { useState, useEffect, createContext } from "react"
import { ReactClient } from "@/client-driver/ReactClient"

interface Props {
  children: React.ReactNode;
  api: EngineAPI;
  model: ModelName;
};

export const RCContext = createContext<ReactClient | null>(null);

export function ReactClientContext({ children, api, model }: Props) {
  const [reactClient] = useState(() => new ReactClient(api, model));

  useEffect(() => {
    reactClient.initialize();
  }, [reactClient]);

  return (
    <RCContext value={reactClient}>
      {children}
    </RCContext>);
}
