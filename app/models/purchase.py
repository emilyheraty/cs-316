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
    def get_chart_data(uid):
        rows = app.db.execute('''
SELECT time_purchased, total_amount, number_of_items
FROM Purchases
WHERE uid = :uid
ORDER BY time_purchased DESC
''',
                              uid=uid)
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
