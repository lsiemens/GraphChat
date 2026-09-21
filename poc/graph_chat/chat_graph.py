#!/usr/bin/env -S streamlit run

import graph
import streamlit as st

_MOCK = False

llm_graph = None
if "llm_graph" not in st.session_state:
    llm_graph = graph.Graph(mock=_MOCK)
    st.session_state.llm_graph = llm_graph
else:
    llm_graph = st.session_state.llm_graph

st.set_page_config(page_title="Graph Chat")

st.title("Graph Chat")

with st.sidebar:
    st.header("Chat Nodes:")
    st.button("Refresh", width="stretch")

    width = 1
    node_IDs = [0]
    node_grid = []
    while (len(node_IDs) > 0):
        node_grid += [node_IDs]
        next_node_IDs = []
        for node_ID in node_IDs:
            if node_ID in llm_graph.children:
                next_node_IDs += llm_graph.children[node_ID]
        if len(next_node_IDs) > width:
            width = len(next_node_IDs)
        node_IDs = next_node_IDs

    for row_id in range(len(node_grid)):
        columns = st.columns(width, gap="small")
        for column_id in range(width):
            with columns[column_id]:
                if (column_id < len(node_grid[row_id])):
                    node_ID = node_grid[row_id][column_id]

                    button_type = "secondary"
                    if llm_graph.current_ID == node_ID:
                        button_type = "primary"

                    if st.button(f"Node [{node_ID}]", type=button_type):
                        llm_graph.set_current_ID(node_ID)

st.write("This chat client is modeled on a directed acyclic graph. The LLM system is connected to xAI's Grok!")

# show thread history
if llm_graph.current_ID is not None:
    node_IDs = [llm_graph.current_ID]
    while (node_IDs[-1] in llm_graph.parents):
        node_IDs.append(llm_graph.parents[node_IDs[-1]][0])

    for node_ID in node_IDs[::-1]:
        user_txt, reply_txt = llm_graph.get_node_txt(node_ID)

        with st.chat_message("user"):
            st.markdown(user_txt)
        with st.chat_message("assistant"):
            st.markdown(reply_txt)

# get user input
if prompt := st.chat_input("Your question ..."):
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message_reply = st.empty()
        response = llm_graph.add_node(prompt)
        message_reply.markdown(response)
