# MedAssist Healthcare Insurance Knowledge Graph

A production-ready healthcare insurance knowledge graph system built with **Neo4j**, **LangGraph**, and **Gemini 2.0 Flash**. This project implements the case study: "Building an Agentic Customer Support System for Healthcare Insurance" using graph-based reasoning over traditional RAG.

## 🤖 **FEATURED: LangGraph Agentic System**

**NEW: Production-ready StateGraph orchestration**
```bash
source .venv/bin/activate
python agent.py
```

Features:
- 🔄 **6-node StateGraph workflow** (Classifier → Planner → Executor → Synthesizer)
- 🎯 **Zero hallucination** - Facts from KG, LLM only formats
- 🧠 **Smart routing** - Confidence-based fallback to RAG
- 🔁 **Auto-correction** - Query retry with error fixing
- 📊 **8/8 tests passing** - Comprehensive validation

See [AGENT_GUIDE.md](AGENT_GUIDE.md) for detailed architecture guide.

## 💬 **Simple Chatbot Interface**

**For quick interactions:**
```bash
source .venv/bin/activate
python chatbot.py
```

Features:
- 💬 Natural language conversations
- 🧠 Intelligent intent detection with Gemini 2.0 Flash  
- 🔍 Multi-hop reasoning across relationships
- 📊 Personalized responses based on customer data

See [CHATBOT_GUIDE.md](CHATBOT_GUIDE.md) for detailed usage guide.

## 🎯 Project Overview

This system demonstrates how knowledge graphs enable **multi-hop relational reasoning** for complex healthcare insurance queries that traditional RAG systems struggle with. It models customers, policies, hospitals, treatments, medications, and claims as interconnected graph entities.

### Why Knowledge Graphs?

Healthcare insurance queries are inherently **relational**:
- "Is my diabetes medication covered under cashless at Apollo Bangalore?"
- "I had knee surgery at Fortis Mumbai. My claim was partially rejected. Can I get the remaining amount covered if I go to Apollo instead?"

These queries require traversing multiple connected facts—something vector search alone cannot reliably handle.

## 📊 Case Study Results

| Metric | RAG-Only | KG + LangGraph Agent |
|--------|----------|---------------------|
| Multi-hop query accuracy | 62% | 94% |
| Average response time | 4.2s | 3.1s |
| Customer satisfaction | 3.2/5 | 4.4/5 |
| Escalation to human | 45% | 18% |
| First-contact resolution | 41% | 73% |
| Hallucinated claims info | 12% | <1% |

## 🏗️ Architecture

### Knowledge Graph Schema

**Entities (Nodes):**
- `Customer`: {id, name, age, city, pre_existing, phone, email}
- `Policy`: {id, plan_type, sum_insured, copay_pct, renewal_date, premium}
- `Hospital`: {id, name, city, tier, cashless_enabled, specialties}
- `Treatment`: {code, category, name, avg_cost, sub_limit, requires_preauth}
- `Medication`: {id, name, generic, formulary_tier, requires_preauth}
- `Claim`: {id, status, amount, approved_amount, date, rejection_reason}

**Relationships (Edges):**
- `(Customer)-[:HAS_POLICY]->(Policy)`
- `(Policy)-[:COVERS]->(Treatment)`
- `(Policy)-[:IN_NETWORK]->(Hospital)`
- `(Policy)-[:IN_FORMULARY]->(Medication)`
- `(Medication)-[:TREATS]->(Treatment)`
- `(Customer)-[:FILED_CLAIM]->(Claim)`
- `(Claim)-[:AT_HOSPITAL]->(Hospital)`
- `(Claim)-[:FOR_TREATMENT]->(Treatment)`

### Tech Stack

- **Graph Database**: Neo4j Aura (Cloud)
- **Orchestration**: LangGraph (for agentic workflows)
- **LLM**: Google Gemini 2.0 Flash
- **Language**: Python 3.8+
- **Libraries**: neo4j-driver, langchain, python-dotenv, colorama

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Neo4j Aura account (free tier available)
- Google Gemini API key

### Installation

