"""
Test Multi-turn Conversation Memory
Tests conversation context and follow-up questions
"""

import sys
import logging
from agent import MedAssistAgent
from colorama import Fore, init
import uuid

init(autoreset=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s:%(name)s:%(message)s'
)


def test_conversation_memory():
    """Test multi-turn conversations with memory"""
    
    print("\n" + "="*70)
    print(f"{Fore.CYAN}🧪 Testing Conversation Memory (Multi-turn)")
    print("="*70 + "\n")
    
    # Initialize agent with memory
    print(f"{Fore.YELLOW}Initializing agent with conversation memory...")
    agent = MedAssistAgent(enable_vector_store=True, enable_memory=True)
    
    if not agent.connect():
        print(f"{Fore.RED}❌ Failed to connect to Neo4j")
        return False
    
    print(f"{Fore.GREEN}✓ Agent initialized with memory\n")
    
    # Generate a session ID
    session_id = f"test_session_{uuid.uuid4().hex[:8]}"
    print(f"{Fore.CYAN}Session ID: {session_id}\n")
    
    # Test conversation sequence with follow-ups
    conversations = [
        {
            "name": "Policy Exclusions Follow-up",
            "queries": [
                ("What treatments are excluded from the policy?", None),
                ("Are there any exceptions to these exclusions?", None),  # Follow-up
            ]
        },
        {
            "name": "Hospital Discount Query",
            "queries": [
                ("Tell me about hospitals with discounts in Bangalore", None),
                ("Which one has the highest discount?", None),  # Follow-up referencing previous
            ]
        },
        {
            "name": "Critical Illness Coverage",
            "queries": [
                ("Is heart attack covered under critical illness rider?", None),
                ("What about cancer?", None),  # Follow-up
                ("How much is the benefit amount?", None),  # Another follow-up
            ]
        }
    ]
    
    results = []
    
    for conv in conversations:
        print(f"\n{Fore.CYAN}{'='*70}")
        print(f"{Fore.CYAN}Test: {conv['name']}")
        print(f"{Fore.CYAN}{'='*70}\n")
        
        for i, (query, customer_id) in enumerate(conv['queries'], 1):
            print(f"{Fore.YELLOW}Query {i}: {query}")
            
            try:
                # Process query with session ID for memory
                response = agent.process_query(query, customer_id, session_id)
                
                print(f"\n{Fore.GREEN}Response:")
                # Print first 300 characters
                response_preview = response[:300] + "..." if len(response) > 300 else response
                print(f"{Fore.WHITE}{response_preview}\n")
                
                results.append({
                    'conversation': conv['name'],
                    'query': query,
                    'response': response,
                    'status': 'SUCCESS'
                })
                
            except Exception as e:
                print(f"{Fore.RED}✗ Error: {e}\n")
                results.append({
                    'conversation': conv['name'],
                    'query': query,
                    'status': 'FAILED',
                    'error': str(e)
                })
    
    # Check conversation history
    print(f"\n{Fore.CYAN}{'='*70}")
    print(f"{Fore.CYAN}Conversation History Summary")
    print(f"{Fore.CYAN}{'='*70}\n")
    
    if agent.memory:
        history = agent.memory.get_history(session_id)
        metadata = agent.memory.get_session_metadata(session_id)
        
        print(f"{Fore.CYAN}Session: {session_id}")
        print(f"{Fore.CYAN}Total messages: {len(history)}")
        print(f"{Fore.CYAN}Customer ID: {metadata.get('customer_id', 'None')}\n")
        
        print(f"{Fore.YELLOW}Last 5 messages:")
        for msg in history[-5:]:
            role = msg['role'].capitalize()
            content = msg['content'][:80] + "..." if len(msg['content']) > 80 else msg['content']
            print(f"  {role}: {content}")
    
    # Print summary
    print(f"\n{Fore.CYAN}{'='*70}")
    print(f"{Fore.CYAN}📊 TEST SUMMARY")
    print(f"{Fore.CYAN}{'='*70}\n")
    
    total_queries = len(results)
    successful = sum(1 for r in results if r['status'] == 'SUCCESS')
    failed = sum(1 for r in results if r['status'] == 'FAILED')
    
    print(f"{Fore.GREEN}✓ Successful: {successful}/{total_queries}")
    print(f"{Fore.RED}✗ Failed: {failed}/{total_queries}")
    
    # Test conversation context retrieval
    if agent.memory:
        print(f"\n{Fore.CYAN}Testing Context Retrieval:")
        context = agent.memory.get_context_string(session_id, last_n=4)
        print(f"{Fore.WHITE}{context[:200]}...")
    
    agent.close()
    
    print(f"\n{Fore.CYAN}{'='*70}")
    if failed == 0:
        print(f"{Fore.GREEN}✅ Conversation Memory: ALL TESTS PASSED!")
    else:
        print(f"{Fore.YELLOW}⚠️  Conversation Memory: {successful} tests successful")
    print(f"{Fore.CYAN}{'='*70}\n")
    
    return failed == 0


if __name__ == "__main__":
    success = test_conversation_memory()
    sys.exit(0 if success else 1)
