import type { ModelName } from "@/types"
import type { EngineAPI } from "@/client-driver/api/EngineAPI"

import { useState, useEffect } from "react"
import { ClientDriver } from "@/client-driver/ClientDriver"

export function useClientDriver(api: EngineAPI, model: ModelName): ClientDriver {
  const [driver] = useState(() => new ClientDriver(api, model));

  useEffect(() => {
    void driver.initialize();
  }, [driver]);
  return driver;
}
