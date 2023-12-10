from flask import current_app as app


class Purchase:
    def __init__(self, id, uid, pid, time_purchased, total_amount, number_of_items, fulfillment_status, order_id, prod_name):
        self.id = id
        self.uid = uid
        self.pid = pid
        self.time_purchased = time_purchased
        self.total_amount = total_amount
        self.number_of_items = number_of_items
        self.fulfillment_status = fulfillment_status
        self.order_id = order_id
        self.prod_name = prod_name

    @staticmethod
    def get(id):
        rows = app.db.execute('''
SELECT Purchases.id, Purchases.uid, Purchases.pid, Purchases.time_purchased, Purchases.total_amount, Purchases.number_of_items, Purchases.fulfillment_status, Purchases.order_id, Products.name
FROM Purchases, Products
WHERE id = :id and Purchases.pid = Products.id
''',
                              id=id)
        return Purchase(*(rows[0])) if rows else None

    @staticmethod
    def get_all_by_uid_since(uid, since):
        rows = app.db.execute('''
SELECT Purchases.id, Purchases.uid, Purchases.pid, Purchases.time_purchased, Purchases.total_amount, Purchases.number_of_items, Purchases.fulfillment_status, Purchases.order_id, Products.name
FROM Purchases, Products
WHERE uid = :uid and Purchases.pid = Products.id
AND time_purchased >= :since
ORDER BY time_purchased DESC
''',
                              uid=uid,
                              since=since)
        return [Purchase(*row) for row in rows]
    
    @staticmethod
    def get_all_by_uid(uid):
        rows = app.db.execute('''
SELECT Purchases.id, Purchases.uid, Purchases.pid, Purchases.time_purchased, Purchases.total_amount, Purchases.number_of_items, Purchases.fulfillment_status, Purchases.order_id, Products.name
FROM Purchases, Products
WHERE uid = :uid and Purchases.pid = Products.id
ORDER BY time_purchased DESC
''',
                              uid=uid)
        return [Purchase(*row) for row in rows]
    
    @staticmethod
    def get_by_natural_time(uid):
        rows = app.db.execute('''
SELECT Purchases.id, Purchases.uid, Purchases.pid, Purchases.time_purchased, Purchases.total_amount, Purchases.number_of_items, Purchases.fulfillment_status, Purchases.order_id, Products.name
FROM Purchases, Products
WHERE uid = :uid and Purchases.pid = Products.id
ORDER BY time_purchased ASC
''',
                              uid=uid)
        return [Purchase(*row) for row in rows]
    
    @staticmethod
    def get_by_product_name(name, uid):
        rows = app.db.execute('''
SELECT Purchases.id, uid, pid, time_purchased, total_amount, number_of_items, fulfillment_status, Purchases.order_id, Products.name
FROM (Purchases JOIN Products ON Purchases.pid = Products.id)
WHERE name = :name AND uid = :uid
                              ''',
                              name=name, uid=uid)
        return [Purchase(*row) for row in rows]
    
    @staticmethod
    def get_by_ascending_amount(uid):
        rows = app.db.execute('''
SELECT Purchases.id, Purchases.uid, Purchases.pid, Purchases.time_purchased, Purchases.total_amount, Purchases.number_of_items, Purchases.fulfillment_status, Purchases.order_id, Products.name
FROM Purchases, Products
WHERE uid = :uid and Purchases.pid = Products.id
ORDER BY total_amount ASC
                              ''', uid=uid)
        return [Purchase(*row) for row in rows]
    
    @staticmethod
    def get_by_descending_amount(uid):
        rows = app.db.execute('''
SELECT Purchases.id, Purchases.uid, Purchases.pid, Purchases.time_purchased, Purchases.total_amount, Purchases.number_of_items, Purchases.fulfillment_status, Purchases.order_id, Products.name
FROM Purchases, Products
WHERE uid = :uid and Purchases.pid = Products.id
ORDER BY total_amount DESC
                              ''', uid=uid)
        return [Purchase(*row) for row in rows]

    @staticmethod
    def get_by_status(status, uid):
        if(status):
            rows = app.db.execute('''
SELECT Purchases.id, Purchases.uid, Purchases.pid, Purchases.time_purchased, Purchases.total_amount, Purchases.number_of_items, Purchases.fulfillment_status, Purchases.order_id, Products.name
FROM Purchases, Products
WHERE fulfillment_status IS NOT NULL AND uid = :uid
                                ''',
                                status=status, uid=uid)
        else:
            rows = app.db.execute('''
SELECT Purchases.id, Purchases.uid, Purchases.pid, Purchases.time_purchased, Purchases.total_amount, Purchases.number_of_items, Purchases.fulfillment_status, Purchases.order_id, Products.name
FROM Purchases, Products
WHERE fulfillment_status IS NULL AND uid = :uid
                                ''',
                                status=status, uid=uid)
        return [Purchase(*row) for row in rows]

        
    @staticmethod
    def get_all_years(uid):
        rows = app.db.execute('''
SELECT EXTRACT(Year FROM Purchases.time_purchased) AS Year, SUM(total_amount) as total_amount
FROM Purchases
WHERE uid = :uid
GROUP BY Year
ORDER BY Year ASC
''',
                              uid=uid)
        return rows
    
    @staticmethod
    def get_by_product_count(uid):
        rows = app.db.execute('''
SELECT Products.name AS name, SUM(number_of_items) as Count
FROM (Purchases JOIN Products ON Purchases.pid = Products.id)
WHERE uid = :uid
GROUP BY name
LIMIT 10
                              ''',
                            uid=uid)
        return rows
    
    @staticmethod
    def get_by_year(uid, year):
        rows = app.db.execute('''
SELECT EXTRACT(Month FROM Purchases.time_purchased) AS Month, SUM(total_amount) as total_amount
FROM Purchases
WHERE uid = :uid AND EXTRACT(Year FROM Purchases.time_purchased) = :year
GROUP BY Month
ORDER BY Month ASC
''',
                              uid=uid, year=year)
        return rows
    
    @staticmethod
    def get_all_by_state(uid):
        rows = app.db.execute('''
SELECT Users.state, SUM(Purchases.total_amount) as total_amount
FROM Purchases
JOIN Users ON Purchases.uid = Users.id
JOIN (SELECT * FROM Products WHERE Products.creator_id = :uid) as d1 ON Purchases.pid = d1.id                  
GROUP BY Users.state
''',
                              uid=uid)
        return rows
    
    @staticmethod
    def get_all_by_state_category(uid, category):
        rows = app.db.execute('''
SELECT Users.state, SUM(Purchases.number_of_items) as number_of_items
FROM Purchases
JOIN Users ON Purchases.uid = Users.id
JOIN (SELECT * FROM Products WHERE Products.creator_id = :uid AND Products.category = :category) as d1 ON Purchases.pid = d1.id                  
WHERE category = :category
GROUP BY Users.state
''',
                              uid=uid, category=category)
        return rows

    @staticmethod
    def submitPurchase(uid, pid, sid, time, amount, quantity, oid):
        try:
            rows = app.db.execute("""
INSERT INTO Purchases(uid, pid, sid, time_purchased, total_amount, number_of_items, fulfillment_status, order_id)
VALUES(:uid, :pid, :sid, :time, :amount, :qty, :status, :oid)
""",
                                  uid=uid,
                                  pid=pid,
                                  sid=sid,
                                  time=time,
                                  amount=amount,
                                  qty=quantity,
                                  status=None,
                                  oid=oid)
        except Exception as e:
            print(str(e))

    @staticmethod
    def maxOId():
        try:
            m = app.db.execute("""
SELECT COALESCE(max(order_id), 0)
FROM Purchases
""")
            return m[0][0]
        except Exception as e:
            print(str(e))

    @staticmethod
    def getOrder(order_id):
        rows = app.db.execute('''
SELECT Purchases.fulfillment_status
FROM Purchases
WHERE order_id = :order_id
''',
                              order_id=order_id)
        if rows is not None:
            if any(element is None for element in rows[0]):
                return "Order not Fulfilled"
            else:
                return "Order Fulfilled"
        else:
            return "Order not Found"
        
    @staticmethod
    def get_by_sellerid(seller_id):
        rows = app.db.execute('''
SELECT Purchases.id, Purchases.uid, Purchases.pid, Purchases.time_purchased, Purchases.total_amount, Purchases.number_of_items, Purchases.fulfillment_status, Purchases.order_id, Products.name
FROM Purchases, Products
WHERE id = :id and Purchases.pid = Products.id
''',
                              id=seller_id)
        return Purchase(*(rows[0])) if rows else None

