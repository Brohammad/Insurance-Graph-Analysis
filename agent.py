"""
MedAssist Agentic Layer - LangGraph StateGraph Implementation
Uses LangGraph for orchestrating multi-agent workflow with Neo4j Knowledge Graph
"""
from typing import TypedDict, Annotated, Sequence, Optional
import operator
from langgraph.graph import StateGraph, END
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from neo4j_connector import Neo4jConnector
from queries import QueryBuilder
from schema import get_schema_info
from config import GOOGLE_API_KEY, LLM_MODEL, LLM_TEMPERATURE, CONFIDENCE_THRESHOLD
from colorama import Fore, Style, init
import json
import re
import logging

# Import ChromaDB vector store (Phase 3.2)
try:
    from vector_store import PolicyVectorStore
    VECTOR_STORE_AVAILABLE = True
except ImportError:
    VECTOR_STORE_AVAILABLE = False
    logging.warning("Vector store not available. Install chromadb, pypdf, and sentence-transformers for RAG functionality.")

# Import conversation memory (Phase 3.3)
try:
    from conversation_memory import ConversationMemory
    CONVERSATION_MEMORY_AVAILABLE = True
except ImportError:
    CONVERSATION_MEMORY_AVAILABLE = False
    logging.warning("Conversation memory not available.")

init(autoreset=True)


# Define the state for the agent workflow
class AgentState(TypedDict):
    """State maintained throughout the agent workflow"""
    messages: Annotated[Sequence[BaseMessage], operator.add]
    user_query: str
    customer_id: str
    session_id: str
    intent: str
    confidence: float
    needs_hybrid: bool
    parameters: dict
    cypher_query: str
    cypher_params: dict
    query_results: list
    rag_results: list
    final_response: str
    error: str
    requires_escalation: bool
    attempt_count: int


