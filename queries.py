"""
Cypher Query Utilities for MedAssist Healthcare Insurance KG
Contains reusable query functions for common operations
"""
from typing import Dict, List, Any, Optional
from schema import *


class QueryBuilder:
    """Builder class for constructing Cypher queries"""
    
    @staticmethod
    def get_customer_policy(customer_id: str) -> str:
        """Get active policy for a customer"""
        return f"""
        MATCH (c:{NODE_CUSTOMER} {{id: $customer_id}})-[hp:{REL_HAS_POLICY}]->(p:{NODE_POLICY})
        WHERE hp.is_active = true
        RETURN c, p, hp
        """
    
    @staticmethod
    def check_coverage(customer_id: str, treatment_code: str, hospital_id: str) -> str:
        """Check if treatment is covered at a specific hospital for a customer"""
        return f"""
        MATCH (c:{NODE_CUSTOMER} {{id: $customer_id}})-[:{REL_HAS_POLICY}]->(p:{NODE_POLICY}),
              (p)-[cov:{REL_COVERS}]->(t:{NODE_TREATMENT} {{code: $treatment_code}}),
              (p)-[net:{REL_IN_NETWORK}]->(h:{NODE_HOSPITAL} {{id: $hospital_id}})
        WHERE net.cashless_eligible = true
        RETURN p.plan_type as policy_plan,
               p.sum_insured as sum_insured,
               cov.sub_limit as treatment_sub_limit,
               cov.copay as copay_amount,
               cov.coverage_pct as coverage_percentage,
               net.tier as hospital_tier,
               net.discount_pct as discount,
               t.name as treatment_name,
               t.avg_cost as estimated_cost,
               h.name as hospital_name
        """
    
    @staticmethod
    def find_network_hospitals(customer_id: str, city: Optional[str] = None) -> str:
        """Find all in-network hospitals for a customer"""
        city_filter = f"AND h.city = $city" if city else ""
        return f"""
        MATCH (c:{NODE_CUSTOMER} {{id: $customer_id}})-[:{REL_HAS_POLICY}]->(p:{NODE_POLICY})-[net:{REL_IN_NETWORK}]->(h:{NODE_HOSPITAL})
        WHERE net.cashless_eligible = true {city_filter}
        RETURN h.id as hospital_id,
               h.name as hospital_name,
               h.city as city,
               h.tier as tier,
               h.specialties as specialties,
               net.discount_pct as discount
        ORDER BY h.tier, h.name
        """
    
    @staticmethod
    def get_claim_history(customer_id: str, limit: int = 10) -> str:
        """Get claim history for a customer"""
        return f"""
        MATCH (c:{NODE_CUSTOMER} {{id: $customer_id}})-[:{REL_FILED_CLAIM}]->(cl:{NODE_CLAIM})
        OPTIONAL MATCH (cl)-[:{REL_AT_HOSPITAL}]->(h:{NODE_HOSPITAL})
        OPTIONAL MATCH (cl)-[:{REL_FOR_TREATMENT}]->(t:{NODE_TREATMENT})
        RETURN cl.id as claim_id,
               cl.status as status,
               cl.amount as claimed_amount,
               cl.approved_amount as approved_amount,
               cl.rejection_reason as rejection_reason,
               cl.remaining_eligible as remaining_eligible,
               cl.date as claim_date,
               h.name as hospital_name,
               t.name as treatment_name
        ORDER BY cl.date DESC
        LIMIT $limit
        """
    
    @staticmethod
    def check_medication_coverage(customer_id: str, medication_name: str) -> str:
        """Check if a medication is covered under customer's policy"""
        return f"""
        MATCH (c:{NODE_CUSTOMER} {{id: $customer_id}})-[:{REL_HAS_POLICY}]->(p:{NODE_POLICY})-[form:{REL_IN_FORMULARY}]->(m:{NODE_MEDICATION})
        WHERE toLower(m.name) CONTAINS toLower($medication_name) OR toLower(m.generic) CONTAINS toLower($medication_name)
        OPTIONAL MATCH (m)-[:{REL_TREATS}]->(t:{NODE_TREATMENT})
        RETURN m.name as medication_name,
               m.generic as generic_name,
               m.formulary_tier as tier,
               form.coverage_pct as coverage_percentage,
               form.requires_preauth as requires_preauth,
               t.name as treats_condition
        """
    
    @staticmethod
    def get_policy_utilization(customer_id: str) -> str:
        """Get policy utilization summary for a customer"""
        return f"""
        MATCH (c:{NODE_CUSTOMER} {{id: $customer_id}})-[hp:{REL_HAS_POLICY}]->(p:{NODE_POLICY})
        WHERE hp.is_active = true
        OPTIONAL MATCH (c)-[:{REL_FILED_CLAIM}]->(cl:{NODE_CLAIM})
        WHERE cl.status = 'Approved' OR cl.status = 'Partially Approved'
        WITH p, hp, sum(cl.approved_amount) as total_utilized
        RETURN p.id as policy_id,
               p.plan_type as plan_type,
               p.sum_insured as total_cover,
               COALESCE(total_utilized, 0) as amount_utilized,
               p.sum_insured - COALESCE(total_utilized, 0) as remaining_cover,
               hp.start_date as policy_start,
               hp.end_date as policy_end,
               p.renewal_date as renewal_date
        """
    
    @staticmethod
    def find_alternative_hospitals(customer_id: str, treatment_code: str, excluded_hospital_id: str) -> str:
        """Find alternative hospitals for a treatment (excluding one hospital)"""
        return f"""
        MATCH (c:{NODE_CUSTOMER} {{id: $customer_id}})-[:{REL_HAS_POLICY}]->(p:{NODE_POLICY}),
              (p)-[cov:{REL_COVERS}]->(t:{NODE_TREATMENT} {{code: $treatment_code}}),
              (p)-[net:{REL_IN_NETWORK}]->(h:{NODE_HOSPITAL})
        WHERE h.id <> $excluded_hospital_id 
          AND net.cashless_eligible = true
          AND h.city = c.city
        RETURN h.id as hospital_id,
               h.name as hospital_name,
               h.city as city,
               h.tier as tier,
               cov.sub_limit as coverage_limit,
               cov.copay as copay_amount,
               net.discount_pct as discount_pct
        ORDER BY h.tier, net.discount_pct DESC
        LIMIT 5
        """
    
    @staticmethod
    def get_treatment_medications(treatment_code: str) -> str:
        """Get all medications that treat a specific condition"""
        return f"""
        MATCH (t:{NODE_TREATMENT} {{code: $treatment_code}})<-[treats:{REL_TREATS}]-(m:{NODE_MEDICATION})
        RETURN m.id as medication_id,
               m.name as medication_name,
               m.generic as generic_name,
               m.formulary_tier as tier,
               m.requires_preauth as requires_preauth,
               treats.primary as is_primary_treatment
        ORDER BY treats.primary DESC, m.formulary_tier
        """
    
    @staticmethod
    def complex_coverage_check(customer_id: str, medication_name: str, hospital_name: str) -> str:
        """
        Complex multi-hop query: Check if medication is covered under cashless at a specific hospital
        This is the type of query mentioned in the case study
        """
        return f"""
        MATCH (c:{NODE_CUSTOMER} {{id: $customer_id}})-[:{REL_HAS_POLICY}]->(p:{NODE_POLICY}),
              (p)-[cov:{REL_COVERS}]->(t:{NODE_TREATMENT})<-[:{REL_TREATS}]-(m:{NODE_MEDICATION}),
              (p)-[net:{REL_IN_NETWORK}]->(h:{NODE_HOSPITAL})
        WHERE (toLower(m.name) CONTAINS toLower($medication_name) OR toLower(m.generic) CONTAINS toLower($medication_name))
          AND toLower(h.name) CONTAINS toLower($hospital_name)
          AND net.cashless_eligible = true
        OPTIONAL MATCH (p)-[form:{REL_IN_FORMULARY}]->(m)
        RETURN p.plan_type as policy_plan,
               m.name as medication_name,
               m.generic as generic_name,
               t.name as treatment_name,
               h.name as hospital_name,
               h.city as hospital_city,
               net.tier as hospital_tier,
               cov.sub_limit as treatment_sub_limit,
               cov.copay as copay_pct,
               form.coverage_pct as medication_coverage_pct,
               form.requires_preauth as requires_preauth,
               net.cashless_eligible as cashless_available
        """


