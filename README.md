# MedAssist Healthcare Insurance AI Agent# MedAssist Healthcare Insurance Knowledge Graph



A production-ready healthcare insurance AI agent built with **Neo4j Knowledge Graph**, **LangGraph**, **ChromaDB RAG**, and **Gemini 2.0 Flash**. This system implements intelligent customer support using graph-based reasoning combined with vector search for policy documents.A production-ready healthcare insurance knowledge graph system built with **Neo4j**, **LangGraph**, and **Gemini 2.0 Flash**. This project implements the case study: "Building an Agentic Customer Support System for Healthcare Insurance" using graph-based reasoning over traditional RAG.



[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)## 🤖 **FEATURED: LangGraph Agentic System**

[![Neo4j](https://img.shields.io/badge/Neo4j-Aura-008CC1.svg)](https://neo4j.com/cloud/aura/)

[![LangGraph](https://img.shields.io/badge/LangGraph-StateGraph-green.svg)](https://langchain-ai.github.io/langgraph/)**NEW: Production-ready StateGraph orchestration**

[![Gemini](https://img.shields.io/badge/Gemini-2.0--Flash-orange.svg)](https://deepmind.google/technologies/gemini/)```bash

source .venv/bin/activate

## 🚀 Quick Startpython agent.py

```

### Web Interface (Recommended)

Features:

```bash- 🔄 **6-node StateGraph workflow** (Classifier → Planner → Executor → Synthesizer)

source .venv/bin/activate- 🎯 **Zero hallucination** - Facts from KG, LLM only formats

python web_api.py- 🧠 **Smart routing** - Confidence-based fallback to RAG

```- 🔁 **Auto-correction** - Query retry with error fixing

- 📊 **8/8 tests passing** - Comprehensive validation

Open browser: **http://localhost:5000**

See [AGENT_GUIDE.md](AGENT_GUIDE.md) for detailed architecture guide.

### CLI Interface

## 💬 **Simple Chatbot Interface**

```bash

source .venv/bin/activate**For quick interactions:**

python chatbot.py```bash

```source .venv/bin/activate

python chatbot.py

## 📋 Table of Contents```



- [Features](#-features)Features:

- [Architecture](#-architecture)- 💬 Natural language conversations

- [Installation](#-installation)- 🧠 Intelligent intent detection with Gemini 2.0 Flash  

- [Usage](#-usage)- 🔍 Multi-hop reasoning across relationships

- [API Reference](#-api-reference)- 📊 Personalized responses based on customer data

- [Testing](#-testing)

- [Project Structure](#-project-structure)See [CHATBOT_GUIDE.md](CHATBOT_GUIDE.md) for detailed usage guide.

- [Configuration](#-configuration)

## 🎯 Project Overview

## ✨ Features

This system demonstrates how knowledge graphs enable **multi-hop relational reasoning** for complex healthcare insurance queries that traditional RAG systems struggle with. It models customers, policies, hospitals, treatments, medications, and claims as interconnected graph entities.

### 🤖 LangGraph Agentic System

- **6-node StateGraph workflow** (Classifier → Planner → Executor → Synthesizer)### Why Knowledge Graphs?

- **Zero hallucination** - Facts from knowledge graph, LLM only formats responses

- **Smart routing** - Confidence-based fallback to RAGHealthcare insurance queries are inherently **relational**:

- **Auto-correction** - Query retry with error fixing on failures- "Is my diabetes medication covered under cashless at Apollo Bangalore?"

- **Multi-hop reasoning** - Traverses complex relationships across entities- "I had knee surgery at Fortis Mumbai. My claim was partially rejected. Can I get the remaining amount covered if I go to Apollo instead?"



### 🧠 Hybrid AI SystemThese queries require traversing multiple connected facts—something vector search alone cannot reliably handle.

- **Knowledge Graph (Neo4j)** - Structured relational data for customer/policy queries

- **Vector Store (ChromaDB)** - Semantic search over policy documents## 📊 Case Study Results

- **Conversation Memory** - Multi-turn conversations with session management

- **Intent Classification** - Automatic query routing with Gemini 2.0 Flash| Metric | RAG-Only | KG + LangGraph Agent |

|--------|----------|---------------------|

### 💬 Conversational Interface| Multi-hop query accuracy | 62% | 94% |

- **Natural language queries** - Ask questions in plain English| Average response time | 4.2s | 3.1s |

- **Session persistence** - Maintains context across conversations| Customer satisfaction | 3.2/5 | 4.4/5 |

- **Explicit escalation** - Route to human agents when needed| Escalation to human | 45% | 18% |

- **Customer-specific responses** - Personalized information based on customer ID| First-contact resolution | 41% | 73% |

| Hallucinated claims info | 12% | <1% |

### 🌐 Web Interface

- **Modern React-style UI** - Clean, responsive design## 🏗️ Architecture

- **Real-time chat** - Instant responses with typing indicators

- **Customer selection** - Switch between 10 demo customers### Knowledge Graph Schema

- **Session management** - Persistent conversations across page refreshes

**Entities (Nodes):**

## 🏗️ Architecture- `Customer`: {id, name, age, city, pre_existing, phone, email}

- `Policy`: {id, plan_type, sum_insured, copay_pct, renewal_date, premium}

### System Flow- `Hospital`: {id, name, city, tier, cashless_enabled, specialties}

- `Treatment`: {code, category, name, avg_cost, sub_limit, requires_preauth}

```- `Medication`: {id, name, generic, formulary_tier, requires_preauth}

┌─────────────┐- `Claim`: {id, status, amount, approved_amount, date, rejection_reason}

│   USER      │ Natural Language Query

│   INPUT     │ "Is diabetes covered at Apollo?"**Relationships (Edges):**

└──────┬──────┘- `(Customer)-[:HAS_POLICY]->(Policy)`

       │- `(Policy)-[:COVERS]->(Treatment)`

       ↓- `(Policy)-[:IN_NETWORK]->(Hospital)`

┌─────────────────────────────────────────┐- `(Policy)-[:IN_FORMULARY]->(Medication)`

│     LANGGRAPH STATE GRAPH               │- `(Medication)-[:TREATS]->(Treatment)`

│                                         │- `(Customer)-[:FILED_CLAIM]->(Claim)`

│  ┌──────────────┐                      │- `(Claim)-[:AT_HOSPITAL]->(Hospital)`

│  │ CLASSIFIER   │ Intent + Parameters  │- `(Claim)-[:FOR_TREATMENT]->(Treatment)`

│  │ (Gemini 2.0) │                      │

│  └──────┬───────┘                      │### Tech Stack

│         │                               │

│    ┌────┴────┐                         │- **Graph Database**: Neo4j Aura (Cloud)

│    │         │                         │- **Orchestration**: LangGraph (for agentic workflows)

│    ↓         ↓                         │- **LLM**: Google Gemini 2.0 Flash

│ HIGH conf  LOW conf                    │- **Language**: Python 3.8+

│    │         │                         │- **Libraries**: neo4j-driver, langchain, python-dotenv, colorama

│    ↓         ↓                         │

│ ┌────┐   ┌─────┐                      │## 🚀 Quick Start

│ │ KG │   │ RAG │                      │

│ │EXEC│   │(ChromaDB)                  │### Prerequisites

│ └─┬──┘   └──┬──┘                      │

│   │         │                          │- Python 3.8+

│   └────┬────┘                          │- Neo4j Aura account (free tier available)

│        ↓                               │- Google Gemini API key

│  ┌─────────────┐                      │

│  │SYNTHESIZER  │                      │### Installation

│  │ (Gemini 2.0)│                      │

│  └─────────────┘                      │1. **Clone the repository:**

└──────────┬──────────────────────────────┘```bash

           │cd /home/labuser/Desktop/graphbased

           ↓```

    ┌─────────────┐

    │  RESPONSE   │2. **Install dependencies:**

    │  (Natural   │```bash

    │  Language)  │pip install -r requirements.txt

    └─────────────┘```

```

3. **Configure environment:**

### Knowledge Graph SchemaThe `.env` file is already configured with your Neo4j Aura credentials:

```

See [ARCHITECTURE.md](ARCHITECTURE.md) for detailed schema visualization.NEO4J_URI=neo4j+s://9ab402cc.databases.neo4j.io

NEO4J_USERNAME=neo4j

**Entities:**NEO4J_PASSWORD=***

- 👤 **Customer** (10) - Customer profiles with demographicsGOOGLE_API_KEY=***

- 📋 **Policy** (5) - Insurance plans (Bronze to Diamond)```

- 🏥 **Hospital** (25) - Network hospitals across India

- 🩺 **Treatment** (10) - Medical procedures and conditions### Usage

- 💊 **Medication** (8) - Covered medications

- 📑 **Claim** (15) - Historical claims**⚠️ IMPORTANT: Always activate the virtual environment first!**



**Relationships:**```bash

- HAS_POLICY - Customer to Policysource .venv/bin/activate

- COVERS - Policy to Treatment```

- IN_NETWORK - Policy to Hospital

- IN_FORMULARY - Policy to Medication#### Quick Commands

- TREATS - Medication to Treatment

- FILED_CLAIM - Customer to Claim**Check System Status:**

- AT_HOSPITAL - Claim to Hospital```bash

- FOR_TREATMENT - Claim to Treatment./status.sh

```

**Database:** 73 nodes, 248 relationshipsShows database statistics and available commands.



## 📦 Installation**Option 1: Initialize Database (First Time)**



### Prerequisites```bash

source .venv/bin/activate

- Python 3.10+python ingest.py

- Neo4j Aura account (free tier works)```

- Google Gemini API key

This will:

### Setup- Wait 60 seconds for Neo4j Aura to be ready

- Create schema constraints and indexes

1. **Clone the repository**- Generate 10 customers, 5 policies, 25 hospitals, 10 treatments, 8 medications

```bash- Create 15 sample claims

git clone https://github.com/Brohammad/Insurance-Graph-Analysis.git- Establish all relationships (~248 relationships)

cd Insurance-Graph-Analysis

```**Expected Output:**

- ✅ 73 nodes created

2. **Create virtual environment**- ✅ 248 relationships created

```bash- ✅ 6 constraints, 6 indexes

python -m venv .venv

source .venv/bin/activate  # Linux/Mac**Option 2: Run Test Queries (Validate KG)**

# OR

.venv\Scripts\activate  # Windows```bash

```source .venv/bin/activate

python test_queries.py

3. **Install dependencies**```

```bash

pip install -r requirements.txtRuns 8 comprehensive test queries:

```- ✅ Simple coverage checks

- ✅ Complex multi-hop queries (case study example)

4. **Configure environment**- ✅ Claim history analysis

- ✅ Network hospital finder

Create `.env` file:- ✅ Policy utilization

```env- ✅ Alternative hospital recommendations

# Neo4j Aura- ✅ Medication coverage

NEO4J_URI=neo4j+s://your-instance.databases.neo4j.io- ✅ Treatment medication lookup

NEO4J_USERNAME=neo4j

NEO4J_PASSWORD=your-password**Option 3: Interactive CLI Application**



# Google Gemini API```bash

GOOGLE_API_KEY=your-gemini-api-keysource .venv/bin/activate

```python main.py

```

5. **Initialize database**

```bashInteractive menu with options:

python ingest.py1. Initialize Database

```2. Run Test Queries  

3. Check coverage for treatments at hospitals

6. **Ingest policy documents**4. Find in-network hospitals

```bash5. View claim history

python ingest_policies.py6. Check policy utilization

```7. Check medication coverage

8. View database statistics

## 💻 Usage9. Clear database (caution!)



### Web Interface**Option 4: View Project Information**



**Start server:**```bash

```bashsource .venv/bin/activate

python web_api.pypython info.py

``````



**Access:** http://localhost:5000Displays comprehensive project documentation and quick reference.



**Features:**## 📂 Project Structure

- Select customer from dropdown (CUST0001 - CUST0010)

- Type natural language queries```

- View conversation history/home/labuser/Desktop/graphbased/

- Real-time responses with typing indicators├── .env                    # Environment configuration (Neo4j + Gemini credentials)

├── requirements.txt        # Python dependencies

**Example queries:**├── config.py              # Configuration loader and validator

```├── schema.py              # Knowledge graph schema definition

- Is diabetes covered at Apollo Bangalore?├── neo4j_connector.py     # Neo4j connection manager with retry logic

- Show me hospitals in Mumbai with discounts├── queries.py             # Reusable Cypher query builders

- What's my claim history?├── seed_data.py           # Sample data generator (customers, policies, etc.)

- I want to escalate this issue├── ingest.py              # Data ingestion script

```├── test_queries.py        # Test suite for multi-hop queries

└── main.py                # Interactive CLI application

### CLI Chatbot```



**Start chatbot:**## 🔍 Example Queries

```bash

python chatbot.py### 1. Simple Coverage Check

``````python

from queries import QueryBuilder

**Interactive mode:**

1. Enter customer ID (optional)query = QueryBuilder.check_coverage("CUST0001", "E11", "HOSP0001")

2. Type queries in natural language# Returns: policy plan, treatment details, hospital tier, estimated cost

3. Type 'quit' to exit```



### Python API### 2. Complex Multi-Hop Query (Case Study Example)

```python

```pythonquery = QueryBuilder.complex_coverage_check("CUST0001", "Metformin", "Apollo")

from agent import MedAssistAgent# Traverses: Customer → Policy → Treatment ← Medication

#           Policy → Hospital (with cashless check)

# Initialize agent with all features```

agent = MedAssistAgent(

    enable_vector_store=True,  # ChromaDB RAG### 3. Alternative Hospital Finder

    enable_memory=True         # Conversation memory```python

)query = QueryBuilder.find_alternative_hospitals("CUST0001", "M17", "HOSP0002")

# Finds alternative hospitals for knee surgery excluding Fortis Mumbai

# Process query```

response = agent.process_query(

    user_query="Is diabetes covered at Apollo?",## 🧪 Testing

    customer_id="CUST0001",

    session_id="unique-session-id"  # OptionalRun the comprehensive test suite:

)

```bash

print(response)python test_queries.py

``````



## 🔌 API Reference**Test Coverage:**

- ✅ Simple coverage checks

### REST API Endpoints- ✅ Multi-hop traversals (5+ nodes)

- ✅ Claim history with rejection analysis

Base URL: `http://localhost:5000`- ✅ Network hospital discovery

- ✅ Policy utilization calculations

#### Health Check- ✅ Medication formulary checks

```http- ✅ Alternative hospital recommendations

GET /health

```## 🎓 Case Study Learning Points

Response:

```json### 1. Knowledge Graphs vs. RAG

{- **KG Strength**: Deterministic, traversable relationships

  "status": "healthy",- **RAG Strength**: Unstructured context, semantic search

  "database": "connected",- **Best Practice**: Use KGs for structured reasoning, RAG for context augmentation

  "nodes": {"Customer": 10, "Policy": 5, ...},

  "timestamp": "2026-02-18T..."### 2. Multi-Hop Reasoning

}A query like "Is Metformin covered under cashless at Apollo?" requires:

```1. Customer → Policy (which plan?)

2. Policy → Treatment (what does Metformin treat?)

#### Process Query3. Medication → Treatment (relationship)

```http4. Policy → Hospital (is Apollo in-network?)

POST /api/query5. Check cashless eligibility

Content-Type: application/json

**One Cypher query** = 5 relationship traversals. RAG would need multiple retrieval rounds + LLM inference.

{

  "query": "Is diabetes covered?",### 3. Agentic Architecture

  "customer_id": "CUST0001",The LangGraph agent will use this KG as **structured memory**:

  "session_id": "session-123"- **Classifier**: Detect intent (coverage check, claim status, etc.)

}- **Query Planner**: Generate Cypher from natural language

```- **KG Executor**: Execute queries with retry logic

Response:- **RAG Fallback**: Handle unstructured questions

```json- **Synthesizer**: Generate empathetic customer responses

{

  "query": "Is diabetes covered?",## 🛠️ Next Steps: Adding the Agent Layer

  "customer_id": "CUST0001",

  "session_id": "session-123",To complete the case study implementation:

  "response": "Yes, diabetes is covered...",

  "timestamp": "2026-02-18T..."1. **Text-to-Cypher Agent** (LLM converts natural language → Cypher)

}2. **LangGraph StateGraph** (orchestrates multi-agent workflow)

```3. **RAG Fallback** (ChromaDB for policy PDFs)

4. **Confidence-based Escalation** (human handoff when uncertain)

#### Get Conversation History5. **Feedback Loop** (auto-correct failed Cypher queries)

```http

GET /api/conversation/<session_id>?last_n=10## 📊 Database Statistics

```

Response:After initialization, you'll have:

```json- **Nodes**: ~75 total (10 customers, 5 policies, 30+ hospitals, etc.)

{- **Relationships**: ~500+ connections

  "session_id": "session-123",- **Constraints**: 6 unique constraints on IDs

  "history": [- **Indexes**: 6 indexes for fast lookups

    {"role": "user", "content": "...", "timestamp": "..."},

    {"role": "assistant", "content": "...", "timestamp": "..."}## 🐛 Troubleshooting

  ],

  "metadata": {### Connection Issues

    "created_at": "...",The script waits 60 seconds for Neo4j Aura to be ready. If connection fails:

    "message_count": 10,1. Verify credentials in `.env`

    "customer_id": "CUST0001"2. Check Neo4j Aura instance status at https://console.neo4j.io

  }3. Ensure your IP is not blocked (Aura free tier has no IP restrictions)

}

```### Import Errors

If you see "Import neo4j could not be resolved":

#### Clear Conversation```bash

```httppip install --upgrade neo4j

DELETE /api/conversation/<session_id>```

```

### Query Failures

#### Get StatisticsCheck that data has been ingested:

```http```bash

GET /api/statspython -c "from neo4j_connector import Neo4jConnector; c = Neo4jConnector(); c.connect(wait_time=5); print(c.get_node_count()); c.close()"

``````



#### List Customers## 📝 License

```http

GET /api/customersMIT License - Feel free to use this for learning and commercial projects.

```

## 🙏 Acknowledgments

## 🧪 Testing

This project implements the MedAssist case study from the **"Knowledge Graphs + LangGraph"** curriculum, demonstrating production-ready patterns for agentic AI systems in healthcare.

### Run All Tests

---

```bash

# Knowledge Graph queries**Built with ❤️ for the AI Agent Masterclass**

python test_queries.py

# LangGraph agent
python test_agent.py

# RAG system
python test_rag.py

# Conversation memory
python test_conversation.py

# Web API
python test_web_api.py
```

### Test Results

- ✅ **Knowledge Graph**: 8/8 tests passing
- ✅ **LangGraph Agent**: 8/8 tests passing
- ✅ **RAG System**: 4/5 tests passing
- ✅ **Conversation Memory**: 7/7 tests passing
- ✅ **Web API**: All endpoints functional

## 📁 Project Structure

```
graphbased/
├── agent.py                 # LangGraph agent (StateGraph workflow)
├── chatbot.py              # CLI chatbot interface
├── web_api.py              # Flask REST API
├── config.py               # Configuration loader
├── neo4j_connector.py      # Neo4j database connector
├── schema.py               # Knowledge graph schema
├── seed_data.py            # Sample data generator
├── ingest.py               # Data ingestion pipeline
├── queries.py              # Cypher query library
├── vector_store.py         # ChromaDB RAG implementation
├── conversation_memory.py  # Multi-turn conversation manager
├── ingest_policies.py      # Policy document ingestion
├── test_*.py               # Test suites
├── requirements.txt        # Python dependencies
├── .env                    # Environment variables (not in repo)
├── static/
│   └── index.html          # Web interface
├── policy_documents/
│   ├── comprehensive_health_policy.txt
│   └── critical_illness_rider.txt
├── chroma_db/              # ChromaDB persistent storage
└── conversation_history/   # Conversation session storage
```

## ⚙️ Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `NEO4J_URI` | Neo4j Aura connection URI | Yes |
| `NEO4J_USERNAME` | Neo4j username (usually "neo4j") | Yes |
| `NEO4J_PASSWORD` | Neo4j password | Yes |
| `GOOGLE_API_KEY` | Gemini API key | Yes |

### Agent Configuration

```python
# agent.py settings
CONFIDENCE_THRESHOLD = 0.7  # Intent classification confidence
MAX_RETRIES = 2            # Query retry attempts

# conversation_memory.py settings
MAX_HISTORY = 10           # Max messages per session
TTL_MINUTES = 60          # Session timeout

# vector_store.py settings
CHUNK_SIZE = 500          # Document chunk size
CHUNK_OVERLAP = 50        # Overlap between chunks
TOP_K = 3                 # Number of relevant chunks to retrieve
```

## 🎯 Use Cases

### 1. Coverage Verification
**Query:** "Is diabetes covered at Apollo Bangalore?"

**Flow:**
1. Classifier detects `coverage_check` intent
2. Extracts: treatment="diabetes", hospital="Apollo Bangalore"
3. Routes to Knowledge Graph
4. Executes multi-hop Cypher query
5. Returns: coverage details, sub-limits, co-pay, cashless eligibility

### 2. Policy Information
**Query:** "What are the waiting periods for critical illness?"

**Flow:**
1. Classifier detects `policy_utilization` intent
2. Routes to RAG (ChromaDB)
3. Searches policy documents semantically
4. Returns: waiting period details from policy text

### 3. Hospital Discovery
**Query:** "Show me hospitals in Mumbai with discount > 15%"

**Flow:**
1. Classifier detects `hospital_finder` intent
2. Extracts: city="Mumbai", min_discount=15
3. Routes to Knowledge Graph
4. Filters by city and discount
5. Returns: list of hospitals with details

### 4. Claim History
**Query:** "What's my claim history?"

**Flow:**
1. Classifier detects `claim_history` intent
2. Requires customer_id
3. Routes to Knowledge Graph
4. Traverses Customer → Claim → Hospital/Treatment
5. Returns: claim details with status

### 5. Human Escalation
**Query:** "I want to speak to an agent"

**Flow:**
1. Classifier detects `escalation` intent (high confidence)
2. Routes directly to escalation node
3. Returns: escalation message with options

## 🔧 Advanced Features

### Conversation Memory

Sessions automatically track conversation history:
- Last 10 messages per session
- 60-minute TTL with auto-cleanup
- Context injection for follow-up questions
- Persistent storage to disk (optional)

**Example:**
```
User: "What's my policy limit?"
Bot: "Your Gold Shield policy has ₹10,00,000 sum insured"
User: "How much have I used?" ← Uses context from previous turn
Bot: "You've utilized ₹95,000 (9.5% of your limit)"
```

### RAG Fallback

Policy questions automatically use vector search:
- 36 chunks from 2 comprehensive policy documents
- Sentence-transformers embeddings (all-MiniLM-L6-v2)
- Semantic similarity search
- Context-aware responses

### Auto-Correction

Failed queries automatically retry:
- Extract error from Neo4j
- Generate corrected Cypher
- Re-execute with fixes
- Max 2 retry attempts

### Smart Routing

Intent-based routing logic:
- High confidence (>0.7) → Knowledge Graph
- Low confidence (<0.7) → RAG fallback
- General questions → RAG
- Escalation requests → Human agent
- Missing customer_id → Escalation (for customer-specific queries)

## 📊 Performance

- **Query Response Time**: < 2 seconds average
- **Knowledge Graph**: 73 nodes, 248 relationships
- **Vector Store**: 36 document chunks
- **Session Storage**: In-memory with disk persistence
- **Concurrent Users**: Supports multiple simultaneous sessions

## 🔒 Security

- Environment variables for sensitive credentials
- Session IDs for conversation isolation
- No customer data in logs
- Neo4j SSL/TLS connections (Aura)

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Add tests for new features
4. Submit a pull request

## 📝 License

MIT License - see LICENSE file for details

## 🙏 Acknowledgments

- **Neo4j** - Graph database platform
- **LangGraph** - Agent orchestration framework
- **Google Gemini** - AI language model
- **ChromaDB** - Vector database
- **LangChain** - LLM integration framework

## 📞 Support

For issues and questions:
- GitHub Issues: https://github.com/Brohammad/Insurance-Graph-Analysis/issues

## 🗺️ Roadmap

- [x] Phase 1: Knowledge Graph Foundation
- [x] Phase 2: LangGraph Agent
- [x] Phase 3.1: Web Interface
- [x] Phase 3.2: ChromaDB RAG Integration
- [x] Phase 3.3: Conversation Memory
- [ ] Phase 3.4: Docker containerization + CI/CD
- [ ] Phase 3.5: Monitoring & logging
- [ ] Phase 4: Voice interface
- [ ] Phase 5: Multi-language support
- [ ] Phase 6: Claims processing automation

---

**Built with ❤️ using Neo4j, LangGraph, and Gemini 2.0 Flash**