class MedAssistAgent:
    """LangGraph-based agentic workflow for healthcare insurance queries"""
    
    def __init__(self, enable_vector_store: bool = True, enable_memory: bool = True):
        # Initialize Neo4j connector
        self.connector = Neo4jConnector()
        try:
            self.connector.connect(wait_time=5)
        except Exception as e:
            print(f"{Fore.YELLOW}⚠ Neo4j connection failed: {e}")
            self.connector = None
        
        self.llm = ChatGoogleGenerativeAI(
            model=LLM_MODEL,
            google_api_key=GOOGLE_API_KEY,
            temperature=LLM_TEMPERATURE
        )
        self.schema_info = get_schema_info()
        
        # Initialize vector store for RAG (Phase 3.2)
        self.vector_store = None
        if enable_vector_store and VECTOR_STORE_AVAILABLE:
            try:
                self.vector_store = PolicyVectorStore()
                print(f"{Fore.GREEN}✓ Vector store initialized for policy RAG")
            except Exception as e:
                print(f"{Fore.YELLOW}⚠ Vector store initialization failed: {e}")
                self.vector_store = None
        
        # Initialize conversation memory (Phase 3.3)
        self.memory = None
        if enable_memory and CONVERSATION_MEMORY_AVAILABLE:
            try:
                self.memory = ConversationMemory(max_history=10, ttl_minutes=60)
                print(f"{Fore.GREEN}✓ Conversation memory initialized")
            except Exception as e:
                print(f"{Fore.YELLOW}⚠ Conversation memory initialization failed: {e}")
                self.memory = None
                self.vector_store = None
        
        self.workflow = self._build_workflow()
    
    def connect(self):
        """Connect to Neo4j"""
        self.connector = Neo4jConnector()
        return self.connector.connect(wait_time=5)
    
    def close(self):
        """Close connections"""
        if self.connector:
            self.connector.close()
    
    def _build_workflow(self) -> StateGraph:
        """Build the LangGraph StateGraph workflow"""
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("classifier", self.classifier_node)
        workflow.add_node("query_planner", self.query_planner_node)
        workflow.add_node("kg_executor", self.kg_executor_node)
        workflow.add_node("synthesizer", self.synthesizer_node)
        workflow.add_node("rag_fallback", self.rag_fallback_node)
        workflow.add_node("hybrid", self.hybrid_node)
        workflow.add_node("escalation", self.escalation_node)
        
        # Set entry point
        workflow.set_entry_point("classifier")
        
        # Add conditional edges
        workflow.add_conditional_edges(
            "classifier",
            self.route_after_classification,
            {
                "query_planner": "query_planner",
                "rag_fallback": "rag_fallback",
                "hybrid": "hybrid",
                "escalation": "escalation"
            }
        )
        
        workflow.add_conditional_edges(
            "query_planner",
            self.route_after_planning,
            {
                "kg_executor": "kg_executor",
                "rag_fallback": "rag_fallback",
                "escalation": "escalation"
            }
        )
        
        workflow.add_conditional_edges(
            "kg_executor",
            self.route_after_execution,
            {
                "synthesizer": "synthesizer",
                "query_planner": "query_planner",  # Retry with correction
                "rag_fallback": "rag_fallback",
                "escalation": "escalation"
            }
        )
        
        workflow.add_edge("synthesizer", END)
        workflow.add_edge("rag_fallback", END)
        workflow.add_edge("hybrid", END)
        workflow.add_edge("escalation", END)
        
        return workflow.compile()
    
    # ========== NODE IMPLEMENTATIONS ==========
    
    def classifier_node(self, state: AgentState) -> AgentState:
        """Classify user intent and extract parameters"""
        print(f"{Fore.CYAN}[Classifier] Analyzing query...")
        
        user_query = state["user_query"]
        customer_id = state.get("customer_id")
        
        prompt = f"""You are an intent classifier for a healthcare insurance system.
Analyze the user query and extract:
1. Primary Intent (one of: coverage_check, hospital_finder, claim_history, policy_utilization, medication_coverage, escalation, general_question, greeting)
2. Secondary Intent (if query needs both KG data AND policy information)
3. Required parameters
4. Confidence score (0.0-1.0)

INTENT CLASSIFICATION RULES:
- "escalation": User explicitly asks to speak to agent/human
- "coverage_check": Asks if treatment/condition is covered (needs KG if hospital/customer specified)
- "hospital_finder": Asks for hospital list, discounts, or hospital details
- "policy_utilization": General policy questions about coverage, limits, waiting periods (needs RAG)
- "claim_history": Asks about past claims (needs KG + customer_id)
- "medication_coverage": Asks about medication coverage (needs KG)

HYBRID QUERY DETECTION:
If query mentions BOTH policy details (coverage, waiting period, limits) AND specific entities (hospital, city, discount), set needs_hybrid=true.

Examples of hybrid queries:
- "What is the policy for diabetes in hospitals in Mumbai with 10% discount?" → needs_hybrid=true
- "Is diabetes covered at Apollo Bangalore?" → needs_hybrid=false (specific hospital, use KG)
- "What are the waiting periods for critical illness?" → needs_hybrid=false (general policy, use RAG)

Schema Context:
{self.schema_info}

User Query: "{user_query}"
Customer ID: {customer_id or "Not provided"}

Respond ONLY with valid JSON:
{{
    "intent": "coverage_check|hospital_finder|claim_history|policy_utilization|medication_coverage|escalation|general_question|greeting",
    "confidence": 0.0-1.0,
    "needs_hybrid": true|false,
    "parameters": {{
        "treatment_code": "E11|I10|M17|etc or null",
        "treatment_name": "extracted name or null",
        "hospital_name": "extracted name or null",
        "medication_name": "extracted name or null",
        "city": "extracted city or null",
        "min_discount": "integer or null"
    }},
    "requires_customer_id": true|false
}}
"""
        
        try:
            response = self.llm.invoke([HumanMessage(content=prompt)])
            text = response.content.strip()
            text = re.sub(r'```json\s*|\s*```', '', text)
            result = json.loads(text)
            
            state["intent"] = result["intent"]
            state["confidence"] = result["confidence"]
            state["parameters"] = result.get("parameters", {})
            state["needs_hybrid"] = result.get("needs_hybrid", False)
            state["messages"] = [AIMessage(content=f"Intent: {result['intent']}, Confidence: {result['confidence']:.2f}")]
            
            hybrid_flag = " [HYBRID]" if state["needs_hybrid"] else ""
            print(f"{Fore.GREEN}[Classifier] Intent: {result['intent']} (confidence: {result['confidence']:.2f}){hybrid_flag}")
            
        except Exception as e:
            print(f"{Fore.RED}[Classifier] Error: {e}")
            state["intent"] = "general_question"
            state["confidence"] = 0.3
            state["error"] = str(e)
        
        return state
    
    def query_planner_node(self, state: AgentState) -> AgentState:
        """Generate Cypher query based on intent and parameters"""
        print(f"{Fore.CYAN}[Query Planner] Generating Cypher query...")
        
        intent = state["intent"]
        parameters = state["parameters"]
        customer_id = state["customer_id"]
        
        try:
            cypher_query = None
            cypher_params = {}
            
            if intent == "coverage_check":
                treatment_name = parameters.get('treatment_name', '').lower()
                treatment_code = self._map_treatment_name_to_code(treatment_name)
                hospital_name = parameters.get('hospital_name', 'Apollo')
                
                if treatment_code and customer_id:
                    cypher_query = f"""
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
                    cypher_params = {
                        'customer_id': customer_id,
                        'treatment_code': treatment_code,
                        'hospital_name': hospital_name
                    }
            
            elif intent == "hospital_finder":
                city = parameters.get('city')
                min_discount = parameters.get('min_discount')
                
                if customer_id:
                    cypher_query = """
                    MATCH (c:Customer {id: $customer_id})-[:HAS_POLICY]->(p:Policy)-[net:IN_NETWORK]->(h:Hospital)
                    WHERE net.cashless_eligible = true
                    """
                    cypher_params = {'customer_id': customer_id}
                    
                    if city:
                        cypher_query += " AND toLower(h.city) = toLower($city)"
                        cypher_params['city'] = city
                    
                    if min_discount:
                        cypher_query += " AND net.discount_pct >= $min_discount"
                        cypher_params['min_discount'] = int(min_discount)
                    
                    cypher_query += """
                    RETURN h.name as hospital_name,
                           h.city as city,
                           h.tier as tier,
                           h.specialties as specialties,
                           net.discount_pct as discount
                    ORDER BY net.discount_pct DESC, h.tier, h.name
                    """
            
            elif intent == "claim_history":
                if customer_id:
                    cypher_query = QueryBuilder.get_claim_history(customer_id, limit=5)
                    cypher_params = {'customer_id': customer_id, 'limit': 5}
            
            elif intent == "policy_utilization":
                if customer_id:
                    cypher_query = QueryBuilder.get_policy_utilization(customer_id)
                    cypher_params = {'customer_id': customer_id}
            
            elif intent == "medication_coverage":
                medication_name = parameters.get('medication_name')
                if customer_id and medication_name:
                    cypher_query = QueryBuilder.check_medication_coverage(customer_id, medication_name)
                    cypher_params = {'customer_id': customer_id, 'medication_name': medication_name}
            
            if cypher_query:
                state["cypher_query"] = cypher_query
                state["cypher_params"] = cypher_params
                print(f"{Fore.GREEN}[Query Planner] Cypher query generated successfully")
            else:
                state["error"] = "Could not generate Cypher query"
                print(f"{Fore.YELLOW}[Query Planner] No query generated for intent: {intent}")
        
        except Exception as e:
            print(f"{Fore.RED}[Query Planner] Error: {e}")
            state["error"] = str(e)
        
        return state
    
    def kg_executor_node(self, state: AgentState) -> AgentState:
        """Execute Cypher query against Neo4j"""
        print(f"{Fore.CYAN}[KG Executor] Executing query...")
        
        cypher_query = state.get("cypher_query")
        cypher_params = state.get("cypher_params", {})
        
        if not cypher_query:
            state["error"] = "No query to execute"
            return state
        
        try:
            results = self.connector.execute_query(cypher_query, cypher_params)
            state["query_results"] = results
            print(f"{Fore.GREEN}[KG Executor] Query executed successfully ({len(results)} results)")
            
            if not results:
                print(f"{Fore.YELLOW}[KG Executor] No results found")
        
        except Exception as e:
            print(f"{Fore.RED}[KG Executor] Error: {e}")
            state["error"] = str(e)
            state["attempt_count"] = state.get("attempt_count", 0) + 1
        
        return state
    
    def synthesizer_node(self, state: AgentState) -> AgentState:
        """Generate natural language response from query results"""
        print(f"{Fore.CYAN}[Synthesizer] Generating response...")
        
        results = state.get("query_results", [])
        user_query = state["user_query"]
        intent = state["intent"]
        
        if not results:
            state["final_response"] = "I couldn't find any information matching your query. Could you provide more details?"
            return state
        
        prompt = f"""You are a friendly healthcare insurance assistant.
