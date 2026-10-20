import logging

from engine_graphchat.core import exceptions
from engine_graphchat.core.dag import node
from engine_graphchat.core.llm import utils as llm_utils


logger = logging.getLogger(__name__)
SCHEMA = "graphchat"


def get_graph_node_ids(cursor, graph_id):
    if graph_id is None:
        cursor.execute(f"SELECT node_id FROM {SCHEMA}.nodes")

        return [item["node_id"] for item in cursor.fetchall()]
    else:
        raise exceptions.NotFoundError("getting nodes by graph is not implemented yet")


def get_NodeData(cursor, node_id):
    pg_upstream = _select_nodes_upstream(cursor, node_id)
    pg_context = _select_nodes_context(cursor, node_id)
    pg_node_data = _select_nodes(cursor, node_id)

    pg_usage = pg_node_data["usage"]
    nodeUsage = node.NodeUsage(
        cached_prompt_text_tokens=int(pg_usage["cached_prompt_text_tokens"]),
        prompt_tokens=int(pg_usage["prompt_tokens"]),
        reasoning_tokens=int(pg_usage["reasoning_tokens"]),
        completion_tokens=int(pg_usage["completion_tokens"]),
        cost_USD=float(pg_usage["cost_usd"]))

    nodeReply = node.NodeReply(
        timestamp=pg_node_data["reply_timestamp"],
        content=pg_node_data["reply"],
        finish_reason=None,
        usage=nodeUsage)

    nodeRequest = node.NodeRequest(
        timestamp=pg_node_data["request_timestamp"],
        context=pg_context,
        content=pg_node_data["request"])

    nodeData = node.NodeData(
        id=pg_node_data["node_id"],
        model=pg_node_data["model"],
        upstream=pg_upstream,
        request=nodeRequest,
        reply=nodeReply)

    return nodeData


def add_NodeData(cursor, nodeData):
    usage = nodeData.reply.usage

    upstream = nodeData.upstream
    context = nodeData.request.context
    data = {
        "node_id": nodeData.id,
        "request_timestamp": nodeData.request.timestamp,
        "request": nodeData.request.content,
        "reply_timestamp": nodeData.reply.timestamp,
        "reply": nodeData.reply.content,
        "model": nodeData.model,
        "cached_prompt_text_tokens": usage.cached_prompt_text_tokens,
        "prompt_tokens": usage.prompt_tokens,
        "reasoning_tokens": usage.reasoning_tokens,
        "completion_tokens": usage.completion_tokens,
        "cost_usd": usage.cost_USD}

    _insert_nodes(cursor, data)
    _insert_nodes_upstream(cursor, nodeData.id, upstream)
    _insert_nodes_context(cursor, nodeData.id, context)


def _select_nodes(cursor, node_id):
    cursor.execute(f"""
        SELECT * FROM {SCHEMA}.nodes
            WHERE node_id = %s""", (node_id,))

    data = cursor.fetchone()
    data["request_timestamp"] = llm_utils.format_timestamp(data["request_timestamp"])
    data["reply_timestamp"] = llm_utils.format_timestamp(data["reply_timestamp"])
    return data


def _insert_nodes(cursor, data):
    cursor.execute(f"""
        INSERT INTO {SCHEMA}.nodes (node_id, request_timestamp, request, reply_timestamp, reply, model, usage)
            VALUES (
                %(node_id)s,
                %(request_timestamp)s,
                %(request)s,
                %(reply_timestamp)s,
                %(reply)s,
                %(model)s,
                ROW(
                    %(cached_prompt_text_tokens)s,
                    %(prompt_tokens)s,
                    %(reasoning_tokens)s,
                    %(completion_tokens)s,
                    %(cost_usd)s))""", data)


def _select_nodes_context(cursor, node_id):
    cursor.execute(f"""
        SELECT context_order, context_id FROM {SCHEMA}.nodes_context
            WHERE node_id = %s
            ORDER BY context_order""", (node_id,))

    return [item["context_id"] for item in cursor.fetchall()]


def _insert_nodes_context(cursor, node_id, context):
    data = [(node_id, index, context_id) for index, context_id in enumerate(context)]

    cursor.executemany(f"""
        INSERT INTO {SCHEMA}.nodes_context (node_id, context_order, context_id)
            VALUES (%s, %s, %s)""", data)


def _select_nodes_upstream(cursor, node_id):
    cursor.execute(f"""
        SELECT upstream_id FROM {SCHEMA}.nodes_upstream
            WHERE node_id = %s
            ORDER BY upstream_order""", (node_id,))

    return [item["upstream_id"] for item in cursor.fetchall()]


def _insert_nodes_upstream(cursor, node_id, upstream):
    data = [(node_id, index, upstream_id) for index, upstream_id in enumerate(upstream)]

    cursor.executemany(f"""
        INSERT INTO {SCHEMA}.nodes_upstream (node_id, upstream_order, upstream_id)
            VALUES (%s, %s, %s)""", data)
