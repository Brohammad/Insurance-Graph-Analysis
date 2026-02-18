# 🤖 MedAssist AI Chatbot - Quick Start Guide

## What is MedAssist AI?

MedAssist AI is a conversational healthcare insurance assistant that combines:
- **Gemini 2.0 Flash** for natural language understanding
- **Neo4j Knowledge Graph** for accurate, deterministic answers
- **Zero hallucination** - all answers backed by real graph data

## Features

✅ **Natural Conversations** - Ask questions in plain English  
✅ **Intelligent Intent Detection** - Automatically understands what you need  
✅ **Multi-hop Reasoning** - Traverses complex relationships in the knowledge graph  
✅ **Personalized Responses** - Uses your customer ID for tailored information  
✅ **Real-time Data** - All answers from live Neo4j database  

## How to Use

### Step 1: Activate Virtual Environment
```bash
cd /home/labuser/Desktop/graphbased
source .venv/bin/activate
```

### Step 2: Launch Chatbot
```bash
python chatbot.py
```

### Step 3: Start Chatting!

The chatbot will ask for your Customer ID (optional). Available IDs: **CUST0001** to **CUST0010**

## Example Conversations

### 💊 Check Medication Coverage
```
You: Is Metformin covered under my policy?

MedAssist AI: Yes! Metformin is covered under your Gold Shield policy 
at 80% coverage. It's a Tier-1 medication for diabetes treatment and 
doesn't require pre-authorization. 💊
```

### 🏥 Find Hospitals
```
You: Show me hospitals in Bangalore

MedAssist AI: I found 3 in-network hospitals in Bangalore with cashless 
facilities:
  1. Apollo Bangalore - Tier-1 | Discount: 10%
  2. Fortis Bangalore - Tier-1 | Discount: 20%
  3. Narayana Health Bangalore - Tier-2 | Discount: 15%
```

### 🔍 Coverage Check
```
You: Is diabetes covered at Apollo Bangalore?

MedAssist AI: Great news! Your Gold Shield policy covers Type 2 Diabetes 
Treatment at Apollo Bangalore. The coverage has a sub-limit of ₹75,000 
with a 20% co-pay. Cashless facility is available! ✅
```

### 📋 Claim History
```
You: What's my claim history?

MedAssist AI: You have 1 claim on record:
  1. CLM0010 - Pending
     Amount: ₹32,188 | Date: 2026-01-05
     Hospital: Max Healthcare Pune
     Treatment: Hypertension Treatment
```

### 📊 Policy Utilization
```
You: How much of my policy have I used?

MedAssist AI: You're in great shape! Your Gold Shield policy has a total 
cover of ₹10,00,000. You've utilized ₹0 so far, leaving you with 
₹10,00,000 remaining (0% utilization). Your policy renews on 2026-12-23.
```

## Supported Query Types

| Intent | Example Questions |
|--------|-------------------|
| **Coverage Check** | "Is knee surgery covered at Fortis Mumbai?" |
| **Hospital Finder** | "Show me hospitals in Delhi" |
| **Claim History** | "What claims have I filed?" |
| **Policy Utilization** | "How much coverage do I have left?" |
| **Medication Coverage** | "Is Insulin covered?" |
| **General Questions** | "What plans do you offer?" |

## Special Commands

- **help** or **?** - Show example questions
- **quit**, **exit**, **bye** - End conversation
- Provide customer ID anytime: "I'm CUST0001"

## How It Works

```
User Question
     ↓
[Gemini 2.0 Flash]
     ↓
Intent Classification + Parameter Extraction
     ↓
[Query Builder]
     ↓
Cypher Query Generation
     ↓
[Neo4j Knowledge Graph]
     ↓
Graph Traversal (Multi-hop)
     ↓
[Gemini 2.0 Flash]
     ↓
Natural Language Response
     ↓
User-Friendly Answer
```

## Architecture Highlights

### 🧠 **Intelligent Intent Detection**
Uses Gemini to classify user queries into intents:
- coverage_check
- hospital_finder
- claim_history
- policy_utilization
- medication_coverage
- general_question

### 🔍 **Dynamic Parameter Extraction**
Automatically extracts:
- Customer IDs (CUST0001-CUST0010)
- Treatment names (diabetes, knee surgery, etc.)
- Hospital names (Apollo, Fortis, Max, etc.)
- Cities (Bangalore, Mumbai, Delhi, etc.)
- Medication names (Metformin, Insulin, etc.)

### 🎯 **Knowledge Graph Queries**
Generates optimized Cypher queries that traverse relationships:
```cypher
MATCH (c:Customer)-[:HAS_POLICY]->(p:Policy),
      (p)-[cov:COVERS]->(t:Treatment),
      (p)-[net:IN_NETWORK]->(h:Hospital)
WHERE net.cashless_eligible = true
RETURN coverage_details
```

### 💬 **Natural Language Generation**
Uses Gemini to convert graph data into conversational responses:
- Friendly and empathetic tone
- Clear explanation of coverage terms
- Highlights important conditions
- Uses Indian Rupees (₹) formatting

## Troubleshooting

### "Failed to connect to Neo4j"
- Make sure you ran `python ingest.py` first
- Check that your Neo4j Aura instance is running
- Verify credentials in `.env` file

### "I need your Customer ID"
- Provide a valid customer ID: CUST0001 to CUST0010
- You can type it anytime in the conversation

### API Rate Limits
- Free tier Gemini API has rate limits
- If you hit limits, wait a minute and try again

## Advanced Usage

### Custom Customer IDs
To add more customers, edit `seed_data.py` and run:
```bash
python ingest.py
```

### Query Logging
The chatbot logs all intent classifications and queries for debugging.

### Extending Intents
Add new intents in the `classify_intent()` method in `chatbot.py`.

## Comparison: Chatbot vs CLI vs Test Queries

| Feature | Chatbot | Interactive CLI | Test Queries |
|---------|---------|-----------------|--------------|
| Natural Language | ✅ Yes | ❌ No | ❌ No |
| AI-powered | ✅ Gemini | ❌ Manual | ❌ Scripted |
| User-friendly | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐ |
| Technical Users | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| Conversational | ✅ Yes | ❌ No | ❌ No |
| Intent Detection | ✅ Automatic | ❌ Manual Menu | ❌ Fixed |
| Best For | End Users | Admins/Devs | Testing/Demo |

## Next Steps

### Phase 2: LangGraph Agent
The chatbot is Phase 1. Next we'll add:
- ✅ Text-to-Cypher agent (DONE - implemented in chatbot)
- ☐ LangGraph StateGraph orchestration
- ☐ RAG fallback for policy documents
- ☐ Confidence-based escalation
- ☐ Query auto-correction loop

### Phase 3: Production Features
- ☐ Multi-turn conversation memory
- ☐ Voice interface (speech-to-text)
- ☐ Web interface (Flask/FastAPI)
- ☐ Authentication and security
- ☐ Analytics dashboard

---

**Ready to chat? Run:** `python chatbot.py` 🚀
