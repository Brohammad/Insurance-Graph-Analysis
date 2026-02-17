"""
Seed Data Generator for MedAssist Healthcare Insurance Knowledge Graph
Generates realistic sample data for customers, policies, hospitals, treatments, medications, and claims
"""
from datetime import datetime, timedelta
import random

# Sample data pools
INDIAN_FIRST_NAMES = [
    "Rajesh", "Priya", "Amit", "Sneha", "Vikram", "Ananya", "Rohan", "Kavya", 
    "Arjun", "Meera", "Karan", "Pooja", "Sanjay", "Neha", "Aditya"
]

INDIAN_LAST_NAMES = [
    "Sharma", "Patel", "Kumar", "Singh", "Reddy", "Nair", "Iyer", "Gupta",
    "Verma", "Rao", "Desai", "Mehta", "Joshi", "Menon", "Pillai"
]

CITIES = [
    "Bangalore", "Mumbai", "Delhi", "Chennai", "Hyderabad", "Pune", 
    "Kolkata", "Ahmedabad", "Jaipur", "Lucknow"
]

PRE_EXISTING_CONDITIONS = [
    "Diabetes", "Hypertension", "Asthma", "Thyroid", "Heart Disease", 
    "Arthritis", None, None, None  # None means no pre-existing condition
]

POLICY_TYPES = [
    {"plan": "Bronze Basic", "sum_insured": 300000, "copay": 30, "premium": 8000, "deductible": 5000},
    {"plan": "Silver Shield", "sum_insured": 500000, "copay": 20, "premium": 15000, "deductible": 3000},
    {"plan": "Gold Shield", "sum_insured": 1000000, "copay": 20, "premium": 25000, "deductible": 2000},
    {"plan": "Platinum Plus", "sum_insured": 1500000, "copay": 10, "premium": 40000, "deductible": 1000},
    {"plan": "Diamond Elite", "sum_insured": 2500000, "copay": 0, "premium": 70000, "deductible": 0},
]

HOSPITALS = [
    {"name": "Apollo", "cities": ["Bangalore", "Mumbai", "Delhi", "Chennai", "Hyderabad"], "tier": "Tier-1"},
    {"name": "Fortis", "cities": ["Mumbai", "Delhi", "Bangalore", "Pune"], "tier": "Tier-1"},
    {"name": "Manipal", "cities": ["Bangalore", "Delhi", "Jaipur"], "tier": "Tier-1"},
    {"name": "Max Healthcare", "cities": ["Delhi", "Mumbai", "Pune"], "tier": "Tier-1"},
    {"name": "Narayana Health", "cities": ["Bangalore", "Kolkata", "Ahmedabad"], "tier": "Tier-2"},
    {"name": "Cloudnine", "cities": ["Bangalore", "Mumbai", "Pune"], "tier": "Tier-2"},
    {"name": "Artemis", "cities": ["Delhi", "Jaipur"], "tier": "Tier-2"},
    {"name": "Columbia Asia", "cities": ["Bangalore", "Pune"], "tier": "Tier-2"},
]

TREATMENTS = [
    {"code": "E11", "category": "Diabetes Management", "name": "Type 2 Diabetes Treatment", "avg_cost": 50000, "sub_limit": 75000, "preauth": False},
    {"code": "I10", "category": "Cardiovascular", "name": "Hypertension Treatment", "avg_cost": 30000, "sub_limit": 50000, "preauth": False},
    {"code": "M17", "category": "Orthopedic", "name": "Knee Surgery", "avg_cost": 250000, "sub_limit": 300000, "preauth": True},
    {"code": "Z01", "category": "Preventive", "name": "Annual Health Checkup", "avg_cost": 5000, "sub_limit": 10000, "preauth": False},
    {"code": "J45", "category": "Respiratory", "name": "Asthma Treatment", "avg_cost": 25000, "sub_limit": 40000, "preauth": False},
    {"code": "C50", "category": "Oncology", "name": "Breast Cancer Treatment", "avg_cost": 500000, "sub_limit": 1000000, "preauth": True},
    {"code": "I21", "category": "Cardiovascular", "name": "Heart Attack Treatment", "avg_cost": 400000, "sub_limit": 600000, "preauth": True},
    {"code": "O80", "category": "Maternity", "name": "Normal Delivery", "avg_cost": 50000, "sub_limit": 75000, "preauth": False},
    {"code": "O82", "category": "Maternity", "name": "Caesarean Section", "avg_cost": 80000, "sub_limit": 100000, "preauth": True},
    {"code": "S06", "category": "Emergency", "name": "Head Injury Treatment", "avg_cost": 150000, "sub_limit": 200000, "preauth": False},
]

