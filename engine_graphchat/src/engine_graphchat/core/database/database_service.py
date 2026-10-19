import psycopg

from engine_graphchat.core.dag import node
from engine_graphchat.core.llm import utils as llm_utils


class DatabaseService:
    _database_name = "graphchat"
    _database_schema = "graphchat"

    def __init__(self):
        self._composite_types = {"node_usage": None}

        self._initialize_composite_types()

    def get_connection(self):
        return psycopg.connect(f"dbname={self._database_name}", row_factory=psycopg.rows.dict_row)

    def get_node_ids(self):
        with self.get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(f"SELECT node_id FROM {self._database_schema}.nodes")
                return [item["node_id"] for item in cursor.fetchall()]

    def get_NodeData(self, node_id):
        with self.get_connection() as connection:
            self._register_composite_types(connection)
            with connection.cursor() as cursor:
                pg_upstream = self._get_nodes_upstream(cursor, node_id)
                pg_context = self._get_nodes_context(cursor, node_id)
                pg_node_data = self._get_nodes(cursor, node_id)

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

    def _get_nodes(self, cursor, node_id):
        cursor.execute(f"""
            SELECT * FROM {self._database_schema}.nodes
                WHERE node_id = %s""", (node_id,))

        data = cursor.fetchone()
        data["request_timestamp"] = llm_utils.format_timestamp(data["request_timestamp"])
        data["reply_timestamp"] = llm_utils.format_timestamp(data["reply_timestamp"])
        return data

    def _get_nodes_context(self, cursor, node_id):
        cursor.execute(f"""
            SELECT context_order, context_id FROM {self._database_schema}.nodes_context
                WHERE node_id = %s
                ORDER BY context_order""", (node_id,))

        return [item["context_id"] for item in cursor.fetchall()]

    def _get_nodes_upstream(self, cursor, node_id):
        cursor.execute(f"""
            SELECT upstream_id FROM {self._database_schema}.nodes_upstream
                WHERE node_id = %s
                ORDER BY upstream_order""", (node_id,))

        return [item["upstream_id"] for item in cursor.fetchall()]

    def _initialize_composite_types(self):
        with self.get_connection() as conn:
            for type_name in self._composite_types.keys():
                info = psycopg.types.composite.CompositeInfo.fetch(conn, f"{self._database_schema}.{type_name}")
                self._composite_types[type_name] = info

    def _register_composite_types(self, connection):
        def to_dict(values, info):
            return dict(zip(info.field_names, values))

        for info in self._composite_types.values():
            psycopg.types.composite.register_composite(info, connection, make_object=to_dict)

A = DatabaseService()
ids = A.get_node_ids()
print(A.get_NodeData(ids[0]))
