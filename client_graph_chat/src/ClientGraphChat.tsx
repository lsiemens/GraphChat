import { HTTPEngineAPI } from "./client-driver/api/HTTPEngineAPI"
import { ClientInterfaceContext } from "./ui/context/ClientInterfaceContext"

import { SplitView } from "./ui/components/layout/SplitView"
import { Chat } from "./ui/components/chat/Chat"
import { Graph } from "./ui/components/graph/Graph"
import "./ClientGraphChat.css"

function ClientGraphChat() {
  const api = new HTTPEngineAPI({host:"http://localhost", port:"8000", apiBase:"/api/v1"});

  return (
    <ClientInterfaceContext api={api}>
      <h1>GraphChat</h1>
      <section id="hbreak"></section>

      <SplitView
        left={<Graph />}
        right={<Chat />}
      />

      <section id="hbreak"></section>
      Footer
    </ClientInterfaceContext>
  )
}

export default ClientGraphChat
