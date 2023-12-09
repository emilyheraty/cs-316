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
    def get_chart_data(uid):
        rows = app.db.execute('''
SELECT time_purchased, total_amount, number_of_items
FROM Purchases, Products
WHERE uid = :uid and Purchases.pid = Products.id
ORDER BY time_purchased DESC
''',
                              uid=uid)
        return rows

    @staticmethod
    def submitPurchase(uid, pid, time, amount, quantity, oid):
        try:
            rows = app.db.execute("""
INSERT INTO Purchases(uid, pid, time_purchased, total_amount, number_of_items, fulfillment_status, order_id)
VALUES(:uid, :pid, :time, :amount, :qty, :status, :oid)
""",
                                  uid=uid,
                                  pid=pid,
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
    def get_by_sellerid(seller_id):
        rows = app.db.execute('''
SELECT Purchases.id, Purchases.uid, Purchases.pid, Purchases.time_purchased, Purchases.total_amount, Purchases.number_of_items, Purchases.fulfillment_status, Purchases.order_id, Products.name
FROM Purchases, Products
WHERE id = :id and Purchases.pid = Products.id
''',
                              id=seller_id)
        return Purchase(*(rows[0])) if rows else None
