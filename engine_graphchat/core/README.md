# Core
Manage the core logic of GraphChat and interactions with xAI. The direct
communication with xAI will be done through the python xAI SDK. The modules are:

- `llm`: A wrapper for interacting with xAI.
- `graph`: Types and structure of a directed acyclic graph (DAG).
- `dialogue`: A module constructing a conversation with an LLM encoded as a DAG.
