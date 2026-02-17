"""
Neo4j Schema Definition for MedAssist Healthcare Insurance Knowledge Graph
Defines all node types, relationships, and constraints
"""

# Node Labels
NODE_CUSTOMER = "Customer"
NODE_POLICY = "Policy"
NODE_HOSPITAL = "Hospital"
NODE_TREATMENT = "Treatment"
NODE_MEDICATION = "Medication"
NODE_CLAIM = "Claim"

# Relationship Types
REL_HAS_POLICY = "HAS_POLICY"
REL_COVERS = "COVERS"
REL_IN_NETWORK = "IN_NETWORK"
REL_IN_FORMULARY = "IN_FORMULARY"
REL_TREATS = "TREATS"
REL_FILED_CLAIM = "FILED_CLAIM"
REL_AT_HOSPITAL = "AT_HOSPITAL"
REL_FOR_TREATMENT = "FOR_TREATMENT"

# Constraints and Indexes
CONSTRAINTS = [
    f"CREATE CONSTRAINT customer_id_unique IF NOT EXISTS FOR (c:{NODE_CUSTOMER}) REQUIRE c.id IS UNIQUE",
    f"CREATE CONSTRAINT policy_id_unique IF NOT EXISTS FOR (p:{NODE_POLICY}) REQUIRE p.id IS UNIQUE",
    f"CREATE CONSTRAINT hospital_id_unique IF NOT EXISTS FOR (h:{NODE_HOSPITAL}) REQUIRE h.id IS UNIQUE",
    f"CREATE CONSTRAINT treatment_code_unique IF NOT EXISTS FOR (t:{NODE_TREATMENT}) REQUIRE t.code IS UNIQUE",
    f"CREATE CONSTRAINT medication_id_unique IF NOT EXISTS FOR (m:{NODE_MEDICATION}) REQUIRE m.id IS UNIQUE",
    f"CREATE CONSTRAINT claim_id_unique IF NOT EXISTS FOR (cl:{NODE_CLAIM}) REQUIRE cl.id IS UNIQUE",
]

INDEXES = [
    f"CREATE INDEX customer_name_idx IF NOT EXISTS FOR (c:{NODE_CUSTOMER}) ON (c.name)",
    f"CREATE INDEX customer_city_idx IF NOT EXISTS FOR (c:{NODE_CUSTOMER}) ON (c.city)",
    f"CREATE INDEX hospital_city_idx IF NOT EXISTS FOR (h:{NODE_HOSPITAL}) ON (h.city)",
    f"CREATE INDEX hospital_name_idx IF NOT EXISTS FOR (h:{NODE_HOSPITAL}) ON (h.name)",
    f"CREATE INDEX policy_plan_type_idx IF NOT EXISTS FOR (p:{NODE_POLICY}) ON (p.plan_type)",
    f"CREATE INDEX claim_status_idx IF NOT EXISTS FOR (cl:{NODE_CLAIM}) ON (cl.status)",
]

