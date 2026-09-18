#!/usr/bin/env -S streamlit run

import graph
import streamlit as st

st.set_page_config(page_title="Linear Chat")
st.title("Linear Chat")

st.write("This is a test of a standard chat client connected to xAI's Grok!")

llm_graph = None
if "llm_graph" not in st.session_state:
    llm_graph = graph.Graph()
    st.session_state.llm_graph = llm_graph
else:
    llm_graph = st.session_state.llm_graph

st.caption("The connection to Grok has been initialized.")

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
