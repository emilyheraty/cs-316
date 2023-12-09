from flask import current_app as app


class Purchase:
    def __init__(self, id, uid, pid, time_purchased, total_amount, number_of_items, fulfillment_status):
        self.id = id
        self.uid = uid
        self.pid = pid
        self.time_purchased = time_purchased
        self.total_amount = total_amount
        self.number_of_items = number_of_items
        self.fulfillment_status = fulfillment_status

    @staticmethod
    def get(id):
        rows = app.db.execute('''
SELECT id, uid, pid, time_purchased, total_amount, number_of_items, fulfillment_status
FROM Purchases
WHERE id = :id
''',
                              id=id)
        return Purchase(*(rows[0])) if rows else None

    @staticmethod
    def get_all_by_uid_since(uid, since):
        rows = app.db.execute('''
SELECT id, uid, pid, time_purchased, total_amount, number_of_items, fulfillment_status
FROM Purchases
WHERE uid = :uid
AND time_purchased >= :since
ORDER BY time_purchased DESC
''',
                              uid=uid,
                              since=since)
        return [Purchase(*row) for row in rows]
    
    @staticmethod
    def get_all_by_uid(uid):
        rows = app.db.execute('''
SELECT id, uid, pid, time_purchased, total_amount, number_of_items, fulfillment_status
FROM Purchases
WHERE uid = :uid
ORDER BY time_purchased DESC
''',
                              uid=uid)
        return [Purchase(*row) for row in rows]
    
    @staticmethod
    def get_by_natural_time(uid):
        rows = app.db.execute('''
SELECT id, uid, pid, time_purchased, total_amount, number_of_items, fulfillment_status
FROM Purchases
WHERE uid = :uid
ORDER BY time_purchased ASC
''',
                              uid=uid)
        return [Purchase(*row) for row in rows]
    
    @staticmethod
    def get_by_product_name(name, uid):
        rows = app.db.execute('''
SELECT Purchases.id, uid, pid, time_purchased, total_amount, number_of_items, fulfillment_status
FROM (Purchases JOIN Products ON Purchases.pid = Products.id)
WHERE name = :name AND uid = :uid
                              ''',
                              name=name, uid=uid)
        return [Purchase(*row) for row in rows]
    
    @staticmethod
    def get_by_ascending_amount(uid):
        rows = app.db.execute('''
SELECT id, uid, pid, time_purchased, total_amount, number_of_items, fulfillment_status
FROM Purchases
WHERE uid = :uid
ORDER BY total_amount ASC
                              ''', uid=uid)
        return [Purchase(*row) for row in rows]
    
    @staticmethod
    def get_by_descending_amount(uid):
        rows = app.db.execute('''
SELECT id, uid, pid, time_purchased, total_amount, number_of_items, fulfillment_status
FROM Purchases
WHERE uid = :uid
ORDER BY total_amount DESC
                              ''', uid=uid)
        return [Purchase(*row) for row in rows]

    @staticmethod
    def get_by_status(status, uid):
        rows = app.db.execute('''
SELECT id, uid, pid, time_purchased, total_amount, number_of_items, fulfillment_status
FROM Purchases
WHERE fulfillment_status = :status AND uid = :uid
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
    def get_all_by_state_product(uid, name):
        rows = app.db.execute('''
SELECT Users.state, SUM(Purchases.total_amount) as total_amount
FROM Purchases
JOIN Users ON Purchases.uid = Users.id
JOIN (SELECT * FROM Products WHERE Products.creator_id = :uid AND Products.name = :name) as d1 ON Purchases.pid = d1.id                  
GROUP BY Users.state
''',
                              uid=uid, name=name)
        return rows

    @staticmethod
    def submitPurchase(uid, pid, time, amount, quantity, status):
        try:
            rows = app.db.execute("""
INSERT INTO Purchases(uid, pid, time_purchased, total_amount, number_of_items, fulfillment_status)
VALUES(:uid, :pid, :time, :amount, :qty, :status)
""",
                                  uid=uid,
                                  pid=pid,
                                  time=time,
                                  amount=amount,
                                  qty=quantity,
                                  status=0)
        except Exception as e:
            print(str(e))

    @staticmethod
    def get_by_sellerid(seller_id):
        rows = app.db.execute('''
SELECT id, uid, pid, time_purchased, total_amount, number_of_items, fulfillment_status
FROM Purchases, 
WHERE id = :id
''',
                              id=id)
        return Purchase(*(rows[0])) if rows else None
