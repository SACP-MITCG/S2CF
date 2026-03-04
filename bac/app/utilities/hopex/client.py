"""
BAC - HOPEX GraphQL Client
Adapted from SAC hopex_client.py

Provides access to HOPEX architecture models for BAM references.
"""
import os
import requests
from typing import Optional


class HopexClient:
    """Client for interacting with HOPEX GraphQL API."""

    def __init__(self):
        self.api_url = os.getenv("HOPEX_API_URL")
        self.api_key = os.getenv("HOPEX_API_KEY")

        if not self.api_url or not self.api_key:
            raise ValueError("HOPEX_API_URL and HOPEX_API_KEY must be set")

    def _execute_query(self, query: str, variables: dict = None) -> dict:
        """Execute a GraphQL query against HOPEX."""
        headers = {
            "Content-Type": "application/json",
            "x-api-key": self.api_key,
        }

        payload = {"query": query}
        if variables:
            payload["variables"] = variables

        response = requests.post(
            self.api_url,
            json=payload,
            headers=headers,
            timeout=30
        )
        response.raise_for_status()

        result = response.json()
        if "errors" in result:
            raise Exception(f"GraphQL errors: {result['errors']}")

        return result.get("data", {})

    def get_capabilities(self, limit: int = 100) -> list[dict]:
        """Get business capabilities from HOPEX."""
        query = """
        query GetCapabilities($limit: Int) {
            businessCapabilities(first: $limit) {
                edges {
                    node {
                        id
                        name
                        description
                        level
                        parentCapability {
                            id
                            name
                        }
                    }
                }
            }
        }
        """

        try:
            data = self._execute_query(query, {"limit": limit})
            edges = data.get("businessCapabilities", {}).get("edges", [])
            return [
                {
                    "id": edge["node"]["id"],
                    "name": edge["node"]["name"],
                    "description": edge["node"].get("description", ""),
                    "level": edge["node"].get("level"),
                    "type": "BusinessCapability",
                    "parent": edge["node"].get("parentCapability"),
                }
                for edge in edges
            ]
        except Exception as e:
            # Return mock data if HOPEX is not available
            return self._mock_capabilities()

    def get_processes(self, limit: int = 100) -> list[dict]:
        """Get business processes from HOPEX."""
        query = """
        query GetProcesses($limit: Int) {
            businessProcesses(first: $limit) {
                edges {
                    node {
                        id
                        name
                        description
                        owner
                    }
                }
            }
        }
        """

        try:
            data = self._execute_query(query, {"limit": limit})
            edges = data.get("businessProcesses", {}).get("edges", [])
            return [
                {
                    "id": edge["node"]["id"],
                    "name": edge["node"]["name"],
                    "description": edge["node"].get("description", ""),
                    "owner": edge["node"].get("owner"),
                    "type": "BusinessProcess",
                }
                for edge in edges
            ]
        except Exception:
            return self._mock_processes()

    def get_applications(self, limit: int = 100) -> list[dict]:
        """Get applications from HOPEX."""
        query = """
        query GetApplications($limit: Int) {
            applications(first: $limit) {
                edges {
                    node {
                        id
                        name
                        description
                        status
                        vendor
                    }
                }
            }
        }
        """

        try:
            data = self._execute_query(query, {"limit": limit})
            edges = data.get("applications", {}).get("edges", [])
            return [
                {
                    "id": edge["node"]["id"],
                    "name": edge["node"]["name"],
                    "description": edge["node"].get("description", ""),
                    "status": edge["node"].get("status"),
                    "vendor": edge["node"].get("vendor"),
                    "type": "Application",
                }
                for edge in edges
            ]
        except Exception:
            return self._mock_applications()

    def get_diagrams(self, element_id: str = None, diagram_type: str = None) -> list[dict]:
        """Get diagrams from HOPEX, optionally filtered by element or type."""
        # Simplified query - actual HOPEX schema may differ
        query = """
        query GetDiagrams {
            diagrams(first: 50) {
                edges {
                    node {
                        id
                        name
                        diagramType
                        lastModified
                    }
                }
            }
        }
        """

        try:
            data = self._execute_query(query)
            edges = data.get("diagrams", {}).get("edges", [])
            return [
                {
                    "id": edge["node"]["id"],
                    "name": edge["node"]["name"],
                    "type": edge["node"].get("diagramType", "Unknown"),
                    "lastModified": edge["node"].get("lastModified"),
                }
                for edge in edges
            ]
        except Exception:
            return self._mock_diagrams()

    def get_diagram_image(self, diagram_id: str) -> dict:
        """Get diagram image from HOPEX."""
        # This would typically call a HOPEX endpoint that returns diagram images
        # The actual implementation depends on HOPEX version and configuration

        # For now, return a placeholder
        return {
            "diagramId": diagram_id,
            "url": f"{self.api_url}/diagrams/{diagram_id}/image",
            "base64": None,  # Would contain actual image data
        }

    def get_element(self, element_id: str) -> dict:
        """Get details of a specific element."""
        query = """
        query GetElement($id: ID!) {
            node(id: $id) {
                id
                ... on BusinessCapability {
                    name
                    description
                    __typename
                }
                ... on BusinessProcess {
                    name
                    description
                    __typename
                }
                ... on Application {
                    name
                    description
                    __typename
                }
            }
        }
        """

        try:
            data = self._execute_query(query, {"id": element_id})
            node = data.get("node", {})
            return {
                "id": node.get("id"),
                "name": node.get("name"),
                "description": node.get("description"),
                "type": node.get("__typename"),
            }
        except Exception as e:
            return {"error": str(e)}

    def search(self, query: str, element_type: str = None) -> list[dict]:
        """Search HOPEX elements."""
        # Simplified search - actual implementation depends on HOPEX API
        results = []

        if not element_type or element_type == "BusinessCapability":
            caps = self.get_capabilities()
            results.extend([c for c in caps if query.lower() in c["name"].lower()])

        if not element_type or element_type == "BusinessProcess":
            procs = self.get_processes()
            results.extend([p for p in procs if query.lower() in p["name"].lower()])

        if not element_type or element_type == "Application":
            apps = self.get_applications()
            results.extend([a for a in apps if query.lower() in a["name"].lower()])

        return results[:20]  # Limit results

    # Mock data for development when HOPEX is not available
    def _mock_capabilities(self) -> list[dict]:
        return [
            {"id": "cap-1", "name": "Customer Management", "description": "Managing customer relationships", "type": "BusinessCapability", "level": 1},
            {"id": "cap-2", "name": "Order Processing", "description": "Processing customer orders", "type": "BusinessCapability", "level": 1},
            {"id": "cap-3", "name": "Inventory Management", "description": "Managing product inventory", "type": "BusinessCapability", "level": 1},
            {"id": "cap-4", "name": "Carbon Footprint Tracking", "description": "Tracking and reporting carbon emissions", "type": "BusinessCapability", "level": 2},
            {"id": "cap-5", "name": "Sustainability Reporting", "description": "ESG and sustainability compliance reporting", "type": "BusinessCapability", "level": 2},
        ]

    def _mock_processes(self) -> list[dict]:
        return [
            {"id": "proc-1", "name": "Order-to-Cash", "description": "End-to-end order fulfillment process", "type": "BusinessProcess"},
            {"id": "proc-2", "name": "Procure-to-Pay", "description": "Procurement and payment process", "type": "BusinessProcess"},
            {"id": "proc-3", "name": "Carbon Data Collection", "description": "Collecting carbon footprint data from suppliers", "type": "BusinessProcess"},
        ]

    def _mock_applications(self) -> list[dict]:
        return [
            {"id": "app-1", "name": "SAP S/4HANA", "description": "ERP System", "type": "Application", "vendor": "SAP"},
            {"id": "app-2", "name": "Salesforce CRM", "description": "Customer Relationship Management", "type": "Application", "vendor": "Salesforce"},
            {"id": "app-3", "name": "Carbon Dashboard", "description": "Sustainability analytics platform", "type": "Application", "vendor": "Internal"},
        ]

    def _mock_diagrams(self) -> list[dict]:
        return [
            {"id": "diag-1", "name": "Business Capability Map", "type": "Capability Map"},
            {"id": "diag-2", "name": "Order Process Flow", "type": "BPMN"},
            {"id": "diag-3", "name": "Application Landscape", "type": "Application Map"},
        ]
