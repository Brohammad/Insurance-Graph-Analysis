#!/bin/bash
# MedAssist Knowledge Graph - Quick Commands Reference

echo "================================================================"
echo "  MedAssist Healthcare Insurance - Knowledge Graph System"
echo "  Quick Commands (Always use with virtual environment)"
echo "================================================================"
echo ""
echo "IMPORTANT: Always activate the virtual environment first!"
echo "  source .venv/bin/activate"
echo ""
echo "Then run any command:"
echo ""
echo "1️⃣  Initialize Database:"
echo "   python ingest.py"
echo ""
echo "2️⃣  Run Test Queries:"
echo "   python test_queries.py"
echo ""
echo "3️⃣  Launch Interactive App:"
echo "   python main.py"
echo ""
echo "4️⃣  View Project Info:"
echo "   python info.py"
echo ""
echo "5️⃣  Test Configuration:"
echo "   python config.py"
echo ""
echo "6️⃣  Generate Sample Data:"
echo "   python seed_data.py"
echo ""
echo "================================================================"
echo ""
echo "📊 Current Database Status:"
echo "================================================================"

# Activate venv and check database status
source .venv/bin/activate

python -c "
from neo4j_connector import Neo4jConnector
try:
    c = Neo4jConnector()
    if c.connect(wait_time=5):
        node_counts = c.get_node_count()
        rel_count = c.get_relationship_count()
        total_nodes = sum(node_counts.values())
        
        print(f'Total Nodes: {total_nodes}')
        for label, count in node_counts.items():
            if count > 0:
                print(f'  • {label}: {count}')
        print(f'Total Relationships: {rel_count}')
        
        if total_nodes == 0:
            print('\n⚠️  Database is empty! Run: python ingest.py')
        else:
            print('\n✅ Database is populated and ready!')
        
        c.close()
    else:
        print('❌ Could not connect to Neo4j')
except Exception as e:
    print(f'❌ Error: {e}')
"

echo ""
echo "================================================================"
