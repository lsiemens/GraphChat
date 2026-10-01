import { useState, useEffect } from "react"
import { ClientDriver } from "@/client-driver/ClientDriver"
import type { EngineAPI } from "@/client-driver/api/EngineAPI"

export function useClientDriver(api: EngineAPI): ClientDriver {
  const [driver] = useState(() => new ClientDriver(api));

  useEffect(() => {
    void driver.initialize();
  }, [driver]);
  return driver;
}
