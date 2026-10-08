import { toModelName } from "./types"
import { HTTPEngineAPI } from "./client-driver/api/HTTPEngineAPI"
import { ReactClientContext } from "./ui/context/ReactClientContext"

import { SplitView } from "./ui/components/layout/SplitView"
import { Chat } from "./ui/components/chat/Chat"
import { Graph } from "./ui/components/graph/Graph"
import "./ClientGraphChat.css"

function ClientGraphChat() {
  const model = toModelName("Grok-4.20");
  const api = new HTTPEngineAPI({host:"http://localhost", port:"8000", apiBase:"/api/v1"});

  return (
    <ReactClientContext api={api} model={model}>
      <h1>GraphChat</h1>
      <section id="hbreak"></section>

      <SplitView
        left={<Graph />}
        right={<Chat />}
      />

      <section id="hbreak"></section>
      Footer
    </ReactClientContext>
  )
}

export default ClientGraphChat
