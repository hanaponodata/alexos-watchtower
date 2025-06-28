"""
compliance/graphql.py
Enterprise-grade GraphQL adapter for Watchtower compliance and reporting.
Enables data export and querying via standards-based GraphQL APIs.
"""

from typing import Dict, Any, Optional
import logging

class GraphQLAdapter:
    def __init__(self, endpoint: str, api_key: Optional[str] = None):
        self.endpoint = endpoint
        self.api_key = api_key
        self.logger = logging.getLogger("watchtower.compliance.graphql")

    def query(self, gql_query: str, variables: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        import requests
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        payload = {
            "query": gql_query,
            "variables": variables or {}
        }
        try:
            resp = requests.post(self.endpoint, json=payload, headers=headers, timeout=10)
            resp.raise_for_status()
            self.logger.info(f"GraphQL query sent: {gql_query}")
            return resp.json()
        except Exception as e:
            self.logger.error(f"GraphQL query failed: {e}")
            return {"error": str(e)}

if __name__ == "__main__":
    adapter = GraphQLAdapter(endpoint="http://localhost:8000/graphql")
    query = """
    query {
      health {
        status
      }
    }
    """
    print(adapter.query(query))