MEDICATIONS = [
    {"name": "Metformin", "generic": "Metformin", "formulary_tier": "Tier-1", "treats": "E11", "preauth": False},
    {"name": "Insulin Glargine", "generic": "Insulin", "formulary_tier": "Tier-2", "treats": "E11", "preauth": True},
    {"name": "Amlodipine", "generic": "Amlodipine", "formulary_tier": "Tier-1", "treats": "I10", "preauth": False},
    {"name": "Losartan", "generic": "Losartan", "formulary_tier": "Tier-1", "treats": "I10", "preauth": False},
    {"name": "Salbutamol", "generic": "Albuterol", "formulary_tier": "Tier-1", "treats": "J45", "preauth": False},
    {"name": "Budesonide", "generic": "Budesonide", "formulary_tier": "Tier-2", "treats": "J45", "preauth": False},
    {"name": "Paracetamol", "generic": "Acetaminophen", "formulary_tier": "Tier-1", "treats": "S06", "preauth": False},
    {"name": "Trastuzumab", "generic": "Herceptin", "formulary_tier": "Tier-3", "treats": "C50", "preauth": True},
]

CLAIM_STATUSES = ["Approved", "Partially Approved", "Rejected", "Under Review", "Pending"]

REJECTION_REASONS = [
    "Exceeded sub-limit for room rent",
    "Treatment not covered under policy",
    "Pre-authorization not obtained",
    "Waiting period not completed",
    "Hospital not in network",
    None  # For approved claims
]


def generate_customers(count: int = 10):
    """Generate sample customer data"""
    customers = []
    for i in range(1, count + 1):
        first_name = random.choice(INDIAN_FIRST_NAMES)
        last_name = random.choice(INDIAN_LAST_NAMES)
        customer = {
            "id": f"CUST{i:04d}",
            "name": f"{first_name} {last_name}",
            "age": random.randint(25, 65),
            "city": random.choice(CITIES),
            "pre_existing": random.choice(PRE_EXISTING_CONDITIONS),
            "phone": f"+91{random.randint(7000000000, 9999999999)}",
            "email": f"{first_name.lower()}.{last_name.lower()}@example.com"
        }
        customers.append(customer)
    return customers


def generate_policies(count: int = 5):
    """Generate sample policy data"""
    policies = []
    for i, policy_type in enumerate(POLICY_TYPES[:count], 1):
        policy = {
            "id": f"POL{i:04d}",
            "plan_type": policy_type["plan"],
            "sum_insured": policy_type["sum_insured"],
            "copay_pct": policy_type["copay"],
            "renewal_date": (datetime.now() + timedelta(days=random.randint(30, 365))).strftime("%Y-%m-%d"),
            "premium": policy_type["premium"],
            "deductible": policy_type["deductible"]
        }
        policies.append(policy)
    return policies


