"""
MedAssist Chatbot - Conversational AI for Healthcare Insurance
Uses Gemini 2.0 Flash + Neo4j Knowledge Graph for intelligent query handling
"""
import google.generativeai as genai
from neo4j_connector import Neo4jConnector
from queries import QueryBuilder
from schema import get_schema_info
from config import GOOGLE_API_KEY, LLM_MODEL, LLM_TEMPERATURE
from colorama import Fore, Style, init
import json
import re

init(autoreset=True)


class MedAssistChatbot:
    """Conversational chatbot for healthcare insurance queries"""
    
    def __init__(self):
        self.connector = None
        self.conversation_history = []
        self.current_customer_id = None
        
        # Initialize Gemini
        genai.configure(api_key=GOOGLE_API_KEY)
        self.model = genai.GenerativeModel(
            model_name=LLM_MODEL,
            generation_config={
                "temperature": LLM_TEMPERATURE,
                "top_p": 0.95,
                "top_k": 40,
                "max_output_tokens": 2048,
            }
        )
        
        # Get schema for context
        self.schema_info = get_schema_info()
    
    def connect(self):
        """Connect to Neo4j"""
        self.connector = Neo4jConnector()
        return self.connector.connect(wait_time=5)
    
    def close(self):
        """Close connections"""
        if self.connector:
            self.connector.close()
    
    def print_banner(self):
        """Print chatbot banner"""
        print(f"\n{Fore.CYAN}{'='*70}")
        print(f"{Fore.CYAN}  🤖 MedAssist AI - Your Healthcare Insurance Assistant")
        print(f"{Fore.CYAN}  Powered by Gemini 2.0 Flash + Neo4j Knowledge Graph")
        print(f"{Fore.CYAN}{'='*70}")
        print(f"\n{Fore.YELLOW}Hi! I'm MedAssist AI. I can help you with:")
        print(f"  • Coverage checks for treatments and medications")
        print(f"  • Finding in-network hospitals")
        print(f"  • Claim status and history")
        print(f"  • Policy utilization and limits")
        print(f"  • General insurance questions")
        print(f"\n{Fore.GREEN}Type your question naturally, or 'help' for examples.")
        print(f"{Fore.RED}Type 'quit' or 'exit' to end the conversation.\n")
    
    def classify_intent(self, query: str) -> dict:
        """Use Gemini to classify user intent and extract parameters"""
        
        prompt = f"""You are an intent classifier for a healthcare insurance chatbot.
Analyze the user query and extract:
1. Intent (one of: coverage_check, hospital_finder, claim_history, policy_utilization, medication_coverage, general_question, greeting)
2. Parameters needed for the query
3. Customer ID if mentioned (format: CUST followed by 4 digits)

Available sample customer IDs: CUST0001 to CUST0010

User Query: "{query}"

Respond ONLY with valid JSON in this format:
{{
    "intent": "coverage_check|hospital_finder|claim_history|policy_utilization|medication_coverage|general_question|greeting",
    "confidence": 0.0-1.0,
    "parameters": {{
        "customer_id": "CUST0001 or null",
        "treatment_code": "E11|I10|M17|etc or null",
        "treatment_name": "extracted treatment name or null",
        "hospital_name": "extracted hospital name or null",
        "hospital_id": "HOSP0001 or null",
        "medication_name": "extracted medication name or null",
        "city": "extracted city or null",
        "min_discount": "minimum discount percentage as integer or null"
    }},
    "requires_customer_id": true|false
}}

Examples:
- "Is diabetes covered at Apollo Bangalore?" → {{"intent": "coverage_check", "parameters": {{"treatment_name": "diabetes", "hospital_name": "Apollo Bangalore"}}}}
- "Show me hospitals in Mumbai" → {{"intent": "hospital_finder", "parameters": {{"city": "Mumbai"}}}}
- "Which hospitals in Bangalore have discount greater than 10%" → {{"intent": "hospital_finder", "parameters": {{"city": "Bangalore", "min_discount": 10}}}}
- "What's my claim history?" → {{"intent": "claim_history", "requires_customer_id": true}}
"""
        
        try:
            response = self.model.generate_content(prompt)
            # Extract JSON from response
            text = response.text.strip()
            # Remove markdown code blocks if present
            text = re.sub(r'```json\s*|\s*```', '', text)
            result = json.loads(text)
            return result
        except Exception as e:
            print(f"{Fore.RED}Error classifying intent: {e}")
            return {
                "intent": "general_question",
                "confidence": 0.3,
                "parameters": {},
                "requires_customer_id": False
            }
    
    def generate_cypher_query(self, intent: str, parameters: dict) -> tuple:
        """Generate appropriate Cypher query based on intent"""
        
        customer_id = parameters.get('customer_id') or self.current_customer_id
        
        if intent == "coverage_check":
            # Try to map treatment name to code
            treatment_name = parameters.get('treatment_name', '').lower()
            treatment_code = None
            
            if 'diabetes' in treatment_name:
                treatment_code = 'E11'
            elif 'hypertension' in treatment_name or 'blood pressure' in treatment_name:
                treatment_code = 'I10'
            elif 'knee' in treatment_name or 'surgery' in treatment_name:
                treatment_code = 'M17'
            elif 'asthma' in treatment_name:
                treatment_code = 'J45'
            
            if treatment_code and customer_id:
                # Find first matching hospital
                hospital_name = parameters.get('hospital_name', 'Apollo')
                query = f"""
                MATCH (c:Customer {{id: $customer_id}})-[:HAS_POLICY]->(p:Policy),
                      (p)-[cov:COVERS]->(t:Treatment {{code: $treatment_code}}),
                      (p)-[net:IN_NETWORK]->(h:Hospital)
                WHERE toLower(h.name) CONTAINS toLower($hospital_name)
                  AND net.cashless_eligible = true
                RETURN p.plan_type as policy_plan,
                       t.name as treatment_name,
                       h.name as hospital_name,
                       h.city as city,
                       cov.sub_limit as sub_limit,
                       cov.copay as copay,
                       t.avg_cost as estimated_cost,
                       net.cashless_eligible as cashless
                LIMIT 1
                """
                params = {
                    'customer_id': customer_id,
                    'treatment_code': treatment_code,
                    'hospital_name': hospital_name
                }
                return query, params
        
        elif intent == "hospital_finder":
            city = parameters.get('city')
            min_discount = parameters.get('min_discount')
            
            if customer_id:
                # Build custom query with filters
                query = f"""
                MATCH (c:Customer {{id: $customer_id}})-[:HAS_POLICY]->(p:Policy)-[net:IN_NETWORK]->(h:Hospital)
                WHERE net.cashless_eligible = true
                """
                params = {'customer_id': customer_id}
                
                # Add city filter
                if city:
                    query += " AND toLower(h.city) = toLower($city)"
                    params['city'] = city
                
                # Add discount filter
                if min_discount:
                    query += " AND net.discount_pct >= $min_discount"
                    params['min_discount'] = int(min_discount)
                
                query += """
                RETURN h.name as hospital_name,
                       h.city as city,
                       h.tier as tier,
                       h.specialties as specialties,
                       net.discount_pct as discount
                ORDER BY net.discount_pct DESC, h.tier, h.name
                """
                
                return query, params
        
        elif intent == "claim_history":
            if customer_id:
                query = QueryBuilder.get_claim_history(customer_id, limit=5)
                return query, {'customer_id': customer_id, 'limit': 5}
        
        elif intent == "policy_utilization":
            if customer_id:
                query = QueryBuilder.get_policy_utilization(customer_id)
                return query, {'customer_id': customer_id}
        
        elif intent == "medication_coverage":
            medication_name = parameters.get('medication_name')
            if customer_id and medication_name:
                query = QueryBuilder.check_medication_coverage(customer_id, medication_name)
                return query, {'customer_id': customer_id, 'medication_name': medication_name}
        
        return None, None
    
    def format_response(self, intent: str, results: list, query: str) -> str:
        """Use Gemini to generate natural language response"""
        
        if not results:
            return "I couldn't find any information for that query. Could you please rephrase or provide more details?"
        
        prompt = f"""You are a friendly healthcare insurance assistant. 
Generate a natural, conversational response based on the user's question and the data from our knowledge graph.

User Question: "{query}"

Data from Knowledge Graph:
{json.dumps(results, indent=2)}

Guidelines:
- Be friendly and empathetic
- Explain coverage clearly with amounts in rupees (₹)
- Highlight important conditions (co-pay, pre-authorization, sub-limits)
- If coverage is available, emphasize the positive
- If there are restrictions, explain them gently
- Keep response concise but complete (2-4 sentences)

Generate a natural response:"""
        
        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            # Fallback to structured response
            if intent == "coverage_check" and results:
                r = results[0]
                return f"""Great news! Your {r.get('policy_plan')} policy covers {r.get('treatment_name')} at {r.get('hospital_name')}. 
The coverage has a sub-limit of ₹{r.get('sub_limit', 0):,} with a {r.get('copay', 0)}% co-pay. 
Estimated treatment cost is ₹{r.get('estimated_cost', 0):,}. Cashless facility is available!"""
            elif intent == "hospital_finder" and results:
                count = len(results)
                return f"I found {count} in-network hospitals for you. Here are your options with cashless facilities."
            else:
                return "Here's what I found for you."
    
    def handle_general_question(self, query: str) -> str:
        """Handle general questions with Gemini"""
        
        prompt = f"""You are a knowledgeable healthcare insurance assistant for MedAssist in India.
Answer this general question about health insurance clearly and helpfully.

User Question: "{query}"

Context: We offer 5 policy tiers (Bronze, Silver, Gold, Platinum, Diamond) with coverage from ₹3L to ₹25L.
We have partnerships with major hospitals like Apollo, Fortis, Max, Manipal across Indian cities.
We cover treatments including diabetes, hypertension, surgeries, maternity, and emergency care.

Provide a helpful, accurate answer (2-3 sentences):"""
        
        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            return "I'm here to help with your insurance questions. Could you please rephrase that?"
    
    def chat(self, user_input: str) -> str:
        """Main chat function"""
        
        # Classify intent
        classification = self.classify_intent(user_input)
        intent = classification['intent']
        confidence = classification.get('confidence', 0.5)
        parameters = classification.get('parameters', {})
        requires_customer = classification.get('requires_customer_id', False)
        
        # Handle greeting
        if intent == "greeting":
            return f"{Fore.GREEN}Hello! I'm here to help you with your healthcare insurance needs. You can ask me about coverage, claims, hospitals, or policies. What would you like to know?"
        
        # Check if customer ID is needed but not provided
        if requires_customer and not self.current_customer_id and not parameters.get('customer_id'):
            return f"{Fore.YELLOW}To help you with that, I need to know your Customer ID. Could you please provide it? (Format: CUST0001)"
        
        # Handle general questions
        if intent == "general_question" or confidence < 0.6:
            return self.handle_general_question(user_input)
        
        # Generate and execute query
        query, params = self.generate_cypher_query(intent, parameters)
        
        if query and params:
            try:
                results = self.connector.execute_query(query, params)
                
                if results:
                    # Generate natural response
                    response = self.format_response(intent, results, user_input)
                    
                    # Add structured data for display
                    if intent == "hospital_finder" and len(results) > 0:
                        response += f"\n\n{Fore.CYAN}Here are your options:"
                        for i, hospital in enumerate(results[:5], 1):
                            response += f"\n{Fore.GREEN}  {i}. {hospital['hospital_name']} - {hospital['city']}"
                            response += f"\n     Tier: {hospital['tier']} | Discount: {hospital.get('discount', 0)}%"
                    
                    elif intent == "claim_history" and len(results) > 0:
                        response += f"\n\n{Fore.CYAN}Your recent claims:"
                        for i, claim in enumerate(results, 1):
                            response += f"\n{Fore.GREEN}  {i}. {claim['claim_id']} - {claim['status']}"
                            response += f"\n     Amount: ₹{claim['claimed_amount']:,} | Date: {claim['claim_date']}"
                    
                    return response
                else:
                    return f"{Fore.YELLOW}I couldn't find any matching information. Could you provide more details or rephrase your question?"
            
            except Exception as e:
                print(f"{Fore.RED}Error executing query: {e}")
                return "I encountered an issue looking that up. Could you try asking differently?"
        
        return "I'm not sure how to help with that. Could you rephrase your question?"
    
    def run(self):
        """Run the chatbot"""
        self.print_banner()
        
        # Connect to Neo4j
        print(f"{Fore.YELLOW}Connecting to knowledge graph...")
        if not self.connect():
            print(f"{Fore.RED}Failed to connect to Neo4j. Exiting.")
            return
        print(f"{Fore.GREEN}✓ Connected!\n")
        
        # Ask for customer ID
        print(f"{Fore.CYAN}To personalize your experience, please enter your Customer ID.")
        print(f"{Fore.CYAN}(Or press Enter to skip and browse general information)")
        customer_input = input(f"{Fore.YELLOW}Customer ID: ").strip()
        
        if customer_input:
            # Validate customer ID
            if re.match(r'^CUST\d{4}$', customer_input):
                self.current_customer_id = customer_input
                print(f"{Fore.GREEN}✓ Welcome back! I have your account information.\n")
            else:
                print(f"{Fore.YELLOW}Invalid format. You can provide it later in the conversation.\n")
        else:
            print(f"{Fore.BLUE}No problem! You can still ask general questions.\n")
        
        # Main chat loop
        while True:
            try:
                # Get user input
                user_input = input(f"{Fore.CYAN}You: {Fore.WHITE}").strip()
                
                if not user_input:
                    continue
                
                # Check for exit commands
                if user_input.lower() in ['quit', 'exit', 'bye', 'goodbye']:
                    print(f"\n{Fore.GREEN}Thank you for using MedAssist AI! Stay healthy! 👋\n")
                    break
                
                # Check for help
                if user_input.lower() in ['help', '?']:
                    print(f"\n{Fore.CYAN}Here are some example questions:")
                    print(f"{Fore.GREEN}  • Is diabetes covered at Apollo Bangalore?")
                    print(f"{Fore.GREEN}  • Show me hospitals in Mumbai")
                    print(f"{Fore.GREEN}  • What's my claim history?")
                    print(f"{Fore.GREEN}  • Is Metformin covered under my policy?")
                    print(f"{Fore.GREEN}  • How much of my policy have I used?")
                    print(f"{Fore.GREEN}  • What does my plan cover?\n")
                    continue
                
                # Check for customer ID in input
                customer_match = re.search(r'CUST\d{4}', user_input)
                if customer_match and not self.current_customer_id:
                    self.current_customer_id = customer_match.group()
                    print(f"{Fore.GREEN}✓ Got it! Using customer ID: {self.current_customer_id}\n")
                
                # Get response
                print(f"{Fore.YELLOW}🤖 MedAssist AI: {Fore.WHITE}", end="")
                response = self.chat(user_input)
                print(response)
                print()  # Empty line for spacing
                
            except KeyboardInterrupt:
                print(f"\n\n{Fore.BLUE}Interrupted. Goodbye! 👋\n")
                break
            except Exception as e:
                print(f"\n{Fore.RED}Error: {e}")
                print(f"{Fore.YELLOW}Let's try that again.\n")
        
        # Cleanup
        self.close()


def main():
    """Main entry point"""
    chatbot = MedAssistChatbot()
    chatbot.run()


if __name__ == "__main__":
    main()
