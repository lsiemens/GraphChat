import { SplitView } from "./components/layout/SplitView"
import { Chat } from "./components/chat/Chat"
import './App.css'

function App() {
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

export default App
