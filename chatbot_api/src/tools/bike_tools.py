from langchain_community.graphs import Neo4jGraph
import os
import numpy as np
from typing import Any

class BikeTool:
    def __init__(self):
        self.graph = Neo4jGraph(
            url=os.environ.get("NEO4J_URL"),
            username=os.environ.get("NEO4J_USERNAME"),
            password=os.environ.get("NEO4J_PASSWORD")
        )

        self.available_brands = self._load_brands()

    def _load_brands(self):
        result = self.graph.query(
            """
            MATCH (p:Product)
            RETURN DISTINCT p.brand AS brand
            """
        )
        return [row["brand"].lower() for row in result if row["brand"]]

    def _calculate_service_cost(self, brand: str) -> int:
        premium_brand = {
            "trek bicycles": 1.3,
            "giant bicycles": 1.25,
            "norco bicycles": 1.1
        }

        if not brand or brand.lower() not in self.available_brands:
            return -1
        base_cost = 30
        if brand.lower() in premium_brand.keys():
            return int(base_cost * premium_brand.get(brand.lower()))

        return base_cost

    def get_service_cost(self, brand: str) -> str:
        cost = self._calculate_service_cost(brand)
        if cost == -1:
            return f"Brand '{brand}' does not exist."
        return f"Estimated service cost for '{brand}': {cost} $"

    def get_most_available_service(self, _: Any) -> dict[str, int]:
        brand_costs = {
            b: self._calculate_service_cost(b)
            for b in self.available_brands
        }
        min_cost = min(brand_costs.values())
        best_services = {
            brand: cost for brand, cost in brand_costs.items() if cost == min_cost
        }
        return best_services





