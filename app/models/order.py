from flask import current_app as app

class Order:
    def __init__(self, buyer_id, prod_name, date, qty, status):
        self.buyer_id = buyer_id
        self.product_name = prod_name
        self.date = date
        self.quantity = qty
        self.status = status

    @staticmethod
    def getPartialOrdersBySellerId(sid, per_page, off):
       rows = app.db.execute('''
                             SELECT Purchases.uid as buyer_id, Products.name, number_of_items, time_purchased, fulfillment_status                             
                             FROM Purchases, Products, Carts, Inventory
                             WHERE Purchases.uid = Carts.buyer_id
                             AND Purchases.pid = Carts.product_id
                             AND Carts.seller_id = Inventory.id
                             AND Carts.product_id = Products.id
                             AND Products.name = Inventory.product_name
                             ORDER BY time_purchased
                             LIMIT :per_page
                             OFFSET :off
                             ''',
                             id=sid, 
                             per_page=per_page,
                             off=off)
       return [Order(*row) for row in rows] if rows else []
    
    @staticmethod
    def getOrdersBySellerId(sid):
       rows = app.db.execute('''
                             SELECT Purchases.uid as buyer_id, Products.name, number_of_items, time_purchased, fulfillment_status                             
                             FROM Purchases, Products, Carts, Inventory
                             WHERE Purchases.uid = Carts.buyer_id
                             AND Purchases.pid = Carts.product_id
                             AND Carts.seller_id = Inventory.id
                             AND Carts.product_id = Products.id
                             AND Products.name = Inventory.product_name
                             ORDER BY time_purchased
                             ''',
                             id=sid)
       return [Order(*row) for row in rows] if rows else []
