from flask import current_app as app


class Cart:
    def __init__(self, buyer_id, name, seller_id, product_id, quantity, price):
        self.buyer_id = buyer_id
        self.prod_name = name
        self.seller_id = seller_id
        self.product_id = product_id
        self.quantity = quantity
        self.price = price

    @staticmethod
    def getCartByBuyerId(id):
        rows = app.db.execute('''
SELECT buyer_id, name, Products.creator_id, product_id, quantity, Carts.price                             
FROM Carts, Products
WHERE Carts.buyer_id = :id and Carts.product_id = Products.id
SELECT buyer_id, name, Inventory.id, product_id, quantity, Products.price                             
FROM Carts, Products, Inventory
WHERE Carts.buyer_id = :id and Carts.seller_id = Inventory.id and Carts.product_id = Products.id and Products.name=Inventory.product_name 
''',
                              id=id)
        # perhaps shold make it so price updates from product table as well as name
        return [Cart(*row) for row in rows] if rows else []

    @staticmethod
    def getPartialCartByBuyerId(id, per_page, off):
        rows = app.db.execute('''
SELECT buyer_id, name, Products.creator_id, product_id, quantity, Carts.price                             
FROM Carts, Products
WHERE Carts.buyer_id = :id and Carts.product_id = Products.id
SELECT buyer_id, name, Inventory.id, product_id, quantity, Products.price                             
FROM Carts, Products, Inventory
WHERE Carts.buyer_id = :id and Carts.seller_id = Inventory.id and Carts.product_id = Products.id and Products.name=Inventory.product_name 
ORDER BY product_id
LIMIT :per_page
OFFSET :off
''',
                              id=id, 
                              per_page=per_page,
                              off=off)
        # perhaps shold make it so price updates from product table as well as name
        return [Cart(*row) for row in rows] if rows else []


#TODO update quantity, price if (bid pid) are already in cart. 
    @staticmethod
    def addToCart(bid, pname, sid, quant):
        try:
            rows = app.db.execute("""
INSERT INTO Carts(
    buyer_id, seller_id, product_id, quantity)
VALUES(:buyer_id, :pname, :seller_id, :quantity)
""",
                                  buyer_id=bid,
                                  pname=pname,
                                  seller_id=sid,
                                  quantity=quant)
            return Cart.getCartByBuyerId(bid)
        except Exception as e:
            print(str(e))
            return None
        
    @staticmethod
    def updateQuantity(bid, sid, pid, newQuantity):
        try:
            res = app.db.execute("""
UPDATE Carts
SET quantity = :newQuantity
WHERE Carts.buyer_id = :bid and Carts.seller_id = :sid and Carts.product_id=:pid;
""",
                                  bid=bid,
                                  sid=sid,
                                  pid=pid,
                                  newQuantity=newQuantity)
            return res
        except Exception as e:
            print(str(e))
            return None
        
    @staticmethod
    def removeProductFromCart(bid, sid, pid):
        try:
            res = app.db.execute(
"""
DELETE FROM Carts
WHERE Carts.buyer_id = :bid and Carts.seller_id = :sid and Carts.product_id=:pid;
""",
                                  bid=bid,
                                  sid=sid,
                                  pid=pid)
            return res
        except Exception as e:
            print(str(e))
            return None

    @staticmethod
    def clearCartByUserId(bid):
        try:
            res = app.db.execute(
"""
DELETE FROM Carts
WHERE Carts.buyer_id = :bid;
""",
                                  bid=bid)
            return res
        except Exception as e:
            print(str(e))
            return None
        
        
        