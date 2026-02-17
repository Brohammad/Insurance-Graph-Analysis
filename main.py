"""
MedAssist Healthcare Insurance Knowledge Graph - Main Application
Interactive CLI for querying the knowledge graph
"""
from neo4j_connector import Neo4jConnector, get_connector
from queries import QueryBuilder
from test_queries import QueryTester
from ingest import DataIngestor
from colorama import Fore, Style, init
import sys

init(autoreset=True)


class MedAssistApp:
    """Main application class"""
    
    def __init__(self):
        self.connector = None
        self.running = False
    
    def print_banner(self):
        """Print application banner"""
        print(f"\n{Fore.CYAN}{'='*70}")
        print(f"{Fore.CYAN}  MedAssist Healthcare Insurance - Knowledge Graph System")
        print(f"{Fore.CYAN}  Powered by Neo4j + LangGraph + Gemini 2.0 Flash")
        print(f"{Fore.CYAN}{'='*70}\n")
    
    def print_menu(self):
        """Print main menu"""
        print(f"\n{Fore.YELLOW}Main Menu:")
        print(f"{Fore.GREEN}  1. {Fore.WHITE}Initialize Database (Setup + Ingest Data)")
        print(f"{Fore.GREEN}  2. {Fore.WHITE}Run Test Queries (Validate Knowledge Graph)")
        print(f"{Fore.GREEN}  3. {Fore.WHITE}Check Coverage (Treatment at Hospital)")
        print(f"{Fore.GREEN}  4. {Fore.WHITE}Find Network Hospitals")
        print(f"{Fore.GREEN}  5. {Fore.WHITE}View Claim History")
        print(f"{Fore.GREEN}  6. {Fore.WHITE}Check Policy Utilization")
        print(f"{Fore.GREEN}  7. {Fore.WHITE}Check Medication Coverage")
        print(f"{Fore.GREEN}  8. {Fore.WHITE}Database Statistics")
        print(f"{Fore.GREEN}  9. {Fore.WHITE}Clear Database (CAUTION)")
        print(f"{Fore.RED}  0. {Fore.WHITE}Exit")
        print()
    
    def initialize_database(self):
        """Initialize database with schema and data"""
        print(f"\n{Fore.YELLOW}Initializing database...")
        confirm = input(f"{Fore.RED}This will clear existing data. Continue? (yes/no): ").strip().lower()
        
        if confirm == 'yes':
            ingestor = DataIngestor(self.connector)
            ingestor.run_full_ingestion(clear_existing=True)
            print(f"\n{Fore.GREEN}✓ Database initialized successfully!")
        else:
            print(f"{Fore.BLUE}Operation cancelled")
    
    def run_test_queries(self):
        """Run all test queries"""
        print(f"\n{Fore.YELLOW}Running test query suite...")
        tester = QueryTester(self.connector)
        tester.run_all_tests()
    
    def check_coverage(self):
        """Interactive coverage check"""
        print(f"\n{Fore.CYAN}=== Coverage Check ===")
        customer_id = input(f"{Fore.YELLOW}Enter Customer ID (e.g., CUST0001): ").strip()
        treatment_code = input(f"{Fore.YELLOW}Enter Treatment Code (e.g., E11 for Diabetes): ").strip()
        hospital_id = input(f"{Fore.YELLOW}Enter Hospital ID (e.g., HOSP0001): ").strip()
        
        query = QueryBuilder.check_coverage(customer_id, treatment_code, hospital_id)
        results = self.connector.execute_query(query, {
            'customer_id': customer_id,
            'treatment_code': treatment_code,
            'hospital_id': hospital_id
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
                print(f"  Estimated Cost: ₹{result['estimated_cost']:,}")
        else:
            print(f"\n{Fore.RED}✗ No coverage found or hospital not in network")
    
    def find_network_hospitals(self):
        """Interactive hospital finder"""
        print(f"\n{Fore.CYAN}=== Network Hospital Finder ===")
        customer_id = input(f"{Fore.YELLOW}Enter Customer ID (e.g., CUST0001): ").strip()
        city = input(f"{Fore.YELLOW}Enter City (optional, press Enter to skip): ").strip() or None
        
        query = QueryBuilder.find_network_hospitals(customer_id, city)
        params = {'customer_id': customer_id}
        if city:
            params['city'] = city
        
        results = self.connector.execute_query(query, params)
        
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
            print(f"\n{Fore.RED}✗ No in-network hospitals found")
    
    def view_claim_history(self):
        """Interactive claim history viewer"""
        print(f"\n{Fore.CYAN}=== Claim History ===")
        customer_id = input(f"{Fore.YELLOW}Enter Customer ID (e.g., CUST0001): ").strip()
        limit = input(f"{Fore.YELLOW}Number of claims to show (default 10): ").strip() or "10"
        
        query = QueryBuilder.get_claim_history(customer_id, int(limit))
        results = self.connector.execute_query(query, {'customer_id': customer_id, 'limit': int(limit)})
        
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
                print(f"    Hospital: {claim['hospital_name']}")
                print(f"    Treatment: {claim['treatment_name']}")
                print(f"    Date: {claim['claim_date']}")
        else:
            print(f"\n{Fore.YELLOW}No claims found for this customer")
    
    def check_policy_utilization(self):
        """Interactive policy utilization check"""
        print(f"\n{Fore.CYAN}=== Policy Utilization ===")
        customer_id = input(f"{Fore.YELLOW}Enter Customer ID (e.g., CUST0001): ").strip()
        
        query = QueryBuilder.get_policy_utilization(customer_id)
        results = self.connector.execute_query(query, {'customer_id': customer_id})
        
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
        else:
            print(f"\n{Fore.RED}✗ No active policy found")
    
    def check_medication_coverage(self):
        """Interactive medication coverage check"""
        print(f"\n{Fore.CYAN}=== Medication Coverage ===")
        customer_id = input(f"{Fore.YELLOW}Enter Customer ID (e.g., CUST0001): ").strip()
        medication_name = input(f"{Fore.YELLOW}Enter Medication Name (e.g., Metformin): ").strip()
        
        query = QueryBuilder.check_medication_coverage(customer_id, medication_name)
        results = self.connector.execute_query(query, {
            'customer_id': customer_id,
            'medication_name': medication_name
        })
        
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
            print(f"\n{Fore.RED}✗ Medication not covered under policy")
    
    def show_statistics(self):
        """Show database statistics"""
        print(f"\n{Fore.CYAN}=== Database Statistics ===")
        
        node_counts = self.connector.get_node_count()
        rel_count = self.connector.get_relationship_count()
        
        print(f"\n{Fore.YELLOW}Node Counts:")
        total_nodes = 0
        for label, count in node_counts.items():
            print(f"  {label}: {count}")
            total_nodes += count
        
        print(f"\n{Fore.YELLOW}Total Nodes: {total_nodes}")
        print(f"{Fore.YELLOW}Total Relationships: {rel_count}")
        
        schema_info = self.connector.verify_schema()
        print(f"\n{Fore.YELLOW}Schema:")
        print(f"  Constraints: {schema_info['constraints']}")
        print(f"  Indexes: {schema_info['indexes']}")
    
    def clear_database(self):
        """Clear all data from database"""
        print(f"\n{Fore.RED}⚠ WARNING: This will delete ALL data from the database!")
        confirm = input(f"{Fore.RED}Type 'DELETE' to confirm: ").strip()
        
        if confirm == 'DELETE':
            self.connector.clear_database()
            print(f"\n{Fore.GREEN}✓ Database cleared")
        else:
            print(f"{Fore.BLUE}Operation cancelled")
    
    def run(self):
        """Run the main application loop"""
        self.print_banner()
        
        # Connect to Neo4j
        print(f"{Fore.YELLOW}Connecting to Neo4j...")
        self.connector = Neo4jConnector()
        
        if not self.connector.connect():
            print(f"{Fore.RED}✗ Failed to connect to Neo4j. Exiting.")
            return
        
        print(f"{Fore.GREEN}✓ Connected to Neo4j successfully!")
        
        self.running = True
        
        while self.running:
            try:
                self.print_menu()
                choice = input(f"{Fore.CYAN}Enter your choice: ").strip()
                
                if choice == '1':
                    self.initialize_database()
                elif choice == '2':
                    self.run_test_queries()
                elif choice == '3':
                    self.check_coverage()
                elif choice == '4':
                    self.find_network_hospitals()
                elif choice == '5':
                    self.view_claim_history()
                elif choice == '6':
                    self.check_policy_utilization()
                elif choice == '7':
                    self.check_medication_coverage()
                elif choice == '8':
                    self.show_statistics()
                elif choice == '9':
                    self.clear_database()
                elif choice == '0':
                    print(f"\n{Fore.BLUE}Exiting...")
                    self.running = False
                else:
                    print(f"\n{Fore.RED}Invalid choice. Please try again.")
                
                if self.running and choice != '0':
                    input(f"\n{Fore.CYAN}Press Enter to continue...")
            
            except KeyboardInterrupt:
                print(f"\n\n{Fore.BLUE}Interrupted by user. Exiting...")
                self.running = False
            except Exception as e:
                print(f"\n{Fore.RED}✗ Error: {e}")
                input(f"\n{Fore.CYAN}Press Enter to continue...")
        
        # Cleanup
        if self.connector:
            self.connector.close()
        
        print(f"\n{Fore.GREEN}Thank you for using MedAssist Knowledge Graph System!")


def main():
    """Main entry point"""
    app = MedAssistApp()
    app.run()


if __name__ == "__main__":
    main()