Generate a natural, empathetic response based on the user's question and data from our knowledge graph.

User Question: "{user_query}"
Intent: {intent}

Data from Knowledge Graph:
{json.dumps(results, indent=2)}

Guidelines:
- Be friendly and professional
- Explain coverage clearly with amounts in ₹ (rupees)
- Highlight important conditions (co-pay, pre-authorization, sub-limits)
- If coverage is available, emphasize the positive
- If there are restrictions, explain them clearly
- Keep response concise (2-4 sentences)
- End with an offer to help with more questions

Generate response:"""
        
        try:
            response = self.llm.invoke([HumanMessage(content=prompt)])
            state["final_response"] = response.content.strip()
            print(f"{Fore.GREEN}[Synthesizer] Response generated successfully")
        
        except Exception as e:
            print(f"{Fore.RED}[Synthesizer] Error: {e}")
            # Fallback to structured response
            state["final_response"] = self._generate_fallback_response(intent, results)
        
        return state
    
    def rag_fallback_node(self, state: AgentState) -> AgentState:
        """Handle queries that don't fit structured KG queries using RAG"""
        print(f"{Fore.CYAN}[RAG Fallback] Handling general question...")
        
        user_query = state["user_query"]
        
        # Try vector store RAG first if available
        if self.vector_store:
            try:
                print(f"{Fore.CYAN}[RAG] Searching policy documents...")
                results = self.vector_store.search(user_query, n_results=3)
                
                if results:
                    # Build context from retrieved documents
                    context = "\n\n".join([
                        f"From {result['metadata'].get('filename', 'policy document')}:\n{result['document']}"
                        for result in results
                    ])
                    
                    print(f"{Fore.GREEN}[RAG] Found {len(results)} relevant policy sections")
                    
                    # Generate response with context
                    prompt = f"""You are a healthcare insurance assistant with access to policy documents.
Answer the following question using the policy information provided below.

Policy Context:
{context}

Question: "{user_query}"

Provide a clear, accurate answer based on the policy information above. If the context doesn't contain 
enough information to answer completely, say so and provide what information you can."""
                    
                    response = self.llm.invoke([HumanMessage(content=prompt)])
                    state["final_response"] = response.content.strip()
                    print(f"{Fore.GREEN}[RAG Fallback] Response generated from policy documents")
                    return state
                    
            except Exception as e:
                print(f"{Fore.YELLOW}[RAG] Vector store error: {e}, falling back to general knowledge")
        
        # Fallback to general knowledge if vector store unavailable or no results
        prompt = f"""You are a knowledgeable healthcare insurance assistant.
Answer the following question based on general healthcare insurance knowledge.

If the question requires specific policy or customer data, politely explain that you need more information.

Question: "{user_query}"

Provide a helpful, accurate response:"""
        
        try:
            response = self.llm.invoke([HumanMessage(content=prompt)])
            state["final_response"] = response.content.strip()
            print(f"{Fore.GREEN}[RAG Fallback] Response generated from general knowledge")
        
        except Exception as e:
            print(f"{Fore.RED}[RAG Fallback] Error: {e}")
            state["final_response"] = "I'm having trouble processing that question. Could you rephrase it or provide more details?"
        
        return state
    
    def hybrid_node(self, state: AgentState) -> AgentState:
        """Handle hybrid queries that need both KG and RAG"""
        print(f"{Fore.MAGENTA}[Hybrid] Executing combined KG + RAG query...")
        
        user_query = state["user_query"]
        intent = state["intent"]
        parameters = state["parameters"]
        
        # Step 1: Execute Knowledge Graph query for structured data
        print(f"{Fore.CYAN}[Hybrid] Step 1: Querying Knowledge Graph...")
        kg_results = []
        
        if not self.connector:
            print(f"{Fore.YELLOW}[Hybrid] KG connector not available, skipping KG query")
        else:
            try:
                # Generate and execute KG query based on intent
                city = parameters.get('city', '')
                min_discount = parameters.get('min_discount', 0)
                
                if intent in ["hospital_finder", "coverage_check", "policy_utilization"] and city:
                    # Query for hospitals in specified city with optional discount filter
                    if min_discount:
                        cypher_query = f"""
                        MATCH (h:Hospital)-[net:IN_NETWORK]-(p:Policy)
                        WHERE toLower(h.city) = toLower($city) AND net.discount_pct >= $min_discount
                        RETURN DISTINCT h.name as hospital, h.city as city, net.discount_pct as discount, 
                               h.tier as tier, h.cashless_enabled as cashless
                        ORDER BY net.discount_pct DESC
                        LIMIT 10
                        """
                        cypher_params = {"city": city, "min_discount": int(min_discount)}
                    else:
                        cypher_query = f"""
                        MATCH (h:Hospital)-[net:IN_NETWORK]-(p:Policy)
                        WHERE toLower(h.city) = toLower($city)
                        RETURN DISTINCT h.name as hospital, h.city as city, net.discount_pct as discount, 
                               h.tier as tier, h.cashless_enabled as cashless
                        ORDER BY net.discount_pct DESC
                        LIMIT 10
                        """
                        cypher_params = {"city": city}
                    
                    kg_results = self.connector.execute_query(cypher_query, cypher_params)
                    print(f"{Fore.GREEN}[Hybrid] Found {len(kg_results)} hospitals in {city} from KG")
            
            except Exception as e:
                print(f"{Fore.YELLOW}[Hybrid] KG query error: {e}")
        
        # Step 2: Execute RAG query for policy information
        print(f"{Fore.CYAN}[Hybrid] Step 2: Searching policy documents...")
        rag_context = ""
        
        if self.vector_store:
            try:
                # Extract policy-related keywords from query
                policy_query = user_query
                if "policy" not in user_query.lower():
                    # Add context for better RAG search
                    treatment = parameters.get('treatment_name', '')
                    if treatment:
                        policy_query = f"What is the coverage policy for {treatment}?"
                
                rag_results = self.vector_store.search(policy_query, n_results=2)
                
                if rag_results:
                    rag_context = "\n\n".join([
                        f"{result['document']}"
                        for result in rag_results
                    ])
                    print(f"{Fore.GREEN}[Hybrid] Found {len(rag_results)} relevant policy sections")
            
            except Exception as e:
                print(f"{Fore.YELLOW}[Hybrid] RAG error: {e}")
        
        # Step 3: Synthesize combined response
        print(f"{Fore.MAGENTA}[Hybrid] Step 3: Synthesizing combined response...")
        
        # Format KG results
        kg_summary = ""
        if kg_results:
            kg_summary = f"\n\nNetwork Hospitals Found ({len(kg_results)}):\n"
            for i, r in enumerate(kg_results[:5], 1):  # Limit to top 5
                cashless = "✓ Cashless" if r.get('cashless', False) else "✗ No Cashless"
                kg_summary += f"{i}. {r['hospital']} - {r['city']}\n"
                kg_summary += f"   Tier: {r['tier']} | Discount: {r['discount']}% | {cashless}\n"
        
        # Create synthesis prompt
        prompt = f"""You are a healthcare insurance assistant providing comprehensive answers.

User Question: "{user_query}"

Knowledge Graph Data (Network Hospitals):
{kg_summary if kg_summary else "No specific hospital data found."}

Policy Information:
{rag_context if rag_context else "No specific policy details found."}

Provide a comprehensive answer that:
1. First addresses the policy coverage details (if available)
2. Then lists the specific hospitals that match the criteria (if available)
3. Combines both pieces of information naturally

Be concise but complete. Format hospital lists clearly."""
        
        try:
            response = self.llm.invoke([HumanMessage(content=prompt)])
            state["final_response"] = response.content.strip()
            state["query_results"] = kg_results
            state["rag_results"] = rag_context
            print(f"{Fore.GREEN}[Hybrid] Combined response generated successfully")
        
        except Exception as e:
            print(f"{Fore.RED}[Hybrid] Error: {e}")
            # Fallback to simple combination
            state["final_response"] = f"{rag_context}\n\n{kg_summary}" if (rag_context or kg_summary) else "I couldn't find complete information for your query."
        
        return state
    
    def escalation_node(self, state: AgentState) -> AgentState:
        """Handle escalation to human agent"""
        print(f"{Fore.YELLOW}[Escalation] Query requires human assistance")
        
        state["final_response"] = """I want to make sure you get the most accurate information for your query. 
Let me connect you with one of our insurance specialists who can provide personalized assistance. 

Would you like me to:
1. Transfer you to a live agent
2. Schedule a callback
3. Try rephrasing your question

Please let me know how you'd like to proceed."""
        
        state["requires_escalation"] = True
        return state
    
    # ========== ROUTING FUNCTIONS ==========
    
    def route_after_classification(self, state: AgentState) -> str:
        """Route based on classification confidence"""
        confidence = state.get("confidence", 0)
        intent = state.get("intent", "")
        needs_hybrid = state.get("needs_hybrid", False)
        
        # Handle explicit escalation requests
        if intent == "escalation":
            print(f"{Fore.YELLOW}[Router] Explicit escalation request, routing to escalation")
            return "escalation"
        
        # Handle hybrid queries (needs both KG and RAG)
        if needs_hybrid:
            print(f"{Fore.MAGENTA}[Router] Hybrid query detected, routing to hybrid node")
            return "hybrid"
        
        if confidence < CONFIDENCE_THRESHOLD:
            print(f"{Fore.YELLOW}[Router] Low confidence, routing to RAG fallback")
            return "rag_fallback"
        
        # General questions and policy queries don't need customer ID - route to RAG
        if intent in ["general_question", "greeting", "policy_utilization", "coverage_check"]:
            print(f"{Fore.CYAN}[Router] General/policy question, routing to RAG")
            return "rag_fallback"
        
        # Customer-specific queries need customer ID
        if not state.get("customer_id") and intent not in ["general_question", "greeting", "policy_utilization", "coverage_check"]:
            print(f"{Fore.YELLOW}[Router] Customer ID required, routing to escalation")
            return "escalation"
        
        return "query_planner"
    
    def route_after_planning(self, state: AgentState) -> str:
        """Route based on query planning success"""
        if state.get("error"):
            print(f"{Fore.YELLOW}[Router] Planning error, routing to RAG fallback")
            return "rag_fallback"
        
        if not state.get("cypher_query"):
            print(f"{Fore.YELLOW}[Router] No query generated, routing to RAG fallback")
            return "rag_fallback"
        
        return "kg_executor"
    
    def route_after_execution(self, state: AgentState) -> str:
        """Route based on execution results"""
        if state.get("error"):
            attempt_count = state.get("attempt_count", 0)
            
            if attempt_count < 2:
                print(f"{Fore.YELLOW}[Router] Execution error, retrying with correction")
                return "query_planner"
            else:
                print(f"{Fore.YELLOW}[Router] Max retries reached, routing to RAG fallback")
                return "rag_fallback"
        
        results = state.get("query_results", [])
        if not results:
            print(f"{Fore.YELLOW}[Router] No results, routing to RAG fallback")
            return "rag_fallback"
        
        return "synthesizer"
    
    # ========== HELPER FUNCTIONS ==========
    
    def _map_treatment_name_to_code(self, treatment_name: str) -> str:
        """Map treatment name to ICD-10 code"""
        mapping = {
            'diabetes': 'E11',
            'hypertension': 'I10',
            'blood pressure': 'I10',
            'knee': 'M17',
            'surgery': 'M17',
            'asthma': 'J45'
        }
        
        for keyword, code in mapping.items():
            if keyword in treatment_name:
                return code
        
        return None
    
    def _generate_fallback_response(self, intent: str, results: list) -> str:
        """Generate structured fallback response"""
        if not results:
            return "I couldn't find information matching your query."
        
        if intent == "coverage_check" and results:
            r = results[0]
            return f"Your {r.get('policy_plan')} policy covers {r.get('treatment_name')} at {r.get('hospital_name')}. " \
                   f"Sub-limit: ₹{r.get('sub_limit'):,}, Co-pay: {r.get('copay')}%."
        
        elif intent == "hospital_finder" and results:
            hospitals = [f"{r['hospital_name']} ({r['discount']}% discount)" for r in results[:3]]
            return f"Here are your in-network hospitals: {', '.join(hospitals)}."
        
        return f"Found {len(results)} result(s) for your query."
    
    # ========== PUBLIC API ==========
    
    def process_query(self, user_query: str, customer_id: Optional[str] = None, session_id: Optional[str] = None) -> str:
        """
        Process a user query through the agent workflow
        
        Args:
            user_query: The user's question
            customer_id: Optional customer ID
            session_id: Optional session ID for conversation memory
            
        Returns:
            Agent's response
        """
        # Get conversation context if session_id provided
        conversation_context = ""
        if session_id and self.memory:
            conversation_context = self.memory.get_context_string(session_id, last_n=4)
            if conversation_context:
                print(f"{Fore.CYAN}[Memory] Retrieved conversation context ({session_id})")
        
        initial_state = {
            "messages": [],
            "user_query": user_query,
            "customer_id": customer_id,
            "intent": "",
            "confidence": 0.0,
            "parameters": {},
            "cypher_query": "",
            "cypher_params": {},
            "query_results": [],
            "final_response": "",
            "error": "",
            "requires_escalation": False,
            "attempt_count": 0
        }
        
        print(f"\n{Fore.CYAN}{'='*70}")
        print(f"{Fore.CYAN}Processing Query: {user_query}")
        print(f"{Fore.CYAN}{'='*70}\n")
        
        final_state = self.workflow.invoke(initial_state)
        response = final_state["final_response"]
        
        # Store in conversation memory if session_id provided
        if session_id and self.memory:
            # Create session if it doesn't exist
            if session_id not in self.memory.get_active_sessions():
                self.memory.create_session(session_id, customer_id)
            
            # Add messages to history
            self.memory.add_message(session_id, "user", user_query, 
                                   metadata={'intent': final_state.get('intent'),
                                           'confidence': final_state.get('confidence')})
            self.memory.add_message(session_id, "assistant", response)
            print(f"{Fore.CYAN}[Memory] Saved to conversation history")
        
        print(f"\n{Fore.GREEN}{'='*70}")
        print(f"{Fore.GREEN}Query Processed Successfully")
        print(f"{Fore.GREEN}{'='*70}\n")
        
        return response


