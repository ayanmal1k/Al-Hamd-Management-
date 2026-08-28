import os
import sys

# Ensure app is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'app')))

os.environ['TESTING'] = '1'

from database import init_db, db_session, DB_PATH
from services.booker_service import create_booker
from services.customer_service import create_customer, get_customer_by_id
from services.transaction_service import add_transaction, update_transaction, delete_transaction

def setup_test_db():
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
    init_db()

def test_dynamic_balance():
    setup_test_db()
    
    # 1. Create a Booker
    booker_id = create_booker("Ahmed")
    
    # 2. Create a Customer with opening balance Rs. 20,000
    customer_id = create_customer("Ahmed Store", None, None, booker_id, "2026-08-28", 2000000) # 20,000 Rs
    
    customer = get_customer_by_id(customer_id)
    assert customer['current_due'] == 2000000, f"Expected 20,000, got {customer['current_due'] / 100}"
    
    # 3. Add a Bill of Rs. 50,000
    bill_id = add_transaction(customer_id, booker_id, 'Bill', 5000000, "2026-08-28")
    
    customer = get_customer_by_id(customer_id)
    assert customer['current_due'] == 7000000, f"Expected 70,000, got {customer['current_due'] / 100}"
    
    # 4. Add a Recovery of Rs. 10,000
    rec_id = add_transaction(customer_id, booker_id, 'Recovery', 1000000, "2026-08-29")
    
    customer = get_customer_by_id(customer_id)
    assert customer['current_due'] == 6000000, f"Expected 60,000, got {customer['current_due'] / 100}"
    
    # 5. Add another Bill of Rs. 15,000
    bill2_id = add_transaction(customer_id, booker_id, 'Bill', 1500000, "2026-08-30")
    
    customer = get_customer_by_id(customer_id)
    assert customer['current_due'] == 7500000, f"Expected 75,000, got {customer['current_due'] / 100}"
    
    # 6. Edit the first bill (50,000 -> 40,000)
    update_transaction(bill_id, 4000000, "2026-08-28")
    
    customer = get_customer_by_id(customer_id)
    assert customer['current_due'] == 6500000, f"Expected 65,000, got {customer['current_due'] / 100}"
    
    # 7. Delete the recovery
    delete_transaction(rec_id)
    
    customer = get_customer_by_id(customer_id)
    assert customer['current_due'] == 7500000, f"Expected 75,000, got {customer['current_due'] / 100}"
    
    print("All balance recalculation tests passed successfully!")

if __name__ == "__main__":
    test_dynamic_balance()
