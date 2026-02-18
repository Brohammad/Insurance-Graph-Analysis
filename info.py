#!/usr/bin/env python3
"""
MedAssist Knowledge Graph - Project Information
Quick reference for all commands and features
"""
from colorama import Fore, Style, init

init(autoreset=True)

BANNER = f"""
{Fore.CYAN}{'='*70}
{Fore.CYAN}  MedAssist Healthcare Insurance - Knowledge Graph System
{Fore.CYAN}  Case Study: Building an Agentic Customer Support System
{Fore.CYAN}{'='*70}
"""

PROJECT_INFO = f"""
{Fore.YELLOW}📊 PROJECT OVERVIEW{Fore.RESET}
  Technology:  Neo4j (Knowledge Graph) + LangGraph + Gemini 2.0 Flash
  Domain:      Healthcare Insurance (India)
  Status:      Phase 1 Complete - Knowledge Graph Operational
  
{Fore.YELLOW}📁 PROJECT STRUCTURE{Fore.RESET}
  Configuration:
    • .env                  - Environment variables (Neo4j + Gemini credentials)
    • config.py             - Configuration loader with validation
    • requirements.txt      - Python dependencies
  
  Knowledge Graph:
    • schema.py             - Graph schema (6 nodes, 8 relationships)
    • neo4j_connector.py    - Database connection manager
    • queries.py            - Reusable Cypher query library
    • seed_data.py          - Sample data generator
  
  Application:
    • ingest.py             - Data ingestion pipeline
    • test_queries.py       - Test suite (8 multi-hop queries)
    • main.py               - Interactive CLI application
  
  Documentation:
    • README.md             - Complete project documentation
    • PROJECT_SUMMARY.md    - Implementation summary
    • start.sh              - Quick start script

{Fore.YELLOW}🚀 QUICK START COMMANDS{Fore.RESET}
  
  {Fore.GREEN}🤖 NEW: AI Chatbot (Recommended):{Fore.RESET}
     python chatbot.py
     
     Features:
     • Natural language conversations
     • Ask questions in plain English
     • Intelligent intent detection
     • Zero hallucination - all answers from KG
     • Personalized for your customer ID
  
  {Fore.GREEN}1. Initialize Database (First Time Setup):{Fore.RESET}
     python ingest.py
     
     What it does:
     • Waits 60 seconds for Neo4j Aura to be ready
     • Creates schema constraints and indexes
     • Generates and ingests sample data
     • Creates relationships
     • Shows statistics
  
  {Fore.GREEN}2. Run Test Queries:{Fore.RESET}
     python test_queries.py
     
     Tests performed:
     ✓ Simple coverage check
     ✓ Complex multi-hop query (case study example)
     ✓ Claim history analysis
     ✓ Network hospital finder
     ✓ Policy utilization
     ✓ Alternative hospital recommendations
     ✓ Medication coverage
     ✓ Treatment medication lookup
  
  {Fore.GREEN}3. Launch Interactive Application:{Fore.RESET}
     python main.py
     
     Features:
     • Database initialization
     • Coverage checks
     • Hospital finder
     • Claim history viewer
     • Policy utilization
     • Medication coverage
     • Statistics dashboard

{Fore.YELLOW}📊 SAMPLE DATA{Fore.RESET}
  After initialization, you'll have:
  • 10 Customers (with realistic Indian names)
  • 5 Policies (Bronze to Diamond tiers)
  • 25 Hospitals (across 10 Indian cities)
  • 10 Treatments (diabetes, knee surgery, etc.)
  • 8 Medications (Metformin, Insulin, etc.)
  • 15 Claims (various statuses)
  • ~500 Relationships

{Fore.YELLOW}🔍 EXAMPLE QUERIES{Fore.RESET}
  
  {Fore.CYAN}Check Coverage:{Fore.RESET}
    Customer: CUST0001
    Treatment: E11 (Diabetes)
    Hospital: HOSP0001 (Apollo Bangalore)
  
  {Fore.CYAN}Complex Multi-Hop:{Fore.RESET}
    "Is Metformin covered under cashless at Apollo for CUST0001?"
    → Traverses 5 entities in one query!
  
  {Fore.CYAN}Alternative Hospitals:{Fore.RESET}
    "Claim rejected at Fortis Mumbai. Find alternatives for knee surgery."
    → Returns in-network hospitals with coverage details

{Fore.YELLOW}📈 CASE STUDY RESULTS{Fore.RESET}
  Knowledge Graphs vs. RAG-Only:
  • Multi-hop accuracy:     62% → 94%
  • Response time:          4.2s → 3.1s
  • First-contact resolution: 41% → 73%
  • Hallucinated info:      12% → <1%

{Fore.YELLOW}🔐 CREDENTIALS{Fore.RESET}
  Neo4j Aura:
    URI:      neo4j+s://9ab402cc.databases.neo4j.io
    Database: neo4j
    (Password in .env file)
  
  Gemini API:
    Model: gemini-2.0-flash-exp
    (API key in .env file)

{Fore.YELLOW}🎯 NEXT STEPS{Fore.RESET}
  Phase 2: Add Agentic Layer
  ☐ Text-to-Cypher agent (natural language → Cypher)
  ☐ LangGraph StateGraph (multi-agent orchestration)
  ☐ RAG fallback (for unstructured queries)
  ☐ Confidence-based escalation
  ☐ Feedback loop for query correction

{Fore.YELLOW}📚 USEFUL COMMANDS{Fore.RESET}
  
  Test configuration:
    python config.py
  
  Generate sample data:
    python seed_data.py
  
  Check database stats:
    python -c "from neo4j_connector import Neo4jConnector; c=Neo4jConnector(); c.connect(wait_time=5); print(c.get_node_count()); c.close()"
  
  Quick start:
    ./start.sh

{Fore.YELLOW}🐛 TROUBLESHOOTING{Fore.RESET}
  
  Connection issues:
    • Wait 60 seconds for Aura instance
    • Check https://console.neo4j.io
    • Verify credentials in .env
  
  Import errors:
    source .venv/bin/activate
    pip install neo4j python-dotenv colorama
  
  Empty results:
    Make sure to run: python ingest.py first

{Fore.YELLOW}📖 DOCUMENTATION{Fore.RESET}
  • README.md - Complete guide
  • PROJECT_SUMMARY.md - Implementation details
  • This script: python info.py

{Fore.CYAN}{'='*70}
{Fore.GREEN}✓ Knowledge Graph System Ready!
{Fore.CYAN}{'='*70}
"""

if __name__ == "__main__":
    print(BANNER)
    print(PROJECT_INFO)
    print(f"\n{Fore.YELLOW}Run 'python main.py' to get started!{Fore.RESET}\n")
