import { StrictMode } from "react"
import { createRoot } from "react-dom/client"
import "./index.css"
import ClientGraphChat from "./ClientGraphChat.tsx"

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <ClientGraphChat />
  </StrictMode>,
)