class CypherQueries:
    """Collection of predefined Cypher queries"""
    
    # Node creation queries
    CREATE_CUSTOMER = f"""
    CREATE (c:{NODE_CUSTOMER} {{
        id: $id, name: $name, age: $age, city: $city,
        pre_existing: $pre_existing, phone: $phone, email: $email
    }})
    RETURN c
    """
    
    CREATE_POLICY = f"""
    CREATE (p:{NODE_POLICY} {{
        id: $id, plan_type: $plan_type, sum_insured: $sum_insured,
        copay_pct: $copay_pct, renewal_date: $renewal_date,
        premium: $premium, deductible: $deductible
    }})
    RETURN p
    """
    
    CREATE_HOSPITAL = f"""
    CREATE (h:{NODE_HOSPITAL} {{
        id: $id, name: $name, city: $city, tier: $tier,
        cashless_enabled: $cashless_enabled, address: $address,
        specialties: $specialties
    }})
    RETURN h
    """
    
    CREATE_TREATMENT = f"""
    CREATE (t:{NODE_TREATMENT} {{
        code: $code, category: $category, name: $name,
        avg_cost: $avg_cost, sub_limit: $sub_limit,
        requires_preauth: $requires_preauth
    }})
    RETURN t
    """
    
    CREATE_MEDICATION = f"""
    CREATE (m:{NODE_MEDICATION} {{
        id: $id, name: $name, generic: $generic,
        formulary_tier: $formulary_tier, requires_preauth: $requires_preauth
    }})
    RETURN m
    """
    
    CREATE_CLAIM = f"""
    CREATE (cl:{NODE_CLAIM} {{
        id: $id, status: $status, amount: $amount,
        approved_amount: $approved_amount, date: $date,
        rejection_reason: $rejection_reason, remaining_eligible: $remaining_eligible
    }})
    RETURN cl
    """
    
    # Relationship creation queries
    CREATE_HAS_POLICY_REL = f"""
    MATCH (c:{NODE_CUSTOMER} {{id: $customer_id}}), (p:{NODE_POLICY} {{id: $policy_id}})
    CREATE (c)-[r:{REL_HAS_POLICY} {{
        start_date: $start_date, end_date: $end_date, is_active: $is_active
    }}]->(p)
    RETURN r
    """
    
    CREATE_COVERS_REL = f"""
    MATCH (p:{NODE_POLICY} {{id: $policy_id}}), (t:{NODE_TREATMENT} {{code: $treatment_code}})
    CREATE (p)-[r:{REL_COVERS} {{
        sub_limit: $sub_limit, waiting_period: $waiting_period,
        copay: $copay, coverage_pct: $coverage_pct
    }}]->(t)
    RETURN r
    """
    
    CREATE_IN_NETWORK_REL = f"""
    MATCH (p:{NODE_POLICY} {{id: $policy_id}}), (h:{NODE_HOSPITAL} {{id: $hospital_id}})
    CREATE (p)-[r:{REL_IN_NETWORK} {{
        cashless_eligible: $cashless_eligible, tier: $tier, discount_pct: $discount_pct
    }}]->(h)
    RETURN r
    """
    
    CREATE_IN_FORMULARY_REL = f"""
    MATCH (p:{NODE_POLICY} {{id: $policy_id}}), (m:{NODE_MEDICATION} {{id: $medication_id}})
    CREATE (p)-[r:{REL_IN_FORMULARY} {{
        coverage_pct: $coverage_pct, requires_preauth: $requires_preauth, tier: $tier
    }}]->(m)
    RETURN r
    """
    
    CREATE_TREATS_REL = f"""
    MATCH (m:{NODE_MEDICATION} {{id: $medication_id}}), (t:{NODE_TREATMENT} {{code: $treatment_code}})
    CREATE (m)-[r:{REL_TREATS} {{
        primary: $primary, effectiveness: $effectiveness
    }}]->(t)
    RETURN r
    """
    
    CREATE_FILED_CLAIM_REL = f"""
    MATCH (c:{NODE_CUSTOMER} {{id: $customer_id}}), (cl:{NODE_CLAIM} {{id: $claim_id}})
    CREATE (c)-[r:{REL_FILED_CLAIM} {{
        claim_date: $claim_date, hospital_id: $hospital_id
    }}]->(cl)
    RETURN r
    """
    
    CREATE_AT_HOSPITAL_REL = f"""
    MATCH (cl:{NODE_CLAIM} {{id: $claim_id}}), (h:{NODE_HOSPITAL} {{id: $hospital_id}})
    CREATE (cl)-[r:{REL_AT_HOSPITAL}]->(h)
    RETURN r
    """
    
    CREATE_FOR_TREATMENT_REL = f"""
    MATCH (cl:{NODE_CLAIM} {{id: $claim_id}}), (t:{NODE_TREATMENT} {{code: $treatment_code}})
    CREATE (cl)-[r:{REL_FOR_TREATMENT}]->(t)
    RETURN r
    """


if __name__ == "__main__":
    # Print sample queries
    print("=== Sample Query: Check Coverage ===")
    print(QueryBuilder.check_coverage("CUST0001", "E11", "HOSP0001"))
    print("\n=== Sample Query: Complex Coverage Check ===")
    print(QueryBuilder.complex_coverage_check("CUST0001", "Metformin", "Apollo"))
