import sqlite3
import datetime as dt
from typing import Optional, List, Dict, Any

from src.domain.models import User, SessionInf

class dbFunctions:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def close(self):
        try:
            self.conn.close()
        except sqlite3.Error as e:
            print("\n[X] SQL Error in close database!\n")
            print(e)

    def commit(self):
        try:
            self.conn.commit()
        except sqlite3.Error as e:
            print("\n[X] SQL Error in update database!\n")
            print(e)
    #   Retrieve the next available user ID.
    #   Returns:
    #           int: Next uid (max(uid)+1) or 1 if table is empty.
    def get_max_uid(self):

        try:
            cur = self.conn.execute("SELECT MAX(uid) FROM users;")
            rs = cur.fetchone()[0]
        except sqlite3.Error as e:
            print("\n[X] SQL Error in get_max_uid()\n")
            print(e)
        
        if rs is None:
            uid = 1
        else:
            uid = rs + 1
        return uid

    #   Retrieve the next available session number for a customer.
    #   Args:
    #       cid (int): Customer ID.
    #   Returns:
    #           int: Next session number (max+1) or 1 if first login.
    def get_max_sessionNo(self,cid):

        try:
            cur = self.conn.execute("SELECT MAX(sessionNo) FROM sessions WHERE cid = ?;",(cid,))
            rs = cur.fetchone()[0]
        except sqlite3.Error as e:
            print("\n[X] SQL Error in get_max_sessionNo()\n")
            print(e)

        if rs is None:
            sessionNo = 1
        else:
            sessionNo = rs + 1
        return sessionNo
    
   
    #   Retrieve the next available order number.
    #   Returns:
    #           int: Next order number (max+1) or 1 if table is empty.
    def get_max_orderNo(self):

        try:
            cur = self.conn.execute("SELECT MAX(ono) FROM orders;")
            rs = cur.fetchone()[0]
        except sqlite3.Error as e:
            print("\n[X] SQL Error in get_max_orderNo()\n")
            print(e)
        
        if rs is None:
            ono = 1
        else:
            ono = rs + 1
        return ono
   
    #   Get basic user information (uid, password, role).
    #   Args:
    #       uid (int): User ID.
    #   Returns:
    #           sqlite3.Row: A row containing user info or None if not found.
    def get_user_inf(self,uid):

        try:
            cur = self.conn.execute("SELECT uid, pwd, role FROM users WHERE uid = ?;", (uid,))
        except sqlite3.Error as e:
            print("\n[X] SQL Error in get_user_inf()\n")
            print(e)
        return cur.fetchone()
    
    #   Get customer name by customer ID.
    #   Args:
    #       uid (int): Customer ID.
    #   Returns:
    #           sqlite3.Row: A row containing customer info or None if not found.
    def get_customer_inf(self,uid):

        try:
            cur = self.conn.execute("SELECT name FROM customers WHERE cid = ?;", (uid,))
        except sqlite3.Error as e:
            print("\n[X] SQL Error in get_customer_inf()\n")
            print(e)
        return cur.fetchone()
    
    #   Verify user credentials.
    #   Args:
    #       uid (int): User ID to verify.
    #   Returns:
    #           User: A User object with uid, name, role, and password (plain text).
    def login_verify(self,uid):
        
        #   Get related user information according to entered uid
        rs = self.get_user_inf(uid)

        #   If uid does not have related user
        if rs is None:
            return None

        pw = rs["pwd"]              #   Plain-text password from DB
        role = rs["role"].lower()
        name = 'Sales'              #   Default for salesperson

        #   Retrieve customer name if role is 'customer'
        if role == 'customer':
            #   Get customer information
            rs2 = self.get_customer_inf(uid)
            name = rs2["name"]

        return User(uid = uid, name = name, role = role, psw = pw)
    
    #   Check if an email already exists in the customers table.
    #   Args:
    #       email (str): Email address to check.
    #   Returns:
    #           sqlite3.Row or None: Existing customer record if found.
    def check_email(self,email):
        
        try:
            cur = self.conn.execute("SELECT cid FROM customers WHERE LOWER(email) = ?;", (email,))
        except sqlite3.Error as e:
            print("\n[X] SQL Error in check_email()\n")
            print(e)

        return cur.fetchone()
    
    #   Register a new customer by inserting into both 'users' and 'customers'.
    #   Args:
    #       userName (str): Customer name.
    #       email (str): Email address.
    #       password (str): Plain-text password (per TA’s requirement).
    #   Returns:
    #           User: Newly created User object.
    def insert_customer(self,userName,email,password):

        #   Get uid
        uid = self.get_max_uid()
        role = 'customer'       #   Default set role as customer
        try:
            #   Insert user login info
            cur = self.conn.execute("INSERT INTO users (uid,pwd,role) VALUES (?,?,?);", (uid,password,role))
            #  Insert customer info
            cur = self.conn.execute("INSERT INTO customers (cid,name,email) VALUES (?,?,?);", (uid,userName,email,))
            self.commit()
        except sqlite3.Error as e:
            print("\n[X] SQL Error in insert_customer()\n")
            print(e)
            self.conn.rollback()

        return User(uid = uid, name = userName, role = role, psw = password)

    #   Create a new session record for the given customer.
    #   The end_time remains NULL until logout.
    #   Args:
    #       cid (int): Customer ID.
    #   Returns:
    #           SessionInf: Session object with cid and sessionNo.
    def create_session(self,cid):
        
        #   Set up all required values before insert into sessions tables
        ts = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        session = self.get_max_sessionNo(cid)
        try:
            cur = self.conn.execute("INSERT INTO sessions (cid,sessionNo,start_time,end_time) VALUES (?,?,?,NULL);",(cid,session,ts,))
            self.commit()
        except sqlite3.Error as e:
            print("\n[X] SQL Error in create_session()\n")
            print(e)
            self.conn.rollback()            
        return SessionInf(cid = cid,sessionNo = session)
    
    #   Update the end_time for the specified session (called at logout).
    #   Args:
    #       sessionInformation (SessionInf): Object with cid and sessionNo.
    def update_session(self,sessionInformation):
         
        ts = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        session = sessionInformation.sessionNo
        cid = sessionInformation.cid
        try:
            cur = self.conn.execute("UPDATE sessions SET end_time = ? where cid = ? AND sessionNo = ? ;",(ts,cid,session,))
            self.commit()
        except sqlite3.Error as e:
            print("\n[X] SQL Error in update_session()\n")
            self.conn.rollback()
            print(e)

    #   Record a customer's search activity in the 'search' table.
    #   Args:
    #       search (str): Search query string.
    #       sessionInformation (SessionInf): Current session details.
    def create_search(self,search,sessionInformation):
        
        ts = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            cur = self.conn.execute("INSERT INTO search (cid,sessionNo,ts,query) VALUES (?,?,?,?);",(sessionInformation.cid,sessionInformation.sessionNo,ts,search))
            self.commit()
        except sqlite3.Error as e:
            print("\n[X]SQL Error in create_search()\n")
            self.conn.rollback()
            print(e)

    #   Perform a case-insensitive keyword search on products.
    #   Records the search in the database.
    #   Args:
    #       conditions (list): List of SQL WHERE conditions.
    #       params (list): List of parameters for prepared statement.
    #       sessionInformation (SessionInf): Current session info.
    #   Returns:
    #          list[sqlite3.Row]: Matching product records.
    def search_product(self,conditions,params,sessionInformation):

        words = " ".join([p.strip('%') for p in params[::2]])
        self.create_search(words,sessionInformation)
        where_clause = " AND ".join(conditions)

        sql = (
            "SELECT pid, name, category, price, stock_count "
            "FROM products "
            "WHERE " + where_clause + ";"
        )
        try:
            cur = self.conn.execute(sql, params)
            rs = cur.fetchall()
            return rs
        except sqlite3.Error as e:
            print("\n[X] SQL Error in search_product()\n")
            print(e)
            return None   
    
    #   Retrieve detailed product information by product ID.
    #   Args:
    #       pid (int): Product ID.
    #   Returns:
    #           sqlite3.Row: Product details (name, category, price, etc.)
    def get_product_details(self,pid):

        try:
            cur = self.conn.execute("SELECT name, category, price, stock_count,descr FROM products WHERE pid = ? ;",(pid,))
            rs = cur.fetchone()
            return rs
        except sqlite3.Error as e:
            print("\n[X] SQL Error in get_product_details()\n")
            print(e)
            return None
        
    #   Record that the customer viewed a specific product.
    #   Args:
    #       sessionInformation (SessionInf): Current session information.
    #       pid (int): ID of the viewed product.
    def create_viewed_product(self,sessionInformation,pid):
        
        ts = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            cur = self.conn.execute("INSERT INTO viewedProduct (cid,sessionNo,ts,pid) VALUES (?,?,?,?);",(sessionInformation.cid,sessionInformation.sessionNo,ts,pid))
            self.commit()
        except sqlite3.Error as e:
            print("\n[X] SQL Error in create_viewed_product()\n")
            print(e)
            self.conn.rollback()

    #   Check if the given product is already in the customer's cart.
    #   Args:
    #       sessionInformation (SessionInf): Current session details.
    #       pid (int): Product ID.
    #   Returns:
    #           sqlite3.Row or None: Existing cart record if present.
    def check_add_to_cart(self,sessionInformation,pid):

        try:
            cur = self.conn.execute("SELECT qty FROM cart WHERE cid = ? and sessionNo = ? and pid = ?;",(sessionInformation.cid,sessionInformation.sessionNo,pid,))
            rs = cur.fetchone()
            return rs
        except sqlite3.Error as e:
            print("\n[X] SQL Error in check_add_to_cart()\n")
            print(e)
            return None
    

    #   Retrieve the current stock count for a given product.
    #   Args:
    #       pid (int): Product ID.
    #   Returns:
    #           sqlite3.Row or None: Row containing stock_count.
    def check_stock(self,pid):

        try:
            cur = self.conn.execute("SELECT stock_count FROM products WHERE pid = ?;",(pid,))
            rs = cur.fetchone()
            return rs
        except sqlite3.Error as e:
            print("\n[X] SQL Error in check_stock()\n")
            print(e)
            return None
        
    #   Add or update a product in the customer's cart.
    #   Args:
    #       sessionInformation (SessionInf): Current session information.
    #       pid (int): Product ID.
    #       qty (int): Quantity to add or set.
    #       mode (str): 
    #           "add" – increment existing quantity (or insert new record)
    #           "set" – replace quantity with a new value
    #   Returns:
    #           bool: True if operation succeeded, False otherwise.
    def add_to_cart(self,sessionInformation,pid,qty,mode):
        
        new_qty = qty
        rs = self.check_add_to_cart(sessionInformation,pid)     #   Check if product already in cart
        rs2 = self.check_stock(pid)                             #   Get available stock
        if mode == "add":
            #   Add new item if not already in cart
            if rs is None and (rs2["stock_count"] > 0):
                try:
                    cur = self.conn.execute("INSERT INTO cart (cid,sessionNo,pid,qty) VALUES (?,?,?,?);",(sessionInformation.cid,sessionInformation.sessionNo,pid,new_qty))
                    self.commit()
                    return True
                except sqlite3.Error as e:
                    print("\n[X] SQL Error in add_to_cart() for new item add to cart\n")
                    print(e)
                    self.conn.rollback()
                    return False
            else:
                #   Item already exists; increment quantity
                new_qty = rs["qty"] + qty

        elif mode == "set":
            new_qty = qty
        #   Remove item if new quantity is 0
        if new_qty == 0:
            self.delete_cart_items(sessionInformation,pid)
            return True
        #   Update cart quantity if stock is sufficient
        if new_qty <= rs2["stock_count"]:
            try:
                cur = self.conn.execute("UPDATE cart SET qty = ? WHERE cid = ? and sessionNo = ? and pid = ? ;",(new_qty,sessionInformation.cid,sessionInformation.sessionNo,pid))
                self.commit()
            except sqlite3.Error as e:
                print("\n[X] SQL Error in add_to_cart() for update qty\n")
                print(e)
                self.conn.rollback()
            return True
        else:         
            print("\nNot enough stock!")
            return False

    #   Retrieve all items in the current customer's cart.
    #   Args:
    #       sessionInformation (SessionInf): Current session information.
    #   Returns:
    #           list[sqlite3.Row]: List of cart items joined with product info.
    def get_cart_items(self,sessionInformation):

        try:
            cur = self.conn.execute("""
                SELECT ct.pid, p.name, p.price, ct.qty, p.stock_count,
                       (p.price * ct.qty) AS total
                FROM cart ct
                JOIN products p ON ct.pid = p.pid
                WHERE ct.cid = ? AND ct.sessionNo = ?;
            """, (sessionInformation.cid, sessionInformation.sessionNo))
            rs = cur.fetchall()
            return rs
        except sqlite3.Error as e:
            print("\n[X] SQL Error get_cart_items()\n")
            print(e)
            return None
    
    #   Delete an item from the customer's cart.
    #   Args:
    #       sessionInformation (SessionInf): Current session info.
    #       pid (int): Product ID to remove.
    #   Returns:
    #           bool: True if delete succeeded, False otherwise.
    def delete_cart_items(self,sessionInformation,pid):

        try:
            cur = self.conn.execute("DELETE FROM cart WHERE cid = ? AND sessionNo = ? AND pid = ?;", (sessionInformation.cid, sessionInformation.sessionNo,pid))
            self.commit()
            return True
        except sqlite3.Error as e:
            print("\n[X] SQL Error delete_cart_items()\n")
            print(e)
            self.conn.rollback()         
            return False 
   
    #   Generate a new order from the current customer's cart.
    #   Performs stock checks and uses a transaction to ensure consistency.
    #   Args:
    #       sessionInformation (SessionInf): Current session details.
    #       shipping_address (str): Address for shipment.
    #   Returns:
    #           int or None: The order number if successful, or None if failed.
    def create_order(self,sessionInformation,shipping_address):

        rs = self.get_cart_items(sessionInformation)
        if not rs:
            print("\n[X] Your cart is empty!")
            return None
        
        odate = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ono = self.get_max_orderNo()
        shipping_address = shipping_address

        try:
            #   Begin transaction
            if not self.conn.in_transaction:
                self.conn.execute("BEGIN IMMEDIATE;")
            #   Insert order header
            cur = self.conn.execute("INSERT INTO orders (ono,cid, sessionNo, odate, shipping_address) VALUES (?,?, ?, ?, ?);",
                (ono,sessionInformation.cid, sessionInformation.sessionNo, odate, shipping_address)
            )
            index = 1
            for row in rs:
                pid = row['pid']
                qty = row['qty']
                stock = row['stock_count']
                price = row['price']
                name = row['name']

                #   Check stock before inserting order line
                if stock < qty:
                    print("\n[X] Not enough stock for product: ", name)
                    print("\n[X] Avaliable in store: ",stock)
                    self.conn.execute("ROLLBACK;")
                    print("\n[X] Checkout cancelled. Please try again later.")
                    return None
                
                #   Insert each order line and update stock
                self.conn.execute("INSERT INTO orderlines (ono, lineNo, pid, qty, uprice) VALUES (?, ?, ?, ?, ?);",
                    (ono, index, pid, qty, price))
                self.conn.execute("UPDATE products SET stock_count = stock_count - ? WHERE pid = ?;",(qty, pid))
                index = index + 1
            #   Clear cart and commit
            self.clear_cart(sessionInformation)
            return ono
            
        except sqlite3.Error as e:
            print("\n[X] SQL Error during order creation:")
            print(e)
        
            if self.conn.in_transaction:
                self.conn.execute("ROLLBACK;")
            print("\n[X] Transaction rolled back. No changes were made.")
            return None

    def clear_cart(self,sessionInformation):
        try:
            #   Clear cart and commit
            cur = self.conn.execute( "DELETE FROM cart WHERE cid = ? AND sessionNo = ?;",(sessionInformation.cid, sessionInformation.sessionNo))
            self.commit()
            return None
        except sqlite3.Error as e:
            print("\n[X] SQL Error in clear_cart()\n")
            print(e)
            return None

    
    
    #   Retrieve detailed order information by order number .
    #   Args:
    #       ono (int): order number.
    #   Returns:
    #           sqlite3.Row: order details (product name, product category, qty,
    #                                       unit price etc.)   
    def get_order_details(self,ono):

        try:
            cur = self.conn.execute("""
                SELECT p.name, p.category, ol.qty, ol.uprice, (ol.qty * ol.uprice) AS total
                FROM orderlines ol
                JOIN products p ON ol.pid = p.pid
                WHERE ol.ono = ?;
            """, (ono,))
            rs = cur.fetchall()
            return rs
        except sqlite3.Error as e:
            print("\n[X] SQL Error in get_order_details()\n")
            print(e)
            return None

    #   Retrieve all orders placed by a specific customer.
    #   Args:
    #       uid (int): Customer ID.
    #   Returns:
    #           list[sqlite3.Row]: Summary of all orders with total cost.
    def get_orders(self,uid):

        try:
            cur = self.conn.execute("""SELECT o.ono, o.odate, o.shipping_address, SUM(ol.qty * ol.uprice) AS total
                FROM orders o
                JOIN orderlines ol ON o.ono = ol.ono
                WHERE o.cid = ?
                GROUP BY o.ono, o.odate, o.shipping_address
                ORDER BY o.odate DESC;
            """, (uid,))
            rs = cur.fetchall()
            return rs
        except sqlite3.Error as e:
            print("\n[X] SQL Error in get_orders()")
            print(e)
            return None
    def get_product_by_pid(self, pid):
        try:
            cur = self.conn.execute(
                "SELECT pid, name, category, price, stock_count, descr FROM products WHERE pid = ?;",
                (pid,),
            )
            return cur.fetchone()
        except sqlite3.Error as e:
            print("\n[X] SQL Error in get_product_by_pid()\n"); 
            print(e)
            return None

    def update_product_price(self, pid, new_price) -> bool:
        try:
            self.conn.execute("UPDATE products SET price = ? WHERE pid = ?;", (new_price, pid))
            self.commit()
            return True
        except sqlite3.Error as e:
            print("\n[X] SQL Error in update_product_price()\n"); 
            print(e)
            self.conn.rollback()
            return False

    def update_product_stock(self, pid, new_stock) -> bool:
        try:
            self.conn.execute("UPDATE products SET stock_count = ? WHERE pid = ?;", (new_stock, pid))
            self.commit()
            return True
        except sqlite3.Error as e:
            print("\n[X] SQL Error in update_product_stock()\n"); 
            print(e)
            self.conn.rollback()           
            return False

    def weekly_sales_metrics(self):
        """
        Weekly sales report for the last 7 days (inclusive).
        Returns dict: {orders, products, customers, avg_per_customer, total_sales}
        """
        try:
            params = ()
            q_orders = (
                "SELECT COUNT(DISTINCT o.ono) FROM orders o "
                "WHERE date(o.odate) >= date('now','-6 day') AND date(o.odate) <= date('now');"
            )
            orders = self.conn.execute(q_orders, params).fetchone()[0]

            q_products = (
                "SELECT COUNT(DISTINCT ol.pid) FROM orderlines ol "
                "JOIN orders o ON ol.ono=o.ono "
                "WHERE date(o.odate) >= date('now','-6 day') AND date(o.odate) <= date('now');"
            )
            products = self.conn.execute(q_products, params).fetchone()[0]

            q_customers = (
                "SELECT COUNT(DISTINCT o.cid) FROM orders o "
                "WHERE date(o.odate) >= date('now','-6 day') AND date(o.odate) <= date('now');"
            )
            customers = self.conn.execute(q_customers, params).fetchone()[0]

            q_total = (
                "SELECT COALESCE(SUM(ol.qty * ol.uprice),0) FROM orderlines ol "
                "JOIN orders o ON ol.ono=o.ono "
                "WHERE date(o.odate) >= date('now','-6 day') AND date(o.odate) <= date('now');"
            )
            total_sales = self.conn.execute(q_total, params).fetchone()[0]

            avg_per_customer = (total_sales / customers) if customers else 0.0
            return {
                'orders': orders,
                'products': products,
                'customers': customers,
                'avg_per_customer': round(avg_per_customer, 2),
                'total_sales': round(total_sales, 2),
            }
        except sqlite3.Error as e:
            print("\n[X] SQL Error in weekly_sales_metrics()\n"); print(e)
            return None

    def top_products_by_distinct_orders(self):
        """Top products by count of DISTINCT orders; returns top-3 including ties at rank 3."""
        try:
            rows = self.conn.execute(
                """
                SELECT p.pid, p.name, COUNT(DISTINCT ol.ono) AS cnt
                FROM orderlines ol
                JOIN products p ON p.pid = ol.pid
                GROUP BY p.pid, p.name
                ORDER BY cnt DESC, p.pid ASC;
                """
            ).fetchall()
            return self._top3_with_ties(rows, key='cnt')
        except sqlite3.Error as e:
            print("\n[X] SQL Error in top_products_by_distinct_orders()\n"); print(e)
            return []

    def top_products_by_views(self):
        """Top products by total views; returns top-3 including ties at rank 3."""
        try:
            rows = self.conn.execute(
                """
                SELECT p.pid, p.name, COUNT(*) AS views
                FROM viewedProduct v
                JOIN products p ON p.pid = v.pid
                GROUP BY p.pid, p.name
                ORDER BY views DESC, p.pid ASC;
                """
            ).fetchall()
            return self._top3_with_ties(rows, key='views')
        except sqlite3.Error as e:
            print("\n[X] SQL Error in top_products_by_views()\n"); print(e)
            return []

    @staticmethod
    def _top3_with_ties(rows, key):
        """rows: list of sqlite3.Row with numeric column `key`."""
        if not rows:
            return []
        counts = [r[key] for r in rows]
        unique_counts = sorted(set(counts), reverse=True)
        if len(unique_counts) <= 2:
            cutoff = unique_counts[-1]
        else:
            cutoff = unique_counts[2]  # 3rd distinct value
        return [dict(pid=r['pid'], name=r['name'], count=r[key]) for r in rows if r[key] >= cutoff]
# --- END new sale helper function ---------------------------------------------
  
