"""
Data Ingestion Script for MedAssist Healthcare Insurance Knowledge Graph
Populates Neo4j with seed data and creates all relationships
"""
from neo4j_connector import Neo4jConnector
from seed_data import generate_all_data
from schema import CONSTRAINTS, INDEXES
from queries import CypherQueries
from colorama import Fore, Style
from datetime import datetime, timedelta
import random


class DataIngestor:
    """Handles data ingestion into Neo4j"""
    
    def __init__(self, connector: Neo4jConnector):
        self.connector = connector
        self.data = None
    
    def setup_schema(self):
        """Create constraints and indexes"""
        print(f"\n{Fore.CYAN}=== Setting up Schema ===")
        
        # Create constraints
        print(f"{Fore.YELLOW}Creating constraints...")
        for constraint in CONSTRAINTS:
            try:
                self.connector.execute_query(constraint)
                print(f"{Fore.GREEN}  ✓ Created constraint")
            except Exception as e:
                if "already exists" in str(e).lower() or "equivalent" in str(e).lower():
                    print(f"{Fore.BLUE}  ⓘ Constraint already exists")
                else:
                    print(f"{Fore.RED}  ✗ Failed: {e}")
        
        # Create indexes
        print(f"{Fore.YELLOW}Creating indexes...")
        for index in INDEXES:
            try:
                self.connector.execute_query(index)
                print(f"{Fore.GREEN}  ✓ Created index")
            except Exception as e:
                if "already exists" in str(e).lower() or "equivalent" in str(e).lower():
                    print(f"{Fore.BLUE}  ⓘ Index already exists")
                else:
                    print(f"{Fore.RED}  ✗ Failed: {e}")
        
        print(f"{Fore.GREEN}✓ Schema setup complete")
    
    def load_data(self):
        """Generate and load all seed data"""
        print(f"\n{Fore.CYAN}=== Generating Seed Data ===")
        self.data = generate_all_data()
        
        print(f"{Fore.GREEN}✓ Generated:")
        print(f"  - {len(self.data['customers'])} customers")
        print(f"  - {len(self.data['policies'])} policies")
        print(f"  - {len(self.data['hospitals'])} hospitals")
        print(f"  - {len(self.data['treatments'])} treatments")
        print(f"  - {len(self.data['medications'])} medications")
        print(f"  - {len(self.data['claims'])} claims")
    
    def ingest_customers(self):
        """Ingest customer nodes"""
        print(f"\n{Fore.CYAN}=== Ingesting Customers ===")
        for customer in self.data['customers']:
            try:
                self.connector.execute_query(CypherQueries.CREATE_CUSTOMER, customer)
                print(f"{Fore.GREEN}  ✓ Created customer: {customer['name']}")
            except Exception as e:
                print(f"{Fore.RED}  ✗ Failed to create customer {customer['id']}: {e}")
    
    def ingest_policies(self):
        """Ingest policy nodes"""
        print(f"\n{Fore.CYAN}=== Ingesting Policies ===")
        for policy in self.data['policies']:
            try:
                self.connector.execute_query(CypherQueries.CREATE_POLICY, policy)
                print(f"{Fore.GREEN}  ✓ Created policy: {policy['plan_type']}")
            except Exception as e:
                print(f"{Fore.RED}  ✗ Failed to create policy {policy['id']}: {e}")
    
    def ingest_hospitals(self):
        """Ingest hospital nodes"""
        print(f"\n{Fore.CYAN}=== Ingesting Hospitals ===")
        for hospital in self.data['hospitals']:
            try:
                self.connector.execute_query(CypherQueries.CREATE_HOSPITAL, hospital)
                print(f"{Fore.GREEN}  ✓ Created hospital: {hospital['name']}")
            except Exception as e:
                print(f"{Fore.RED}  ✗ Failed to create hospital {hospital['id']}: {e}")
    
    def ingest_treatments(self):
        """Ingest treatment nodes"""
        print(f"\n{Fore.CYAN}=== Ingesting Treatments ===")
        for treatment in self.data['treatments']:
            try:
                self.connector.execute_query(CypherQueries.CREATE_TREATMENT, treatment)
                print(f"{Fore.GREEN}  ✓ Created treatment: {treatment['name']}")
            except Exception as e:
                print(f"{Fore.RED}  ✗ Failed to create treatment {treatment['code']}: {e}")
    
    def ingest_medications(self):
        """Ingest medication nodes"""
        print(f"\n{Fore.CYAN}=== Ingesting Medications ===")
        for medication in self.data['medications']:
            try:
                params = {
                    'id': medication['id'],
                    'name': medication['name'],
                    'generic': medication['generic'],
                    'formulary_tier': medication['formulary_tier'],
                    'requires_preauth': medication['requires_preauth']
                }
                self.connector.execute_query(CypherQueries.CREATE_MEDICATION, params)
                print(f"{Fore.GREEN}  ✓ Created medication: {medication['name']}")
            except Exception as e:
                print(f"{Fore.RED}  ✗ Failed to create medication {medication['id']}: {e}")
    
    def ingest_claims(self):
        """Ingest claim nodes"""
        print(f"\n{Fore.CYAN}=== Ingesting Claims ===")
        for claim in self.data['claims']:
            try:
                params = {
                    'id': claim['id'],
                    'status': claim['status'],
                    'amount': claim['amount'],
                    'approved_amount': claim['approved_amount'],
                    'date': claim['date'],
                    'rejection_reason': claim['rejection_reason'],
                    'remaining_eligible': claim['remaining_eligible']
                }
                self.connector.execute_query(CypherQueries.CREATE_CLAIM, params)
                print(f"{Fore.GREEN}  ✓ Created claim: {claim['id']}")
            except Exception as e:
                print(f"{Fore.RED}  ✗ Failed to create claim {claim['id']}: {e}")
    
    def create_customer_policy_relationships(self):
        """Create HAS_POLICY relationships"""
        print(f"\n{Fore.CYAN}=== Creating Customer-Policy Relationships ===")
        
        # Assign each customer a random policy
        for customer in self.data['customers']:
            policy = random.choice(self.data['policies'])
            start_date = (datetime.now() - timedelta(days=random.randint(30, 365))).strftime("%Y-%m-%d")
            end_date = (datetime.now() + timedelta(days=random.randint(30, 365))).strftime("%Y-%m-%d")
            
            params = {
                'customer_id': customer['id'],
                'policy_id': policy['id'],
                'start_date': start_date,
                'end_date': end_date,
                'is_active': True
            }
            
            try:
                self.connector.execute_query(CypherQueries.CREATE_HAS_POLICY_REL, params)
                print(f"{Fore.GREEN}  ✓ {customer['name']} → {policy['plan_type']}")
            except Exception as e:
                print(f"{Fore.RED}  ✗ Failed: {e}")
    
    def create_policy_treatment_relationships(self):
        """Create COVERS relationships"""
        print(f"\n{Fore.CYAN}=== Creating Policy-Treatment Relationships ===")
        
        # Each policy covers all treatments with varying terms
        for policy in self.data['policies']:
            for treatment in self.data['treatments']:
                params = {
                    'policy_id': policy['id'],
                    'treatment_code': treatment['code'],
                    'sub_limit': treatment['sub_limit'],
                    'waiting_period': random.choice([0, 30, 90, 180]),
                    'copay': policy['copay_pct'],
                    'coverage_pct': random.choice([80, 90, 100])
                }
                
                try:
                    self.connector.execute_query(CypherQueries.CREATE_COVERS_REL, params)
                    print(f"{Fore.GREEN}  ✓ {policy['plan_type']} covers {treatment['name']}")
                except Exception as e:
                    print(f"{Fore.RED}  ✗ Failed: {e}")
    
    def create_policy_hospital_relationships(self):
        """Create IN_NETWORK relationships"""
        print(f"\n{Fore.CYAN}=== Creating Policy-Hospital Relationships ===")
        
        # Higher tier policies have more hospitals in network
        for policy in self.data['policies']:
            # Determine how many hospitals based on policy tier
            if "Diamond" in policy['plan_type'] or "Platinum" in policy['plan_type']:
                hospital_count = len(self.data['hospitals'])  # All hospitals
            elif "Gold" in policy['plan_type']:
                hospital_count = int(len(self.data['hospitals']) * 0.8)
            elif "Silver" in policy['plan_type']:
                hospital_count = int(len(self.data['hospitals']) * 0.6)
            else:  # Bronze
                hospital_count = int(len(self.data['hospitals']) * 0.4)
            
            selected_hospitals = random.sample(self.data['hospitals'], min(hospital_count, len(self.data['hospitals'])))
            
            for hospital in selected_hospitals:
                params = {
                    'policy_id': policy['id'],
                    'hospital_id': hospital['id'],
                    'cashless_eligible': True,
                    'tier': hospital['tier'],
                    'discount_pct': random.choice([5, 10, 15, 20])
                }
                
                try:
                    self.connector.execute_query(CypherQueries.CREATE_IN_NETWORK_REL, params)
                    print(f"{Fore.GREEN}  ✓ {policy['plan_type']} → {hospital['name']}")
                except Exception as e:
                    print(f"{Fore.RED}  ✗ Failed: {e}")
    
    def create_policy_medication_relationships(self):
        """Create IN_FORMULARY relationships"""
        print(f"\n{Fore.CYAN}=== Creating Policy-Medication Relationships ===")
        
        # All policies cover all medications but with different coverage percentages
        for policy in self.data['policies']:
            for medication in self.data['medications']:
                # Higher tier policies have better coverage
                if "Diamond" in policy['plan_type'] or "Platinum" in policy['plan_type']:
                    coverage_pct = 100
                elif "Gold" in policy['plan_type']:
                    coverage_pct = 80 if medication['formulary_tier'] == 'Tier-1' else 60
                else:
                    coverage_pct = 70 if medication['formulary_tier'] == 'Tier-1' else 50
                
                params = {
                    'policy_id': policy['id'],
                    'medication_id': medication['id'],
                    'coverage_pct': coverage_pct,
                    'requires_preauth': medication['requires_preauth'],
                    'tier': medication['formulary_tier']
                }
                
                try:
                    self.connector.execute_query(CypherQueries.CREATE_IN_FORMULARY_REL, params)
                    print(f"{Fore.GREEN}  ✓ {policy['plan_type']} → {medication['name']}")
                except Exception as e:
                    print(f"{Fore.RED}  ✗ Failed: {e}")
    
    def create_medication_treatment_relationships(self):
        """Create TREATS relationships"""
        print(f"\n{Fore.CYAN}=== Creating Medication-Treatment Relationships ===")
        
        for medication in self.data['medications']:
            treatment_code = medication['treats_code']
            params = {
                'medication_id': medication['id'],
                'treatment_code': treatment_code,
                'primary': True,
                'effectiveness': random.choice([85, 90, 95])
            }
            
            try:
                self.connector.execute_query(CypherQueries.CREATE_TREATS_REL, params)
                print(f"{Fore.GREEN}  ✓ {medication['name']} treats {treatment_code}")
            except Exception as e:
                print(f"{Fore.RED}  ✗ Failed: {e}")
    
    def create_claim_relationships(self):
        """Create claim relationships (FILED_CLAIM, AT_HOSPITAL, FOR_TREATMENT)"""
        print(f"\n{Fore.CYAN}=== Creating Claim Relationships ===")
        
        for claim in self.data['claims']:
            # FILED_CLAIM
            params = {
                'customer_id': claim['customer_id'],
                'claim_id': claim['id'],
                'claim_date': claim['date'],
                'hospital_id': claim['hospital_id']
            }
            try:
                self.connector.execute_query(CypherQueries.CREATE_FILED_CLAIM_REL, params)
                print(f"{Fore.GREEN}  ✓ Customer {claim['customer_id']} filed claim {claim['id']}")
            except Exception as e:
                print(f"{Fore.RED}  ✗ Failed FILED_CLAIM: {e}")
            
            # AT_HOSPITAL
            params = {
                'claim_id': claim['id'],
                'hospital_id': claim['hospital_id']
            }
            try:
                self.connector.execute_query(CypherQueries.CREATE_AT_HOSPITAL_REL, params)
                print(f"{Fore.GREEN}  ✓ Claim {claim['id']} at hospital {claim['hospital_id']}")
            except Exception as e:
                print(f"{Fore.RED}  ✗ Failed AT_HOSPITAL: {e}")
            
            # FOR_TREATMENT
            params = {
                'claim_id': claim['id'],
                'treatment_code': claim['treatment_code']
            }
            try:
                self.connector.execute_query(CypherQueries.CREATE_FOR_TREATMENT_REL, params)
                print(f"{Fore.GREEN}  ✓ Claim {claim['id']} for treatment {claim['treatment_code']}")
            except Exception as e:
                print(f"{Fore.RED}  ✗ Failed FOR_TREATMENT: {e}")
    
    def run_full_ingestion(self, clear_existing: bool = False):
        """Run complete data ingestion pipeline"""
        print(f"\n{Fore.MAGENTA}{'='*60}")
        print(f"{Fore.MAGENTA}MedAssist Knowledge Graph Data Ingestion")
        print(f"{Fore.MAGENTA}{'='*60}")
        
        if clear_existing:
            print(f"\n{Fore.RED}⚠ Clearing existing data...")
            self.connector.clear_database()
        
        # Setup
        self.setup_schema()
        self.load_data()
        
        # Ingest nodes
        self.ingest_customers()
        self.ingest_policies()
        self.ingest_hospitals()
        self.ingest_treatments()
        self.ingest_medications()
        self.ingest_claims()
        
        # Create relationships
        self.create_customer_policy_relationships()
        self.create_policy_treatment_relationships()
        self.create_policy_hospital_relationships()
        self.create_policy_medication_relationships()
        self.create_medication_treatment_relationships()
        self.create_claim_relationships()
        
        # Summary
        print(f"\n{Fore.MAGENTA}{'='*60}")
        print(f"{Fore.GREEN}✓ Data Ingestion Complete!")
        print(f"{Fore.MAGENTA}{'='*60}")
        
        node_counts = self.connector.get_node_count()
        rel_count = self.connector.get_relationship_count()
        
        print(f"\n{Fore.CYAN}=== Graph Statistics ===")
        print(f"{Fore.YELLOW}Nodes:")
        for label, count in node_counts.items():
            print(f"  {label}: {count}")
        print(f"{Fore.YELLOW}Total Relationships: {rel_count}")


if __name__ == "__main__":
    # Run ingestion
    connector = Neo4jConnector()
    
    if connector.connect():
        ingestor = DataIngestor(connector)
        ingestor.run_full_ingestion(clear_existing=True)
        connector.close()
    else:
        print(f"{Fore.RED}Failed to connect to Neo4j. Please check your credentials.")
