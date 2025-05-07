import os
import logging
from retry import retry
from neo4j import GraphDatabase

# Environment variables for CSV paths
CUSTOMERS_CSV_PATH = os.getenv("CUSTOMER_LIST_CSV_PATH")
TRANSACTIONS_CSV_PATH = os.getenv("TRANSACTIONS_CSV_PATH")
PRODUCTS_CSV_PATH = os.getenv("PRODUCTS_CSV_PATH")

NEO4J_URI = os.getenv("NEO4J_URL")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s]: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
LOGGER = logging.getLogger(__name__)


NODES = ["Customer", "Transaction", "Product"]


def _set_uniqueness_constraints(tx, node):
    """Create uniqueness constraints for nodes"""
    if node == "Customer":
        query = "CREATE CONSTRAINT IF NOT EXISTS FOR (n:Customer) REQUIRE n.customer_id IS UNIQUE"
    elif node == "Transaction":
        query = "CREATE CONSTRAINT IF NOT EXISTS FOR (n:Transaction) REQUIRE n.transaction_id IS UNIQUE"
    elif node == "Product":
        query = "CREATE CONSTRAINT IF NOT EXISTS FOR (n:Product) REQUIRE n.product_id IS UNIQUE"

    tx.run(query)


@retry(tries=100, delay=10)
def load_bicycle_store_graph_from_csv() -> None:
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))


    LOGGER.info("Setting uniqueness constraints on nodes")
    with driver.session(database="neo4j") as session:
        for node in NODES:
            session.execute_write(_set_uniqueness_constraints, node)


    LOGGER.info("Loading customer nodes")
    with driver.session(database="neo4j") as session:
        query = f"""
           LOAD CSV WITH HEADERS
           FROM '{CUSTOMERS_CSV_PATH}' AS row
           WITH row
           WHERE row.customerId IS NOT NULL AND row.firstName IS NOT NULL AND row.lastName IS NOT NULL AND row.gender IS NOT NULL
           AND row.past3YearsBikeRelatedPurchases IS NOT NULL AND row.DOB IS NOT NULL AND row.jobTitle IS NOT NULL
           AND row.Rank IS NOT NULL
           AND row.jobIndustryCategory IS NOT NULL
           MERGE (c:Customer {{
           customer_id: toInteger(row.customerId),
           first_name: row.firstName,
           last_name: row.lastName,
           gender: row.gender,
           past_3_years_bike_related_purchases: row.past3YearsBikeRelatedPurchases,
           DOB: row.DOB,
           job_title: row.jobTitle,
           job_industry_category: row.jobIndustryCategory,
           wealth_segment: row.wealthSegment,
           owns_car: row.ownsCar,
           tenure: row.tenure,
           address: row.address,
           postcode: row.postcode,
           state: row.state,
           country: row.country,
           property_valuation: row.propertyValuation,
           rank: row.Rank,
           value: row.Value       
                             
                              }});
           """
        _ = session.run(query, {})

    LOGGER.info("Loading product nodes ")
    with driver.session(database="neo4j") as session:
        query = f"""
            LOAD CSV WITH HEADERS
            FROM '{PRODUCTS_CSV_PATH}' as row
            MERGE (p:Product {{
               product_id: toInteger(row.productid),
               brand: row.brand,
               product_line: row.productLine,
               product_size: row.productSize,
               price: row.listPrice
           }})
         """
        _ = session.run(query, {})

    LOGGER.info("Loading transaction nodes with relationships")
    with driver.session(database="neo4j") as session:
        query = f"""
           LOAD CSV WITH HEADERS
           FROM '{TRANSACTIONS_CSV_PATH}' AS row
           MERGE (t:Transaction {{
               transaction_id: toInteger(row.transactionId),
               date: row.transactionDate,
               online_order: row.onlineOrder,
               status: row.orderStatus
           }})

        """
        session.run(query)

    LOGGER.info("Loading 'MADE' relationships")
    with driver.session(database="neo4j") as session:
        query = f"""
                LOAD CSV WITH HEADERS FROM '{TRANSACTIONS_CSV_PATH}' AS row
                MATCH (c:Customer {{customer_id: toInteger(row.customerId)}})
                MATCH (t:Transaction {{transaction_id: toInteger(row.transactionId)}})
                MERGE (c)-[:MADE]->(t)
               """
        _ = session.run(query, {})

    LOGGER.info("Loading 'CONTAINS' relationships")
    with driver.session(database="neo4j") as session:
        query = f"""
                  LOAD CSV WITH HEADERS FROM '{TRANSACTIONS_CSV_PATH}' AS row
                  MATCH (t:Transaction {{transaction_id: toInteger(row.transactionId)}})
                  MATCH (p:Product {{product_id: toInteger(row.productId)}})
                  MERGE (t)-[:CONTAINS]->(p)
                 """
        _ = session.run(query, {})


    LOGGER.info("Bicycle store data loading completed successfully")


if __name__ == "__main__":
    load_bicycle_store_graph_from_csv()