import { SplitView } from "./components/layout/SplitView"
import './App.css'

function App() {
  return (
    <>
      <h1>Test</h1>
      <section id="hbreak"></section>

      <SplitView left={<div>Node</div>} right={<div>Chat</div>} /> 

      <section id="hbreak"></section>
      Footer
    </>
  )
}

export default App