# Schema Documentation
SCHEMA_DOC = """
MedAssist Healthcare Insurance Knowledge Graph Schema

NODES:
------
Customer: {id, name, age, city, pre_existing, phone, email}
Policy: {id, plan_type, sum_insured, copay_pct, renewal_date, premium, deductible}
Hospital: {id, name, city, tier, cashless_enabled, address, specialties}
Treatment: {code, category, name, avg_cost, sub_limit, requires_preauth}
Medication: {id, name, generic, formulary_tier, requires_preauth}
Claim: {id, status, amount, approved_amount, date, rejection_reason, remaining_eligible}

RELATIONSHIPS:
--------------
(Customer)-[:HAS_POLICY {start_date, end_date, is_active}]->(Policy)
(Policy)-[:COVERS {sub_limit, waiting_period, copay, coverage_pct}]->(Treatment)
(Policy)-[:IN_NETWORK {cashless_eligible, tier, discount_pct}]->(Hospital)
(Policy)-[:IN_FORMULARY {coverage_pct, requires_preauth, tier}]->(Medication)
(Medication)-[:TREATS {primary, effectiveness}]->(Treatment)
(Customer)-[:FILED_CLAIM {claim_date, hospital_id}]->(Claim)
(Claim)-[:AT_HOSPITAL]->(Hospital)
(Claim)-[:FOR_TREATMENT]->(Treatment)

EXAMPLE QUERIES:
----------------
1. Check coverage for a specific treatment at a hospital:
   MATCH (c:Customer {id: $cust_id})-[:HAS_POLICY]->(p:Policy),
         (p)-[cov:COVERS]->(t:Treatment {code: $treatment_code}),
         (p)-[net:IN_NETWORK]->(h:Hospital {id: $hospital_id})
   WHERE net.cashless_eligible = true
   RETURN p.plan_type, cov.sub_limit, cov.copay, net.tier

2. Find all in-network hospitals for a customer:
   MATCH (c:Customer {id: $cust_id})-[:HAS_POLICY]->(p:Policy)-[net:IN_NETWORK]->(h:Hospital)
   WHERE net.cashless_eligible = true
   RETURN h.name, h.city, h.tier, net.discount_pct
   ORDER BY h.tier, h.name

3. Get claim history with rejection reasons:
   MATCH (c:Customer {id: $cust_id})-[:FILED_CLAIM]->(cl:Claim)-[:AT_HOSPITAL]->(h:Hospital)
   RETURN cl.id, cl.status, cl.amount, cl.approved_amount, 
          cl.rejection_reason, h.name, cl.date
   ORDER BY cl.date DESC
"""

def get_schema_info():
    """Return schema information for LLM context"""
    return {
        "nodes": [
            {"label": NODE_CUSTOMER, "properties": ["id", "name", "age", "city", "pre_existing", "phone", "email"]},
            {"label": NODE_POLICY, "properties": ["id", "plan_type", "sum_insured", "copay_pct", "renewal_date", "premium", "deductible"]},
            {"label": NODE_HOSPITAL, "properties": ["id", "name", "city", "tier", "cashless_enabled", "address", "specialties"]},
            {"label": NODE_TREATMENT, "properties": ["code", "category", "name", "avg_cost", "sub_limit", "requires_preauth"]},
            {"label": NODE_MEDICATION, "properties": ["id", "name", "generic", "formulary_tier", "requires_preauth"]},
            {"label": NODE_CLAIM, "properties": ["id", "status", "amount", "approved_amount", "date", "rejection_reason", "remaining_eligible"]},
        ],
        "relationships": [
            {"type": REL_HAS_POLICY, "from": NODE_CUSTOMER, "to": NODE_POLICY, "properties": ["start_date", "end_date", "is_active"]},
            {"type": REL_COVERS, "from": NODE_POLICY, "to": NODE_TREATMENT, "properties": ["sub_limit", "waiting_period", "copay", "coverage_pct"]},
            {"type": REL_IN_NETWORK, "from": NODE_POLICY, "to": NODE_HOSPITAL, "properties": ["cashless_eligible", "tier", "discount_pct"]},
            {"type": REL_IN_FORMULARY, "from": NODE_POLICY, "to": NODE_MEDICATION, "properties": ["coverage_pct", "requires_preauth", "tier"]},
            {"type": REL_TREATS, "from": NODE_MEDICATION, "to": NODE_TREATMENT, "properties": ["primary", "effectiveness"]},
            {"type": REL_FILED_CLAIM, "from": NODE_CUSTOMER, "to": NODE_CLAIM, "properties": ["claim_date", "hospital_id"]},
            {"type": REL_AT_HOSPITAL, "from": NODE_CLAIM, "to": NODE_HOSPITAL, "properties": []},
            {"type": REL_FOR_TREATMENT, "from": NODE_CLAIM, "to": NODE_TREATMENT, "properties": []},
        ],
        "documentation": SCHEMA_DOC
    }
