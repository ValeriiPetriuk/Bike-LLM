import os
from models.bike_rag_query import UserModel
from neo4j import GraphDatabase, AsyncGraphDatabase

class DBUser:
    def __init__(self):
        self.driver = GraphDatabase.driver(
            uri=os.getenv('NEO4J_URL'),
            auth=(os.getenv('NEO4J_USERNAME'), os.getenv('NEO4J_PASSWORD')),
        )

    def close(self):
        self.driver.close()

    def get_user_by_username(self, username):
        with self.driver.session() as session:
            result = session.run(
                """
                    MATCH (u:User {username: $username})
                    RETURN u.username AS username, u.password AS password, id(u) AS id
                """,
                username=username,
            )
            record = result.single()
            if record:
                return UserModel(
                    username=record["username"],
                    password=record["password"]
                )
            return None


db_user = DBUser()