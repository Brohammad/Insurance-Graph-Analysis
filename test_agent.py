"""
Test Suite for MedAssist Agentic Layer (LangGraph)
Tests all nodes and routing logic in the StateGraph workflow
"""
from agent import MedAssistAgent
from colorama import Fore, Style, init
import sys

init(autoreset=True)


class AgentTester:
    """Test suite for the agentic workflow"""
    
    def __init__(self):
        self.agent = MedAssistAgent()
        self.passed = 0
        self.failed = 0
    
    def connect(self):
        """Connect to Neo4j"""
        return self.agent.connect()
    
    def close(self):
        """Close connections"""
        self.agent.close()
    
    def print_test_header(self, test_num: int, description: str):
        """Print test header"""
        print(f"\n{Fore.CYAN}{'='*70}")
        print(f"{Fore.CYAN}TEST {test_num}: {description}")
        print(f"{Fore.CYAN}{'='*70}\n")
    
    def test_1_coverage_check(self):
        """Test coverage check intent"""
        self.print_test_header(1, "Coverage Check - Classifier → Planner → Executor → Synthesizer")
        
        query = "Is diabetes covered at Apollo Bangalore?"
        customer_id = "CUST0001"
        
        print(f"Query: {query}")
        print(f"Customer: {customer_id}\n")
        
        try:
            response = self.agent.process_query(query, customer_id)
            
            if response and len(response) > 10:
                print(f"{Fore.GREEN}✓ Test PASSED")
                print(f"{Fore.GREEN}Response: {response[:100]}...")
                self.passed += 1
            else:
                print(f"{Fore.RED}✗ Test FAILED - Empty or invalid response")
                self.failed += 1
        
        except Exception as e:
            print(f"{Fore.RED}✗ Test FAILED - Exception: {e}")
            self.failed += 1
    
    def test_2_hospital_finder_with_filters(self):
        """Test hospital finder with city and discount filters"""
        self.print_test_header(2, "Hospital Finder - With City and Discount Filters")
        
        query = "Show me hospitals in Bangalore with discount greater than 10%"
        customer_id = "CUST0001"
        
        print(f"Query: {query}")
        print(f"Customer: {customer_id}\n")
        
        try:
            response = self.agent.process_query(query, customer_id)
            
            if response and ("bangalore" in response.lower() or "hospital" in response.lower()):
                print(f"{Fore.GREEN}✓ Test PASSED")
                print(f"{Fore.GREEN}Response: {response[:150]}...")
                self.passed += 1
            else:
                print(f"{Fore.RED}✗ Test FAILED - Response doesn't match query")
                self.failed += 1
        
        except Exception as e:
            print(f"{Fore.RED}✗ Test FAILED - Exception: {e}")
            self.failed += 1
    
    def test_3_claim_history(self):
        """Test claim history retrieval"""
        self.print_test_header(3, "Claim History - Database Query")
        
        query = "What is my claim history?"
        customer_id = "CUST0001"
        
        print(f"Query: {query}")
        print(f"Customer: {customer_id}\n")
        
        try:
            response = self.agent.process_query(query, customer_id)
            
            if response and ("claim" in response.lower() or "no claims" in response.lower()):
                print(f"{Fore.GREEN}✓ Test PASSED")
                print(f"{Fore.GREEN}Response: {response[:150]}...")
                self.passed += 1
            else:
                print(f"{Fore.RED}✗ Test FAILED - Response doesn't match query")
                self.failed += 1
        
        except Exception as e:
            print(f"{Fore.RED}✗ Test FAILED - Exception: {e}")
            self.failed += 1
    
    def test_4_policy_utilization(self):
        """Test policy utilization query"""
        self.print_test_header(4, "Policy Utilization - Complex Query")
        
        query = "How much of my policy have I used?"
        customer_id = "CUST0001"
        
        print(f"Query: {query}")
        print(f"Customer: {customer_id}\n")
        
        try:
            response = self.agent.process_query(query, customer_id)
            
            if response and ("policy" in response.lower() or "cover" in response.lower()):
                print(f"{Fore.GREEN}✓ Test PASSED")
                print(f"{Fore.GREEN}Response: {response[:150]}...")
                self.passed += 1
            else:
                print(f"{Fore.RED}✗ Test FAILED - Response doesn't match query")
                self.failed += 1
        
        except Exception as e:
            print(f"{Fore.RED}✗ Test FAILED - Exception: {e}")
            self.failed += 1
    
    def test_5_medication_coverage(self):
        """Test medication coverage check"""
        self.print_test_header(5, "Medication Coverage - Multi-hop Query")
        
        query = "Is Metformin covered in my policy?"
        customer_id = "CUST0001"
        
        print(f"Query: {query}")
        print(f"Customer: {customer_id}\n")
        
        try:
            response = self.agent.process_query(query, customer_id)
            
            if response and ("metformin" in response.lower() or "medication" in response.lower()):
                print(f"{Fore.GREEN}✓ Test PASSED")
                print(f"{Fore.GREEN}Response: {response[:150]}...")
                self.passed += 1
            else:
                print(f"{Fore.RED}✗ Test FAILED - Response doesn't match query")
                self.failed += 1
        
        except Exception as e:
            print(f"{Fore.RED}✗ Test FAILED - Exception: {e}")
            self.failed += 1
    
    def test_6_general_question_rag_fallback(self):
        """Test RAG fallback for general questions"""
        self.print_test_header(6, "General Question - RAG Fallback Node")
        
        query = "What is health insurance?"
        customer_id = None
        
        print(f"Query: {query}")
        print(f"Customer: {customer_id or 'None'}\n")
        
        try:
            response = self.agent.process_query(query, customer_id)
            
            if response and len(response) > 20:
                print(f"{Fore.GREEN}✓ Test PASSED")
                print(f"{Fore.GREEN}Response: {response[:150]}...")
                self.passed += 1
            else:
                print(f"{Fore.RED}✗ Test FAILED - Empty or invalid response")
                self.failed += 1
        
        except Exception as e:
            print(f"{Fore.RED}✗ Test FAILED - Exception: {e}")
            self.failed += 1
    
    def test_7_low_confidence_routing(self):
        """Test low confidence routing to RAG fallback"""
        self.print_test_header(7, "Low Confidence - Routing Logic")
        
        query = "xyz abc 123"
        customer_id = "CUST0001"
        
        print(f"Query: {query}")
        print(f"Customer: {customer_id}\n")
        
        try:
            response = self.agent.process_query(query, customer_id)
            
            if response:
                print(f"{Fore.GREEN}✓ Test PASSED - Agent handled unclear query")
                print(f"{Fore.GREEN}Response: {response[:150]}...")
                self.passed += 1
            else:
                print(f"{Fore.RED}✗ Test FAILED - No response")
                self.failed += 1
        
        except Exception as e:
            print(f"{Fore.RED}✗ Test FAILED - Exception: {e}")
            self.failed += 1
    
    def test_8_greeting(self):
        """Test greeting intent"""
        self.print_test_header(8, "Greeting Intent - RAG Fallback")
        
        query = "Hello!"
        customer_id = None
        
        print(f"Query: {query}")
        print(f"Customer: {customer_id or 'None'}\n")
        
        try:
            response = self.agent.process_query(query, customer_id)
            
            if response and len(response) > 10:
                print(f"{Fore.GREEN}✓ Test PASSED")
                print(f"{Fore.GREEN}Response: {response[:150]}...")
                self.passed += 1
            else:
                print(f"{Fore.RED}✗ Test FAILED - Empty or invalid response")
                self.failed += 1
        
        except Exception as e:
            print(f"{Fore.RED}✗ Test FAILED - Exception: {e}")
            self.failed += 1
    
    def run_all_tests(self):
        """Run all agent tests"""
        print(f"{Fore.CYAN}{'='*70}")
        print(f"{Fore.CYAN}MedAssist Agentic Layer - Test Suite")
        print(f"{Fore.CYAN}Testing LangGraph StateGraph Workflow")
        print(f"{Fore.CYAN}{'='*70}\n")
        
        self.test_1_coverage_check()
        self.test_2_hospital_finder_with_filters()
        self.test_3_claim_history()
        self.test_4_policy_utilization()
        self.test_5_medication_coverage()
        self.test_6_general_question_rag_fallback()
        self.test_7_low_confidence_routing()
        self.test_8_greeting()
        
        # Print summary
        print(f"\n{Fore.CYAN}{'='*70}")
        print(f"{Fore.CYAN}Test Summary")
        print(f"{Fore.CYAN}{'='*70}")
        print(f"{Fore.GREEN}✓ Passed: {self.passed}")
        print(f"{Fore.RED}✗ Failed: {self.failed}")
        print(f"{Fore.CYAN}{'='*70}\n")
        
        if self.failed == 0:
            print(f"{Fore.GREEN}✓ All tests passed!\n")
            return 0
        else:
            print(f"{Fore.RED}✗ Some tests failed\n")
            return 1


def main():
    """Main test runner"""
    tester = AgentTester()
    
    print("Connecting to knowledge graph...")
    if not tester.connect():
        print(f"{Fore.RED}Failed to connect to Neo4j. Exiting.")
        return 1
    
    print(f"{Fore.GREEN}✓ Connected!\n")
    
    try:
        exit_code = tester.run_all_tests()
    finally:
        tester.close()
        print("Connection closed.")
    
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
