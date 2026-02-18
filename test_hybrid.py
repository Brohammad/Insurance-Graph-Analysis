"""
Test Hybrid Queries (KG + RAG)
Tests queries that need both Knowledge Graph and RAG
"""
from agent import MedAssistAgent
from colorama import Fore, Style, init

init(autoreset=True)

def test_hybrid_query(agent, query, description):
    """Test a single hybrid query"""
    print(f"\n{'='*70}")
    print(f"{Fore.CYAN}Test: {description}")
    print(f"{'='*70}")
    print(f"{Fore.YELLOW}Query: {query}")
    print(f"{'-'*70}")
    
    try:
        response = agent.process_query(query, customer_id=None)
        print(f"\n{Fore.GREEN}Response:")
        print(response)
        return True
    except Exception as e:
        print(f"\n{Fore.RED}Error: {e}")
        return False

def main():
    print(f"\n{Fore.CYAN}{'='*70}")
    print(f"{Fore.CYAN}TESTING HYBRID QUERIES (KG + RAG)")
    print(f"{Fore.CYAN}{'='*70}\n")
    
    # Initialize agent with both vector store and memory
    print("Initializing agent with hybrid capabilities...")
    agent = MedAssistAgent(enable_vector_store=True, enable_memory=True)
    print(f"{Fore.GREEN}✓ Agent initialized\n")
    
    # Test cases
    test_cases = [
        {
            "query": "What is the policy for diabetes in hospitals in Mumbai with a discount of 10 percent?",
            "description": "Diabetes policy + Mumbai hospitals with 10% discount (HYBRID)"
        },
        {
            "query": "Show me hospitals in Bangalore with 15% discount and tell me about critical illness coverage",
            "description": "Hospital list + Critical illness policy (HYBRID)"
        },
        {
            "query": "What are the waiting periods for heart disease and which hospitals in Delhi have cashless?",
            "description": "Waiting periods + Delhi hospitals (HYBRID)"
        },
        {
            "query": "Is cancer covered at Apollo Mumbai?",
            "description": "Specific hospital coverage (Should use KG, not hybrid)"
        },
        {
            "query": "What are the exclusions in my policy?",
            "description": "General policy question (Should use RAG, not hybrid)"
        }
    ]
    
    results = []
    for test in test_cases:
        success = test_hybrid_query(agent, test["query"], test["description"])
        results.append(success)
    
    # Summary
    print(f"\n\n{Fore.CYAN}{'='*70}")
    print(f"{Fore.CYAN}TEST SUMMARY")
    print(f"{Fore.CYAN}{'='*70}")
    
    passed = sum(results)
    total = len(results)
    
    print(f"\n{Fore.GREEN}✓ Successful: {passed}/{total}")
    if passed < total:
        print(f"{Fore.RED}✗ Failed: {total - passed}/{total}")
    
    if passed == total:
        print(f"\n{Fore.GREEN}{'='*70}")
        print(f"{Fore.GREEN}✅ ALL HYBRID TESTS PASSED!")
        print(f"{Fore.GREEN}{'='*70}\n")
    else:
        print(f"\n{Fore.YELLOW}{'='*70}")
        print(f"{Fore.YELLOW}⚠️  Some tests need attention")
        print(f"{Fore.YELLOW}{'='*70}\n")

if __name__ == "__main__":
    main()
