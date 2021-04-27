from neo4j import GraphDatabase

class DBExecution:

    def __init__(self):
        self.uri = "bolt://localhost:7687"
        self.driver = None
        self.query = []
        self.dataset_name = dataset_name

    def init_driver(self):
        self.driver = GraphDatabase.driver(self.uri, auth=("neo4j", "root"))

    def read_file(self, file_name):
        file = open(file_name, "r")
        self.query = file.read().splitlines()

    def close_driver(self) :
        self.driver.close()

    def execute(self, message):
        for i in range(len(self.query)):
            self.init_driver()
            with self.driver.session() as session :
                results = session.write_transaction(self._create_and_return, message, self.query[i])
                print(results)
                self.close_driver()

    @staticmethod
    def _create_and_return(tx, message, query) :
        tx.run(query, message=message)
        return "SUCCESS"

if __name__=="__main__":
    dataset_name = "mimic_2"
    e = DBExecution()
    e.read_file("neo4j_query/neo4j_insert_queries_"+dataset_name+".txt")
    e.execute("SUCCESS")
    # e.close()