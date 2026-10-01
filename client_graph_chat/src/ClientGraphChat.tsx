import { SplitView } from "./ui/components/layout/SplitView"
import { Chat } from "./ui/components/chat/Chat"
import { Graph } from "./ui/components/graph/Graph"
import { HTTPEngineAPI } from "./client-driver/api/HTTPEngineAPI"
import { useClientDriver } from "./ui/hooks/useClientDriver"
import "./ClientGraphChat.css"

function ClientGraphChat() {
  const api = new HTTPEngineAPI({host:"http://localhost", port:"8000", apiBase:"/api/v1"});
  const driver = useClientDriver(api);
  console.log("useDriver.model: " + driver.prompt.model);

  return (
    <>
      <h1>GraphChat</h1>
      <section id="hbreak"></section>

      <SplitView
        left={<Graph />}
        right={<Chat />}
      />

      <section id="hbreak"></section>
      Footer
    </>
  )
}

export default ClientGraphChat
