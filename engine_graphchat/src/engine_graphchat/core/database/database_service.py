import psycopg

from engine_graphchat.core.database import tables


class DatabaseService:
    _database_name = "graphchat"
    _database_schema = "graphchat"

    def __init__(self):
        self._composite_types = {"node_usage": None}

        self._initialize_composite_types()

    def get_graph(self, graph_id=None):
        node_ids = self.get_node_ids(graph_id)
        return {node_id: self.get_NodeData(node_id) for node_id in node_ids}

    def get_node_ids(self, graph_id=None):
        with self.get_connection() as connection:
            with connection.cursor() as cursor:
                return tables.get_graph_node_ids(cursor, graph_id)

    def get_NodeData(self, node_id):
        with self.get_connection() as connection:
            self._register_composite_types(connection)
            with connection.cursor() as cursor:
                return tables.get_NodeData(cursor, node_id)

    def add_NodeData(self, nodeData):
        with self.get_connection() as connection:
            self._register_composite_types(connection)
            with connection.cursor() as cursor:
                tables.add_NodeData(cursor, nodeData)

    def get_connection(self):
        return psycopg.connect(f"dbname={self._database_name}", row_factory=psycopg.rows.dict_row)

    def _initialize_composite_types(self):
        with self.get_connection() as conn:
            for type_name in self._composite_types.keys():
                info = psycopg.types.composite.CompositeInfo.fetch(conn, f"{self._database_schema}.{type_name}")
                self._composite_types[type_name] = info

    def _register_composite_types(self, connection):
        def to_dict(values, info):
            return dict(zip(info.field_names, values))

        def from_dict(data, info):
            return [data[name] for name in info.field_names]

        for info in self._composite_types.values():
            psycopg.types.composite.register_composite(info, connection, make_object=to_dict, make_sequence=from_dict)
