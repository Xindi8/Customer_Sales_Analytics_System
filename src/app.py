import sys
import os

from src.db.connection import create_connection
from src.db.repository import dbFunctions
from src.services.auth_service import login, register
from src.services.customer_service import customerFunctions
from src.services.sales_service import SalesFunctions




def main():
    if len(sys.argv) < 2:
        print("\n[X] Missing database file name!")
        print("Usage: python src/app.py data/store.db")
        sys.exit(1)

    db_path = sys.argv[1]
    if not os.path.exists(db_path):
        print(f"\n[X] Database file not found: {db_path}")
        sys.exit(1)

    print(">>> Program started successfully!")
    print(f"\n[✓] Connected to database: {db_path}")

    conn = create_connection(db_path)
    repo = dbFunctions(conn)

    while True:
        print("\n========= Login Page =========")
        print("1. Login")
        print("2. Register")
        print("3. Exit")
        print("===========================")

        choice = input("Please enter your choice: ").strip()

        if choice == "1":
            user = login(repo)
            if not user:
                continue

            if user.role == "customer":
                cust = customerFunctions(user, repo)
                result = cust.customer_page()
                if result == "Logout":
                    continue
            elif user.role == "sales":
                sales = SalesFunctions(user, repo)
                sales.sales_page()

        elif choice == "2":
            reg_user = register(repo)
            if reg_user:
                cust = customerFunctions(reg_user, repo)
                result = cust.customer_page()
                if result == "Logout":
                    continue

        elif choice == "3":
            print("\n[...] Exiting program. Thank you for using this program!")
            repo.close()
            break

        else:
            print("\n[X] Invalid input!Please select 1,2,3")

if __name__ == "__main__":
    main()
