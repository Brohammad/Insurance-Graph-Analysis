"""
Test script for Flask Web API
"""
from web_api import app
import json

def test_api():
    """Test all API endpoints"""
    app.config['TESTING'] = True
    client = app.test_client()
    
    print("\n" + "="*70)
    print("Testing MedAssist Web API")
    print("="*70)
    
    passed = 0
    failed = 0
    
    # Test 1: Health Check
    print("\n1. GET /health")
    try:
        response = client.get('/health')
        if response.status_code == 200:
            data = response.json
            print(f"   ✓ PASSED - Status: {data['status']}, Nodes: {data['nodes']}")
            passed += 1
        else:
            print(f"   ✗ FAILED - Status code: {response.status_code}")
            failed += 1
    except Exception as e:
        print(f"   ✗ FAILED - Error: {e}")
        failed += 1
    
    # Test 2: Stats
    print("\n2. GET /api/stats")
    try:
        response = client.get('/api/stats')
        if response.status_code == 200:
            data = response.json
            print(f"   ✓ PASSED - Nodes: {data['total_nodes']}, Relationships: {data['total_relationships']}")
            passed += 1
        else:
            print(f"   ✗ FAILED - Status code: {response.status_code}")
            failed += 1
    except Exception as e:
        print(f"   ✗ FAILED - Error: {e}")
        failed += 1
    
    # Test 3: Customers List
    print("\n3. GET /api/customers")
    try:
        response = client.get('/api/customers')
        if response.status_code == 200:
            data = response.json
            print(f"   ✓ PASSED - Found {data['count']} customers")
            passed += 1
        else:
            print(f"   ✗ FAILED - Status code: {response.status_code}")
            failed += 1
    except Exception as e:
        print(f"   ✗ FAILED - Error: {e}")
        failed += 1
    
    # Test 4: Schema
    print("\n4. GET /api/schema")
    try:
        response = client.get('/api/schema')
        if response.status_code == 200:
            print(f"   ✓ PASSED - Schema retrieved")
            passed += 1
        else:
            print(f"   ✗ FAILED - Status code: {response.status_code}")
            failed += 1
    except Exception as e:
        print(f"   ✗ FAILED - Error: {e}")
        failed += 1
    
    # Test 5: Query (simple, fast query)
    print("\n5. POST /api/query")
    try:
        response = client.post('/api/query',
            data=json.dumps({
                'query': 'Hello',
                'customer_id': None
            }),
            content_type='application/json'
        )
        if response.status_code == 200:
            print(f"   ✓ PASSED - Query processed successfully")
            passed += 1
        else:
            print(f"   ✗ FAILED - Status code: {response.status_code}")
            failed += 1
    except Exception as e:
        print(f"   ✗ FAILED - Error: {e}")
        failed += 1
    
    # Summary
    print("\n" + "="*70)
    print(f"Test Results: {passed} passed, {failed} failed")
    print("="*70 + "\n")
    
    return failed == 0

if __name__ == '__main__':
    import sys
    success = test_api()
    sys.exit(0 if success else 1)
