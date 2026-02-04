from src.domain.models import User
from src.db.repository import dbFunctions
class SalesFunctions:
    def __init__(self, user:User,db:dbFunctions):
        self.userinf = user
        self.db = db


    def sales_page(self):
        while True:
            print("\n\n\n========= Main Menue (Sales) =========")
            print("\n========= Please select what you want to do =========")
            print("1. Update product information")
            print("2. Weekly sales report (last 7 days)")
            print("3. Top products (by distinct orders & by views)")
            print("4. Logout")
            print("5.Exit program")
            print("===========================")
            choice = input("Please enter your choice: ").strip()
            if choice == "1":
                self.update_product_flow()
            elif choice == "2":
                self.show_weekly_report()
            elif choice == "3":
                self.show_top_products()
            elif choice == "4":
                print("\nSee you next time!")
                return 
            elif choice =="5":
                print("\nExting program......")
                sys.exit(0)  
            else:
                print("\n[X] Invalid input! Please select 1,2,3,4")

    def update_product_flow(self):
        # --- PID: loop until a valid integer pid that exists; allow 'q' to cancel ---
        while True:
            pid_in = input("Enter product id to view/update (q to cancel): ").strip().lower()
            if pid_in == "q":
                print("[...] Cancelled.")
                return
            if not pid_in.isdigit():
                print("[X] pid must be a positive integer. Try again.")
                continue
            pid = int(pid_in)
            row = self.db.get_product_by_pid(pid)
            if row is None:
                print("[X] No such product. Try another pid.")
                continue
            break

        print("\nCurrent product info:")
        print(f"PID: {pid}\nName: {row['name']}\nCategory: {row['category']}\n"
            f"Price: {row['price']}\nStock: {row['stock_count']}\nDescr: {row['descr']}")

        # --- Update price: loop until valid float >= 0 or blank to skip; 'q' cancels whole flow ---
        while True:
            np = input("Enter new price (blank to skip, q to cancel): ").strip().lower()
            if np == "":
                break  # skip price update
            if np == "q":
                print("[...] Cancelled."); return
            try:
                npv = float(np)
                if npv < 0:
                    print("[X] Price cannot be negative. Try again.")
                    continue
                if self.db.update_product_price(pid, npv):
                    print("[✓] Price updated.")
                break
            except ValueError:
                print("[X] Invalid price (must be a number). Try again.")

        # --- Update stock: loop until valid non-negative integer or blank to skip; 'q' cancels ---
        while True:
            ns = input("Enter new stock (integer, blank to skip, q to cancel): ").strip().lower()
            if ns == "":
                break  # skip stock update
            if ns == "q":
                print("[...] Cancelled."); return
            if ns.isdigit():
                nsv = int(ns)
                if self.db.update_product_stock(pid, nsv):
                    print("[✓] Stock updated.")
                break
            else:
                print("[X] Invalid stock (must be a non-negative integer). Try again.")

    def show_weekly_report(self):
        metrics = self.db.weekly_sales_metrics()
        if not metrics:
            print("[X] Could not compute weekly sales metrics.")
            return
        print("\n===== Weekly Sales Report (last 7 days inclusive) =====")
        print(f"Distinct orders:           {metrics['orders']}")
        print(f"Distinct products sold:    {metrics['products']}")
        print(f"Distinct customers:        {metrics['customers']}")
        print(f"Avg spent per customer:    {metrics['avg_per_customer']}")
        print(f"Total sales amount:        {metrics['total_sales']}")

    def show_top_products(self):
        print("\n===== Top by Distinct Orders (with ties at rank 3) =====")
        ords = self.db.top_products_by_distinct_orders()
        if not ords:
            print("(no data)")
        else:
            for i, r in enumerate(ords, start=1):
                print(f"{i}. PID {r['pid']}  {r['name']}  orders={r['count']}")

        print("\n===== Top by Views (with ties at rank 3) =====")
        views = self.db.top_products_by_views()
        if not views:
            print("(no data)")
        else:
            for i, r in enumerate(views, start=1):
                print(f"{i}. PID {r['pid']}  {r['name']}  views={r['count']}")
# --- END SalesFunctions --------------------------------------------------
