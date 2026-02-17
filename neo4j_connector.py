"""
Neo4j Connection Manager for MedAssist Healthcare Insurance KG
Handles connection pooling, query execution, and error handling
"""
from neo4j import GraphDatabase
from neo4j.exceptions import ServiceUnavailable, AuthError
import time
from typing import List, Dict, Any, Optional
from config import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD, NEO4J_DATABASE, MAX_RETRIES
from colorama import Fore, Style, init

init(autoreset=True)


class Neo4jConnector:
    """Neo4j database connector with retry logic and error handling"""
    
    def __init__(self, uri: str = NEO4J_URI, username: str = NEO4J_USERNAME, 
                 password: str = NEO4J_PASSWORD, database: str = NEO4J_DATABASE):
        self.uri = uri
        self.username = username
        self.password = password
        self.database = database
        self.driver = None
        
    def connect(self, max_retries: int = MAX_RETRIES, wait_time: int = 60):
        """Establish connection to Neo4j with retry logic"""
        print(f"{Fore.YELLOW}Connecting to Neo4j Aura at {self.uri}...")
        print(f"{Fore.YELLOW}⏳ Waiting {wait_time} seconds for Aura instance to be ready...")
        time.sleep(wait_time)
        
        for attempt in range(max_retries):
            try:
                self.driver = GraphDatabase.driver(
                    self.uri,
                    auth=(self.username, self.password),
                    database=self.database
                )
                # Test the connection
                self.driver.verify_connectivity()
                print(f"{Fore.GREEN}✓ Successfully connected to Neo4j!")
                return True
            except AuthError as e:
                print(f"{Fore.RED}✗ Authentication failed: {e}")
                return False
            except ServiceUnavailable as e:
                if attempt < max_retries - 1:
                    print(f"{Fore.YELLOW}⚠ Connection attempt {attempt + 1} failed. Retrying in 10 seconds...")
                    time.sleep(10)
                else:
                    print(f"{Fore.RED}✗ Failed to connect after {max_retries} attempts: {e}")
                    return False
            except Exception as e:
                print(f"{Fore.RED}✗ Unexpected error: {e}")
                return False
        
        return False
    
    def close(self):
        """Close the Neo4j driver connection"""
        if self.driver:
            self.driver.close()
            print(f"{Fore.BLUE}Connection closed.")
    
    def execute_query(self, query: str, parameters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Execute a Cypher query and return results"""
        if not self.driver:
            raise ConnectionError("Not connected to Neo4j. Call connect() first.")
        
        try:
            with self.driver.session(database=self.database) as session:
                result = session.run(query, parameters or {})
                return [record.data() for record in result]
        except Exception as e:
            print(f"{Fore.RED}✗ Query execution failed: {e}")
            print(f"{Fore.YELLOW}Query: {query}")
            print(f"{Fore.YELLOW}Parameters: {parameters}")
            raise
    
    def execute_write(self, query: str, parameters: Optional[Dict[str, Any]] = None) -> Any:
        """Execute a write transaction"""
        if not self.driver:
            raise ConnectionError("Not connected to Neo4j. Call connect() first.")
        
        def _write_tx(tx, query, params):
            result = tx.run(query, params)
            return result.single()
        
        try:
            with self.driver.session(database=self.database) as session:
                result = session.execute_write(_write_tx, query, parameters or {})
                return result
        except Exception as e:
            print(f"{Fore.RED}✗ Write transaction failed: {e}")
            print(f"{Fore.YELLOW}Query: {query}")
            raise
    
    def execute_batch(self, queries: List[str]) -> int:
        """Execute multiple queries in a single transaction"""
        if not self.driver:
            raise ConnectionError("Not connected to Neo4j. Call connect() first.")
        
        success_count = 0
        with self.driver.session(database=self.database) as session:
            with session.begin_transaction() as tx:
                for query in queries:
                    try:
                        tx.run(query)
                        success_count += 1
                    except Exception as e:
                        print(f"{Fore.RED}✗ Batch query failed: {e}")
                        print(f"{Fore.YELLOW}Query: {query}")
                tx.commit()
        
        return success_count
    
    def clear_database(self):
        """Clear all nodes and relationships (USE WITH CAUTION!)"""
        print(f"{Fore.YELLOW}⚠ Clearing database...")
        query = "MATCH (n) DETACH DELETE n"
        self.execute_query(query)
        print(f"{Fore.GREEN}✓ Database cleared.")
    
    def get_node_count(self) -> Dict[str, int]:
        """Get count of nodes by label"""
        query = """
        CALL db.labels() YIELD label
        CALL apoc.cypher.run('MATCH (n:`' + label + '`) RETURN count(n) as count', {})
        YIELD value
        RETURN label, value.count as count
        """
        try:
            results = self.execute_query(query)
            return {r['label']: r['count'] for r in results}
        except:
            # Fallback if APOC is not available
            labels = ['Customer', 'Policy', 'Hospital', 'Treatment', 'Medication', 'Claim']
            counts = {}
            for label in labels:
                query = f"MATCH (n:{label}) RETURN count(n) as count"
                result = self.execute_query(query)
                counts[label] = result[0]['count'] if result else 0
            return counts
    
    def get_relationship_count(self) -> int:
        """Get total count of relationships"""
        query = "MATCH ()-[r]->() RETURN count(r) as count"
        result = self.execute_query(query)
        return result[0]['count'] if result else 0
    
    def verify_schema(self) -> Dict[str, Any]:
        """Verify database schema (constraints and indexes)"""
        constraints_query = "SHOW CONSTRAINTS"
        indexes_query = "SHOW INDEXES"
        
        try:
            constraints = self.execute_query(constraints_query)
            indexes = self.execute_query(indexes_query)
            return {
                "constraints": len(constraints),
                "indexes": len(indexes),
                "constraint_details": constraints,
                "index_details": indexes
            }
        except Exception as e:
            print(f"{Fore.YELLOW}⚠ Could not verify schema: {e}")
            return {"constraints": 0, "indexes": 0}


# Singleton instance
_connector_instance = None

def get_connector() -> Neo4jConnector:
    """Get or create the Neo4j connector singleton"""
    global _connector_instance
    if _connector_instance is None:
        _connector_instance = Neo4jConnector()
    return _connector_instance


if __name__ == "__main__":
    # Test connection
    connector = Neo4jConnector()
    if connector.connect():
        print(f"\n{Fore.CYAN}=== Database Info ===")
        node_counts = connector.get_node_count()
        rel_count = connector.get_relationship_count()
        
        print(f"Node counts: {node_counts}")
        print(f"Relationship count: {rel_count}")
        
        schema_info = connector.verify_schema()
        print(f"Constraints: {schema_info['constraints']}")
        print(f"Indexes: {schema_info['indexes']}")
        
        connector.close()
