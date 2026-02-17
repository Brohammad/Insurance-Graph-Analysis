"""
Test Queries for MedAssist Knowledge Graph
Validates the knowledge graph with multi-hop queries from the case study
"""
from neo4j_connector import Neo4jConnector
from queries import QueryBuilder
from colorama import Fore, Style
import json


class QueryTester:
    """Test the knowledge graph with real-world scenarios"""
    
    def __init__(self, connector: Neo4jConnector):
        self.connector = connector
    
    def test_1_simple_coverage_check(self):
        """Test 1: Check if treatment is covered at a hospital"""
        print(f"\n{Fore.CYAN}{'='*70}")
        print(f"{Fore.CYAN}TEST 1: Simple Coverage Check")
        print(f"{Fore.CYAN}{'='*70}")
        print(f"{Fore.YELLOW}Query: Is diabetes treatment covered at Apollo Bangalore for customer CUST0001?")
        
        query = QueryBuilder.check_coverage("CUST0001", "E11", "HOSP0001")
        results = self.connector.execute_query(query, {
            'customer_id': 'CUST0001',
            'treatment_code': 'E11',
            'hospital_id': 'HOSP0001'
        })
        
        if results:
            for result in results:
                print(f"\n{Fore.GREEN}✓ Coverage Found:")
                print(f"  Policy: {result['policy_plan']}")
                print(f"  Sum Insured: ₹{result['sum_insured']:,}")
                print(f"  Treatment: {result['treatment_name']}")
                print(f"  Sub-limit: ₹{result['treatment_sub_limit']:,}")
                print(f"  Co-pay: {result['copay_amount']}%")
                print(f"  Hospital: {result['hospital_name']}")
                print(f"  Hospital Tier: {result['hospital_tier']}")
                print(f"  Estimated Cost: ₹{result['estimated_cost']:,}")
        else:
            print(f"{Fore.RED}✗ No coverage found or hospital not in network")
    
    def test_2_complex_multi_hop(self):
        """Test 2: Complex multi-hop query (medication coverage at specific hospital)"""
        print(f"\n{Fore.CYAN}{'='*70}")
        print(f"{Fore.CYAN}TEST 2: Complex Multi-Hop Query (Case Study Example)")
        print(f"{Fore.CYAN}{'='*70}")
        print(f"{Fore.YELLOW}Query: Is Metformin covered under cashless at Apollo for CUST0001?")
        
        query = QueryBuilder.complex_coverage_check("CUST0001", "Metformin", "Apollo")
        results = self.connector.execute_query(query, {
            'customer_id': 'CUST0001',
            'medication_name': 'Metformin',
            'hospital_name': 'Apollo'
        })
        
        if results:
            for result in results:
                print(f"\n{Fore.GREEN}✓ Complex Coverage Analysis:")
                print(f"  Policy: {result['policy_plan']}")
                print(f"  Medication: {result['medication_name']} ({result['generic_name']})")
                print(f"  Treats: {result['treatment_name']}")
                print(f"  Hospital: {result['hospital_name']}, {result['hospital_city']}")
                print(f"  Hospital Tier: {result['hospital_tier']}")
                print(f"  Cashless Available: {result['cashless_available']}")
                print(f"  Treatment Sub-limit: ₹{result['treatment_sub_limit']:,}")
                print(f"  Co-pay: {result['copay_pct']}%")
                if result['medication_coverage_pct']:
                    print(f"  Medication Coverage: {result['medication_coverage_pct']}%")
                if result['requires_preauth']:
                    print(f"  {Fore.YELLOW}⚠ Requires Pre-authorization")
        else:
            print(f"{Fore.RED}✗ Medication not covered or hospital not in network")
    
    def test_3_claim_history(self):
        """Test 3: Get claim history for customer"""
        print(f"\n{Fore.CYAN}{'='*70}")
        print(f"{Fore.CYAN}TEST 3: Claim History Analysis")
        print(f"{Fore.CYAN}{'='*70}")
        print(f"{Fore.YELLOW}Query: Get claim history for CUST0001")
        
        query = QueryBuilder.get_claim_history("CUST0001", limit=5)
        results = self.connector.execute_query(query, {'customer_id': 'CUST0001', 'limit': 5})
        
        if results:
            print(f"\n{Fore.GREEN}✓ Found {len(results)} claims:")
            for i, claim in enumerate(results, 1):
                print(f"\n  Claim {i}:")
                print(f"    ID: {claim['claim_id']}")
                print(f"    Status: {claim['status']}")
                print(f"    Claimed: ₹{claim['claimed_amount']:,}")
                print(f"    Approved: ₹{claim['approved_amount']:,}")
                if claim['rejection_reason']:
                    print(f"    {Fore.RED}Rejection: {claim['rejection_reason']}")
                if claim['remaining_eligible']:
                    print(f"    Remaining Eligible: ₹{claim['remaining_eligible']:,}")
                print(f"    Hospital: {claim['hospital_name']}")
                print(f"    Treatment: {claim['treatment_name']}")
                print(f"    Date: {claim['claim_date']}")
        else:
            print(f"{Fore.YELLOW}No claims found for this customer")
    
    def test_4_network_hospitals(self):
        """Test 4: Find all in-network hospitals"""
        print(f"\n{Fore.CYAN}{'='*70}")
        print(f"{Fore.CYAN}TEST 4: Network Hospital Finder")
        print(f"{Fore.CYAN}{'='*70}")
        print(f"{Fore.YELLOW}Query: Find in-network hospitals in Bangalore for CUST0001")
        
        query = QueryBuilder.find_network_hospitals("CUST0001", "Bangalore")
        results = self.connector.execute_query(query, {'customer_id': 'CUST0001', 'city': 'Bangalore'})
        
        if results:
            print(f"\n{Fore.GREEN}✓ Found {len(results)} hospitals:")
            for hospital in results:
                print(f"\n  {hospital['hospital_name']}")
                print(f"    City: {hospital['city']}")
                print(f"    Tier: {hospital['tier']}")
                print(f"    Discount: {hospital['discount']}%")
                if hospital['specialties']:
                    print(f"    Specialties: {', '.join(hospital['specialties'][:3])}")
        else:
            print(f"{Fore.RED}No in-network hospitals found")
    
    def test_5_policy_utilization(self):
        """Test 5: Check policy utilization"""
        print(f"\n{Fore.CYAN}{'='*70}")
        print(f"{Fore.CYAN}TEST 5: Policy Utilization Analysis")
        print(f"{Fore.CYAN}{'='*70}")
        print(f"{Fore.YELLOW}Query: Check policy utilization for CUST0001")
        
        query = QueryBuilder.get_policy_utilization("CUST0001")
        results = self.connector.execute_query(query, {'customer_id': 'CUST0001'})
        
        if results:
            for result in results:
                utilization_pct = (result['amount_utilized'] / result['total_cover']) * 100 if result['total_cover'] > 0 else 0
                print(f"\n{Fore.GREEN}✓ Policy Utilization:")
                print(f"  Policy: {result['plan_type']}")
                print(f"  Total Cover: ₹{result['total_cover']:,}")
                print(f"  Amount Utilized: ₹{result['amount_utilized']:,}")
                print(f"  Remaining Cover: ₹{result['remaining_cover']:,}")
                print(f"  Utilization: {utilization_pct:.1f}%")
                print(f"  Policy Period: {result['policy_start']} to {result['policy_end']}")
                print(f"  Renewal Date: {result['renewal_date']}")
        else:
            print(f"{Fore.RED}No active policy found")
    
    def test_6_alternative_hospitals(self):
        """Test 6: Find alternative hospitals (case study scenario)"""
        print(f"\n{Fore.CYAN}{'='*70}")
        print(f"{Fore.CYAN}TEST 6: Alternative Hospital Finder (Case Study Scenario)")
        print(f"{Fore.CYAN}{'='*70}")
        print(f"{Fore.YELLOW}Scenario: Claim partially rejected at Fortis Mumbai for knee surgery.")
        print(f"{Fore.YELLOW}Query: Find alternative hospitals in customer's city")
        
        query = QueryBuilder.find_alternative_hospitals("CUST0001", "M17", "HOSP0002")
        results = self.connector.execute_query(query, {
            'customer_id': 'CUST0001',
            'treatment_code': 'M17',
            'excluded_hospital_id': 'HOSP0002'
        })
        
        if results:
            print(f"\n{Fore.GREEN}✓ Found {len(results)} alternative hospitals:")
            for i, hospital in enumerate(results, 1):
                print(f"\n  Option {i}: {hospital['hospital_name']}")
                print(f"    City: {hospital['city']}")
                print(f"    Tier: {hospital['tier']}")
                print(f"    Coverage Limit: ₹{hospital['coverage_limit']:,}")
                print(f"    Co-pay: {hospital['copay_amount']}%")
                print(f"    Discount: {hospital['discount_pct']}%")
        else:
            print(f"{Fore.YELLOW}No alternative hospitals found in customer's city")
    
    def test_7_medication_coverage(self):
        """Test 7: Check medication coverage"""
        print(f"\n{Fore.CYAN}{'='*70}")
        print(f"{Fore.CYAN}TEST 7: Medication Coverage Check")
        print(f"{Fore.CYAN}{'='*70}")
        print(f"{Fore.YELLOW}Query: Is Insulin covered for CUST0001?")
        
        query = QueryBuilder.check_medication_coverage("CUST0001", "Insulin")
        results = self.connector.execute_query(query, {'customer_id': 'CUST0001', 'medication_name': 'Insulin'})
        
        if results:
            print(f"\n{Fore.GREEN}✓ Found {len(results)} matching medication(s):")
            for med in results:
                print(f"\n  {med['medication_name']} ({med['generic_name']})")
                print(f"    Formulary Tier: {med['tier']}")
                print(f"    Coverage: {med['coverage_percentage']}%")
                print(f"    Treats: {med['treats_condition']}")
                if med['requires_preauth']:
                    print(f"    {Fore.YELLOW}⚠ Requires Pre-authorization")
        else:
            print(f"{Fore.RED}Medication not covered under policy")
    
    def test_8_treatment_medications(self):
        """Test 8: Get medications for a treatment"""
        print(f"\n{Fore.CYAN}{'='*70}")
        print(f"{Fore.CYAN}TEST 8: Treatment Medications Lookup")
        print(f"{Fore.CYAN}{'='*70}")
        print(f"{Fore.YELLOW}Query: What medications treat Diabetes (E11)?")
        
        query = QueryBuilder.get_treatment_medications("E11")
        results = self.connector.execute_query(query, {'treatment_code': 'E11'})
        
        if results:
            print(f"\n{Fore.GREEN}✓ Found {len(results)} medication(s):")
            for med in results:
                primary_label = "Primary" if med['is_primary_treatment'] else "Alternative"
                print(f"\n  {med['medication_name']} ({med['generic_name']})")
                print(f"    Type: {primary_label}")
                print(f"    Tier: {med['tier']}")
                if med['requires_preauth']:
                    print(f"    {Fore.YELLOW}⚠ Requires Pre-authorization")
        else:
            print(f"{Fore.RED}No medications found for this treatment")
    
    def run_all_tests(self):
        """Run all test queries"""
        print(f"\n{Fore.MAGENTA}{'='*70}")
        print(f"{Fore.MAGENTA}MedAssist Knowledge Graph - Test Suite")
        print(f"{Fore.MAGENTA}Testing Multi-Hop Queries from Case Study")
        print(f"{Fore.MAGENTA}{'='*70}")
        
        try:
            self.test_1_simple_coverage_check()
            self.test_2_complex_multi_hop()
            self.test_3_claim_history()
            self.test_4_network_hospitals()
            self.test_5_policy_utilization()
            self.test_6_alternative_hospitals()
            self.test_7_medication_coverage()
            self.test_8_treatment_medications()
            
            print(f"\n{Fore.MAGENTA}{'='*70}")
            print(f"{Fore.GREEN}✓ All tests completed!")
            print(f"{Fore.MAGENTA}{'='*70}")
        except Exception as e:
            print(f"\n{Fore.RED}✗ Test suite failed: {e}")


if __name__ == "__main__":
    connector = Neo4jConnector()
    
    if connector.connect(wait_time=5):  # Shorter wait for testing
        tester = QueryTester(connector)
        tester.run_all_tests()
        connector.close()
    else:
        print(f"{Fore.RED}Failed to connect to Neo4j")
