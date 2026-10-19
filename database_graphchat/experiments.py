import datetime
import psycopg

node_usage_info = None
with psycopg.connect("dbname=graphchat") as conn:
    node_usage_info = psycopg.types.composite.CompositeInfo.fetch(conn, "graphchat.node_usage")


with psycopg.connect("dbname=graphchat", row_factory=psycopg.rows.dict_row) as conn:
    print(conn)

    psycopg.types.composite.register_composite(node_usage_info, conn)
    print(node_usage_info.python_type(1.5, 2, 3, 4, -0.034))

    with conn.cursor() as cur:
        cur.execute("SELECT graph_id FROM graphchat.graphs")
        graph_ids = [item["graph_id"] for item in cur.fetchall()]
        print(graph_ids)
        for graph_id in graph_ids:
            cur.execute("SELECT node_id FROM graphchat.graphs_nodes WHERE graph_id = %s", (graph_id,))
            node_ids = [item["node_id"] for item in cur.fetchall()]
            print(node_ids)
            for node_id in node_ids:
                cur.execute("SELECT * FROM graphchat.nodes WHERE node_id = %s", (node_id,))
                node = cur.fetchone()
                print(node)
                print(node["reply_timestamp"].astimezone(datetime.timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z"))
                
                cur.execute("SELECT * FROM graphchat.nodes_upstream WHERE node_id = %s ORDER BY upstream_order", (node_id,))
                upstream = [item["upstream_id"] for item in cur.fetchall()]
                print(upstream)
                
                cur.execute("SELECT * FROM graphchat.nodes_context WHERE node_id = %s ORDER BY context_order", (node_id,))
                context = [item["context_id"] for item in cur.fetchall()]
                print(context)