1. **Clone the repository:**
```bash
cd /home/labuser/Desktop/graphbased
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Configure environment:**
The `.env` file is already configured with your Neo4j Aura credentials:
```
NEO4J_URI=neo4j+s://9ab402cc.databases.neo4j.io
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=***
GOOGLE_API_KEY=***
```

### Usage

**⚠️ IMPORTANT: Always activate the virtual environment first!**

```bash
source .venv/bin/activate
```

#### Quick Commands

**Check System Status:**
```bash
./status.sh
```
Shows database statistics and available commands.

**Option 1: Initialize Database (First Time)**

```bash
source .venv/bin/activate
python ingest.py
```

This will:
- Wait 60 seconds for Neo4j Aura to be ready
- Create schema constraints and indexes
- Generate 10 customers, 5 policies, 25 hospitals, 10 treatments, 8 medications
- Create 15 sample claims
- Establish all relationships (~248 relationships)

**Expected Output:**
- ✅ 73 nodes created
- ✅ 248 relationships created
- ✅ 6 constraints, 6 indexes

**Option 2: Run Test Queries (Validate KG)**

```bash
source .venv/bin/activate
python test_queries.py
```

Runs 8 comprehensive test queries:
- ✅ Simple coverage checks
- ✅ Complex multi-hop queries (case study example)
- ✅ Claim history analysis
- ✅ Network hospital finder
- ✅ Policy utilization
- ✅ Alternative hospital recommendations
- ✅ Medication coverage
- ✅ Treatment medication lookup

**Option 3: Interactive CLI Application**

```bash
source .venv/bin/activate
python main.py
```

Interactive menu with options:
1. Initialize Database
2. Run Test Queries  
3. Check coverage for treatments at hospitals
4. Find in-network hospitals
5. View claim history
6. Check policy utilization
7. Check medication coverage
8. View database statistics
9. Clear database (caution!)

**Option 4: View Project Information**

```bash
source .venv/bin/activate
python info.py
```

Displays comprehensive project documentation and quick reference.

## 📂 Project Structure

```
/home/labuser/Desktop/graphbased/
├── .env                    # Environment configuration (Neo4j + Gemini credentials)
├── requirements.txt        # Python dependencies
├── config.py              # Configuration loader and validator
├── schema.py              # Knowledge graph schema definition
├── neo4j_connector.py     # Neo4j connection manager with retry logic
├── queries.py             # Reusable Cypher query builders
├── seed_data.py           # Sample data generator (customers, policies, etc.)
├── ingest.py              # Data ingestion script
├── test_queries.py        # Test suite for multi-hop queries
└── main.py                # Interactive CLI application
```

## 🔍 Example Queries

### 1. Simple Coverage Check
```python
from queries import QueryBuilder

query = QueryBuilder.check_coverage("CUST0001", "E11", "HOSP0001")
# Returns: policy plan, treatment details, hospital tier, estimated cost
```

### 2. Complex Multi-Hop Query (Case Study Example)
```python
query = QueryBuilder.complex_coverage_check("CUST0001", "Metformin", "Apollo")
# Traverses: Customer → Policy → Treatment ← Medication
#           Policy → Hospital (with cashless check)
```

### 3. Alternative Hospital Finder
```python
query = QueryBuilder.find_alternative_hospitals("CUST0001", "M17", "HOSP0002")
# Finds alternative hospitals for knee surgery excluding Fortis Mumbai
```

## 🧪 Testing

Run the comprehensive test suite:

```bash
python test_queries.py
```

**Test Coverage:**
- ✅ Simple coverage checks
- ✅ Multi-hop traversals (5+ nodes)
- ✅ Claim history with rejection analysis
- ✅ Network hospital discovery
- ✅ Policy utilization calculations
- ✅ Medication formulary checks
- ✅ Alternative hospital recommendations

## 🎓 Case Study Learning Points

### 1. Knowledge Graphs vs. RAG
- **KG Strength**: Deterministic, traversable relationships
- **RAG Strength**: Unstructured context, semantic search
- **Best Practice**: Use KGs for structured reasoning, RAG for context augmentation

### 2. Multi-Hop Reasoning
A query like "Is Metformin covered under cashless at Apollo?" requires:
1. Customer → Policy (which plan?)
2. Policy → Treatment (what does Metformin treat?)
3. Medication → Treatment (relationship)
4. Policy → Hospital (is Apollo in-network?)
5. Check cashless eligibility

**One Cypher query** = 5 relationship traversals. RAG would need multiple retrieval rounds + LLM inference.

### 3. Agentic Architecture
The LangGraph agent will use this KG as **structured memory**:
- **Classifier**: Detect intent (coverage check, claim status, etc.)
- **Query Planner**: Generate Cypher from natural language
- **KG Executor**: Execute queries with retry logic
- **RAG Fallback**: Handle unstructured questions
- **Synthesizer**: Generate empathetic customer responses

## 🛠️ Next Steps: Adding the Agent Layer

To complete the case study implementation:

1. **Text-to-Cypher Agent** (LLM converts natural language → Cypher)
2. **LangGraph StateGraph** (orchestrates multi-agent workflow)
3. **RAG Fallback** (ChromaDB for policy PDFs)
4. **Confidence-based Escalation** (human handoff when uncertain)
5. **Feedback Loop** (auto-correct failed Cypher queries)

## 📊 Database Statistics

After initialization, you'll have:
- **Nodes**: ~75 total (10 customers, 5 policies, 30+ hospitals, etc.)
- **Relationships**: ~500+ connections
- **Constraints**: 6 unique constraints on IDs
- **Indexes**: 6 indexes for fast lookups

## 🐛 Troubleshooting

### Connection Issues
The script waits 60 seconds for Neo4j Aura to be ready. If connection fails:
1. Verify credentials in `.env`
2. Check Neo4j Aura instance status at https://console.neo4j.io
3. Ensure your IP is not blocked (Aura free tier has no IP restrictions)

### Import Errors
If you see "Import neo4j could not be resolved":
```bash
pip install --upgrade neo4j
```

### Query Failures
Check that data has been ingested:
```bash
python -c "from neo4j_connector import Neo4jConnector; c = Neo4jConnector(); c.connect(wait_time=5); print(c.get_node_count()); c.close()"
```

## 📝 License

MIT License - Feel free to use this for learning and commercial projects.

## 🙏 Acknowledgments

This project implements the MedAssist case study from the **"Knowledge Graphs + LangGraph"** curriculum, demonstrating production-ready patterns for agentic AI systems in healthcare.

---

**Built with ❤️ for the AI Agent Masterclass**
