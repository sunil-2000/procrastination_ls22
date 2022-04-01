import psycopg2
from sshtunnel import SSHTunnelForwarder
from private.private import private

class Client:
    def __init__(self, host, username, password):
        private = Private()
        self.server = SSHTunnelForwarder(
            (host, private.tunnel_port),
            ssh_username=username,
            ssh_password=password,
            remote_bind_address=(private.ip, private.port),
        )
        
        self.server.start()
        self.binded_port = self.server.local_bind_port
        print('server connected')
        self.conn = psycopg2.connect(
            user=private.psql_user, host=private.ip, port=self.binded_port, database=private.db
        )
        print("database connected")

    def close_connection(self):
        self.conn.close()
        print('db connection closed')
        self.server.stop()
        print('server connection closed')

    def query_to_csv(self, query, file_name):
        """
        executes sql query and returns panda dataframe of query result
        input: valid sql query as string
        """
        cur = self.conn.cursor()
        print("connection opened")

        outputquery = "COPY ({0}) TO STDOUT WITH CSV HEADER".format(query)
        print("executing copy")
        with open(file_name, "w") as f:
            cur.copy_expert(outputquery, f)
        print("connection closed")
        return f
    
    def query(self, query):
        """
        Executes query and returns as Python object
        """
        cur = self.conn.cursor()
        cur.execute(query)
        res = cur.fetchall()
        return res 