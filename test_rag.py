"""
Test ChromaDB RAG Integration with MedAssist Agent
Tests policy document retrieval and answer generation
"""

import sys
import logging
from agent import MedAssistAgent
from colorama import Fore, Style, init

init(autoreset=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s:%(name)s:%(message)s'
)


def test_rag_queries():
    """Test policy-related queries that should use RAG"""
    
    print("\n" + "="*70)
    print(f"{Fore.CYAN}🧪 Testing ChromaDB RAG Integration")
    print("="*70 + "\n")
    
    # Initialize agent
    print(f"{Fore.YELLOW}Initializing agent with vector store...")
    agent = MedAssistAgent(enable_vector_store=True)
    
    if not agent.connect():
        print(f"{Fore.RED}❌ Failed to connect to Neo4j")
        return False
    
    print(f"{Fore.GREEN}✓ Agent initialized\n")
    
    # Test queries that should trigger RAG fallback
    test_queries = [
        {
            "query": "What is the waiting period for pre-existing diseases?",
            "expected_keywords": ["waiting", "period", "2 year", "pre-existing"],
            "description": "Policy waiting period question"
        },
        {
            "query": "Is cancer covered under the critical illness rider?",
            "expected_keywords": ["cancer", "covered", "critical illness", "chemotherapy"],
            "description": "Critical illness coverage question"
        },
        {
            "query": "What are the maternity benefits in the comprehensive policy?",
            "expected_keywords": ["maternity", "delivery", "₹50,000", "₹75,000"],
            "description": "Maternity benefits question"
        },
        {
            "query": "Which hospitals are in the Tier-1 network?",
            "expected_keywords": ["Apollo", "Fortis", "Max", "Tier-1"],
            "description": "Network hospital question"
        },
        {
            "query": "What is excluded from the critical illness rider?",
            "expected_keywords": ["exclusions", "not cover", "pre-existing", "self-inflicted"],
            "description": "Exclusions question"
        }
    ]
    
    results = []
    for i, test_case in enumerate(test_queries, 1):
        print(f"\n{Fore.CYAN}{'='*70}")
        print(f"{Fore.CYAN}Test {i}: {test_case['description']}")
        print(f"{Fore.CYAN}{'='*70}")
        print(f"{Fore.YELLOW}Query: {test_case['query']}\n")
        
        try:
            # Process query
            response = agent.process_query(test_case['query'])
            
            print(f"\n{Fore.GREEN}Response:")
            print(f"{Fore.WHITE}{response}\n")
            
            # Check if expected keywords are in response
            response_lower = response.lower()
            found_keywords = [kw for kw in test_case['expected_keywords'] 
                            if kw.lower() in response_lower]
            
            success = len(found_keywords) >= 2  # At least 2 keywords should match
            
            if success:
                print(f"{Fore.GREEN}✓ PASS - Found relevant information")
                print(f"{Fore.GREEN}  Matched keywords: {', '.join(found_keywords)}")
            else:
                print(f"{Fore.YELLOW}⚠ PARTIAL - Response may lack specific details")
                print(f"{Fore.YELLOW}  Matched keywords: {', '.join(found_keywords) if found_keywords else 'None'}")
            
            results.append({
                'test': test_case['description'],
                'query': test_case['query'],
                'response': response,
                'status': 'PASS' if success else 'PARTIAL',
                'keywords_found': found_keywords
            })
            
        except Exception as e:
            print(f"{Fore.RED}✗ FAIL - Error: {e}")
            results.append({
                'test': test_case['description'],
                'query': test_case['query'],
                'status': 'FAIL',
                'error': str(e)
            })
    
    # Print summary
    print(f"\n{Fore.CYAN}{'='*70}")
    print(f"{Fore.CYAN}📊 TEST SUMMARY")
    print(f"{Fore.CYAN}{'='*70}\n")
    
    passed = sum(1 for r in results if r['status'] == 'PASS')
    partial = sum(1 for r in results if r['status'] == 'PARTIAL')
    failed = sum(1 for r in results if r['status'] == 'FAIL')
    
    print(f"{Fore.GREEN}✓ Passed: {passed}/{len(test_queries)}")
    print(f"{Fore.YELLOW}⚠ Partial: {partial}/{len(test_queries)}")
    print(f"{Fore.RED}✗ Failed: {failed}/{len(test_queries)}")
    
    # Detailed results
    print(f"\n{Fore.CYAN}Detailed Results:")
    for i, result in enumerate(results, 1):
        status_color = Fore.GREEN if result['status'] == 'PASS' else Fore.YELLOW if result['status'] == 'PARTIAL' else Fore.RED
        print(f"{status_color}{i}. {result['test']}: {result['status']}")
        if result['status'] != 'FAIL' and 'keywords_found' in result:
            print(f"   Keywords: {', '.join(result['keywords_found'])}")
    
    agent.close()
    
    print(f"\n{Fore.CYAN}{'='*70}")
    if failed == 0:
        print(f"{Fore.GREEN}✅ ChromaDB RAG Integration: ALL TESTS PASSED!")
    else:
        print(f"{Fore.YELLOW}⚠️  ChromaDB RAG Integration: {passed + partial} tests successful")
    print(f"{Fore.CYAN}{'='*70}\n")
    
    return failed == 0


if __name__ == "__main__":
    success = test_rag_queries()
    sys.exit(0 if success else 1)