def main():
    """Interactive agent CLI"""
    print(f"{Fore.CYAN}{'='*70}")
    print(f"{Fore.CYAN}  🤖 MedAssist Agentic System - LangGraph Orchestration")
    print(f"{Fore.CYAN}  Powered by LangGraph + Neo4j + Gemini 2.0 Flash")
    print(f"{Fore.CYAN}{'='*70}\n")
    
    agent = MedAssistAgent()
    
    print("Connecting to knowledge graph...")
    if not agent.connect():
        print(f"{Fore.RED}Failed to connect to Neo4j. Exiting.")
        return
    
    print(f"{Fore.GREEN}✓ Connected!\n")
    
    # Get customer ID
    customer_id = input("Enter your Customer ID (or press Enter to skip): ").strip()
    if customer_id:
        print(f"{Fore.GREEN}✓ Customer ID set: {customer_id}\n")
    
    print(f"{Fore.YELLOW}Type your questions or 'quit' to exit\n")
    
    try:
        while True:
            user_input = input(f"{Fore.WHITE}You: ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() in ['quit', 'exit', 'bye']:
                print(f"\n{Fore.CYAN}Goodbye! 👋\n")
                break
            
            # Process query through agent workflow
            response = agent.process_query(user_input, customer_id)
            
            print(f"\n{Fore.GREEN}🤖 MedAssist AI: {response}\n")
    
    except KeyboardInterrupt:
        print(f"\n\n{Fore.YELLOW}Interrupted. Goodbye! 👋\n")
    
    finally:
        agent.close()


if __name__ == "__main__":
    main()
