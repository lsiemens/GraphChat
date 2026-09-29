import { SplitView } from "./components/layout/SplitView"
import { Chat } from "./components/chat/Chat"
import './ClientGraphChat.css'

function ClientGraphChat() {
  return (
    <>
      <h1>Test</h1>
      <section id="hbreak"></section>

      <SplitView
        left={<div>Node</div>}
        right={<Chat />}
      />

      <section id="hbreak"></section>
      Footer
    </>
  )
}

export default ClientGraphChat
