import { SplitView } from "./components/layout/SplitView"
import { Chat } from "./components/chat/Chat"
import { Graph } from "./components/graph/Graph"
import "./ClientGraphChat.css"

function ClientGraphChat() {
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
