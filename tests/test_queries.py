"""
Unit tests for Cypher query generation.
Tests the QueryBuilder class from queries.py.
"""

import pytest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from queries import QueryBuilder


@pytest.mark.unit
class TestQueryBuilder:
    """Test suite for QueryBuilder class."""
    
    def test_get_customer_policy(self):
        """Test customer policy query generation."""
        query = QueryBuilder.get_customer_policy("CUST001")
        
        assert "MATCH" in query
        assert "Customer" in query
        assert "Policy" in query
        assert "HAS_POLICY" in query
        
    def test_check_coverage_query(self):
        """Test coverage check query generation."""
        query = QueryBuilder.check_coverage("CUST001", "TREAT001", "HOSP001")
        
        assert "MATCH" in query
        assert "COVERS" in query
        assert "Treatment" in query
        assert "Hospital" in query
        
    def test_find_network_hospitals_basic(self):
        """Test network hospital finder."""
        query = QueryBuilder.find_network_hospitals("CUST001")
        
        assert "MATCH" in query
        assert "Hospital" in query
        assert "IN_NETWORK" in query
        
    def test_find_network_hospitals_with_city(self):
        """Test network hospital finder with city filter."""
        query = QueryBuilder.find_network_hospitals("CUST001", "Bangalore")
        
        assert "MATCH" in query
        assert "Hospital" in query
        assert "city" in query.lower()
        
    def test_get_claim_history(self):
        """Test claim history query."""
        query = QueryBuilder.get_claim_history("CUST001", limit=5)
        
        assert "MATCH" in query
        assert "Claim" in query
        assert "LIMIT" in query
        
    def test_check_medication_coverage(self):
        """Test medication coverage query."""
        query = QueryBuilder.check_medication_coverage("CUST001", "Metformin")
        
        assert "MATCH" in query
        assert "Medication" in query
        assert "FORMULARY" in query or "IN_FORMULARY" in query
        
    def test_get_policy_utilization(self):
        """Test policy utilization query."""
        query = QueryBuilder.get_policy_utilization("CUST001")
        
        assert "MATCH" in query
        assert "Policy" in query
        assert "is_active" in query
        
    def test_query_uses_parameters(self):
        """Test that queries use parameterized queries."""
        query = QueryBuilder.get_customer_policy("CUST001")
        
        # Should use $customer_id instead of hardcoded value
        assert "$customer_id" in query
        assert "CUST001" not in query


@pytest.mark.unit
class TestQuerySafety:
    """Test security aspects of query generation."""
    
    def test_no_sql_injection_in_customer_id(self):
        """Test that queries prevent injection via customer ID."""
        malicious_id = "CUST001'; DROP DATABASE neo4j; //]"
        query = QueryBuilder.get_customer_policy(malicious_id)
        
        # Should still use parameterization
        assert "$customer_id" in query
        # Should not contain the injection attempt directly
        assert "DROP" not in query
        
    def test_parameterization_prevents_injection(self):
        """Test that all queries use parameterization."""
        test_queries = [
            QueryBuilder.get_customer_policy("TEST"),
            QueryBuilder.find_network_hospitals("TEST", "Mumbai"),
            QueryBuilder.check_medication_coverage("TEST", "Drug"),
        ]
        
        for query in test_queries:
            # All queries should use $ parameters
            assert "$" in query


@pytest.mark.unit
def test_query_performance():
    """Test that query generation is fast."""
    import time
    
    start = time.time()
    for _ in range(100):
        QueryBuilder.get_customer_policy("CUST001")
        QueryBuilder.find_network_hospitals("CUST001")
    elapsed = time.time() - start
    
    # Should generate 200 queries in under 1 second
    assert elapsed < 1.0, f"Query generation too slow: {elapsed}s"


@pytest.mark.unit
def test_query_builder_static_methods():
    """Test that QueryBuilder methods are static."""
    # Should not need to instantiate QueryBuilder
    query = QueryBuilder.get_customer_policy("CUST001")
    assert query is not None
    assert isinstance(query, str)