def generate_hospitals():
    """Generate sample hospital data"""
    hospitals = []
    hospital_id = 1
    for hospital in HOSPITALS:
        for city in hospital["cities"]:
            hosp = {
                "id": f"HOSP{hospital_id:04d}",
                "name": f"{hospital['name']} {city}",
                "city": city,
                "tier": hospital["tier"],
                "cashless_enabled": True,
                "address": f"{random.randint(1, 99)} {hospital['name']} Road, {city}",
                "specialties": random.sample(["Cardiology", "Orthopedics", "Oncology", "Neurology", "Pediatrics"], k=3)
            }
            hospitals.append(hosp)
            hospital_id += 1
    return hospitals


def generate_treatments():
    """Generate sample treatment data"""
    return [
        {
            "code": t["code"],
            "category": t["category"],
            "name": t["name"],
            "avg_cost": t["avg_cost"],
            "sub_limit": t["sub_limit"],
            "requires_preauth": t["preauth"]
        }
        for t in TREATMENTS
    ]


def generate_medications():
    """Generate sample medication data"""
    medications = []
    for i, med in enumerate(MEDICATIONS, 1):
        medication = {
            "id": f"MED{i:04d}",
            "name": med["name"],
            "generic": med["generic"],
            "formulary_tier": med["formulary_tier"],
            "requires_preauth": med["preauth"],
            "treats_code": med["treats"]
        }
        medications.append(medication)
    return medications


def generate_claims(customers, hospitals, treatments, count: int = 15):
    """Generate sample claim data"""
    claims = []
    for i in range(1, count + 1):
        customer = random.choice(customers)
        hospital = random.choice(hospitals)
        treatment = random.choice(treatments)
        status = random.choice(CLAIM_STATUSES)
        
        amount = random.randint(int(treatment["avg_cost"] * 0.7), int(treatment["avg_cost"] * 1.3))
        
        if status == "Approved":
            approved_amount = amount
            rejection_reason = None
            remaining_eligible = 0
        elif status == "Partially Approved":
            approved_amount = int(amount * random.uniform(0.5, 0.9))
            rejection_reason = random.choice([r for r in REJECTION_REASONS if r is not None])
            remaining_eligible = amount - approved_amount
        elif status == "Rejected":
            approved_amount = 0
            rejection_reason = random.choice([r for r in REJECTION_REASONS if r is not None])
            remaining_eligible = amount
        else:  # Under Review or Pending
            approved_amount = 0
            rejection_reason = None
            remaining_eligible = 0
        
        claim = {
            "id": f"CLM{i:04d}",
            "status": status,
            "amount": amount,
            "approved_amount": approved_amount,
            "date": (datetime.now() - timedelta(days=random.randint(1, 180))).strftime("%Y-%m-%d"),
            "rejection_reason": rejection_reason,
            "remaining_eligible": remaining_eligible,
            "customer_id": customer["id"],
            "hospital_id": hospital["id"],
            "treatment_code": treatment["code"]
        }
        claims.append(claim)
    return claims


def generate_all_data():
    """Generate complete dataset"""
    customers = generate_customers(10)
    policies = generate_policies(5)
    hospitals = generate_hospitals()
    treatments = generate_treatments()
    medications = generate_medications()
    claims = generate_claims(customers, hospitals, treatments, 15)
    
    return {
        "customers": customers,
        "policies": policies,
        "hospitals": hospitals,
        "treatments": treatments,
        "medications": medications,
        "claims": claims
    }


if __name__ == "__main__":
    # Test data generation
    data = generate_all_data()
    print(f"Generated {len(data['customers'])} customers")
    print(f"Generated {len(data['policies'])} policies")
    print(f"Generated {len(data['hospitals'])} hospitals")
    print(f"Generated {len(data['treatments'])} treatments")
    print(f"Generated {len(data['medications'])} medications")
    print(f"Generated {len(data['claims'])} claims")
    
    # Print sample
    print("\nSample Customer:", data['customers'][0])
    print("Sample Policy:", data['policies'][0])
    print("Sample Hospital:", data['hospitals'][0])
    print("Sample Claim:", data['claims'][0])
