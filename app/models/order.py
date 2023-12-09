from flask import current_app as app

class Order:
    def __init__(self, buyer_id, prod_name, date, qty, status, address):
        self.buyer_id = buyer_id
        self.product_name = prod_name
        self.date = date
        self.quantity = qty
        self.status = status
        self.address = address

    @staticmethod
    def getPartialOrdersBySellerId(sid, per_page, off):
       rows = app.db.execute('''
                             SELECT Purchases.uid as buyer_id, Products.name, number_of_items, time_purchased, fulfillment_status, Users.address                            
                             FROM Purchases, Products, Users
                             WHERE Purchases.sid = :sid
                             AND Purchases.pid = Products.id
                             AND Purchases.uid = Users.id
                             ORDER BY time_purchased
                             LIMIT :per_page
                             OFFSET :off
                             ''',
                             sid=sid, 
                             per_page=per_page,
                             off=off)
       return [Order(*row) for row in rows] if rows else []
    
    @staticmethod
    def getOrdersBySellerId(sid):
        print(sid)
        rows = app.db.execute('''
                             SELECT Purchases.uid as buyer_id, Products.name, number_of_items, time_purchased, fulfillment_status, Users.address                             
                             FROM Purchases, Products, Users
                             WHERE Purchases.sid = :sid
                             AND Purchases.pid = Products.id
                             AND Purchases.uid = Users.id
                             ORDER BY time_purchased
                             ''',
                             sid=sid)
        return [Order(*row) for row in rows] if rows else []


    @staticmethod
    def updateFulfillmentStatus(sid, time_purchased, uid, fulfillment_status):
        # print("bruh")
        res = app.db.execute('''
UPDATE Purchases
SET fulfillment_status = :fulfillment_status
WHERE Purchases.sid = :sid AND Purchases.time_purchased = :time_purchased AND Purchases.uid = :uid
''',
                                sid=sid,
                                time_purchased=time_purchased,
                                uid=uid,
                                fulfillment_status=fulfillment_status)
        # print("did it work tho")
        return res


    @staticmethod
    def searchProductName(sid, str, per_page, off):
        print("bruh")
        rows = app.db.execute('''
SELECT Purchases.uid as buyer_id, Products.name, number_of_items, time_purchased, fulfillment_status, Users.address
FROM Purchases, Products, Users
WHERE Purchases.sid = :sid
AND Purchases.pid = Products.id
AND Purchases.uid = Users.id
AND Products.name LIKE '%' || :str || '%'
ORDER BY time_purchased DESC
LIMIT :per_page
OFFSET :off
''',
                                sid=sid,
                                str=str,
                                per_page=per_page,
                                off=off)
        print("did it work tho")
        return [Order(*row) for row in rows] if rows else []


    @staticmethod
    def getOrdersByStatus(fulfillment_status, sid, per_page, off):
        print("bruh")
        rows = app.db.execute('''
SELECT Purchases.uid as buyer_id, Products.name, number_of_items, time_purchased, fulfillment_status, Users.address
FROM Purchases, Products, Users
WHERE Purchases.sid = :sid
AND Purchases.pid = Products.id
AND Purchases.uid = Users.id
AND Purchases.fulfillment_status = :fulfillment_status
ORDER BY time_purchased DESC
LIMIT :per_page
OFFSET :off
''',
                                sid=sid,
                                fulfillment_status=fulfillment_status,
                                per_page=per_page,
                                off=off)
        print("did it work tho")
        return [Order(*row) for row in rows] if rows else []