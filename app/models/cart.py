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
SELECT buyer_id, name, Inventory.id, product_id, quantity, Products.price                             
FROM Carts, Products, Inventory
WHERE Carts.buyer_id = :id and Carts.product_id = Products.id and Products.name=Inventory.product_name
''',
                              id=id)
        # perhaps shold make it so price updates from product table as well as name
        return [Cart(*row) for row in rows] if rows else []

    @staticmethod
    def getPartialCartByBuyerId(id, per_page, off):
        rows = app.db.execute('''
SELECT buyer_id, name, Inventory.id, product_id, quantity, Products.price                             
FROM Carts, Products, Inventory
WHERE Carts.buyer_id = :id and Carts.product_id = Products.id and Products.name=Inventory.product_name 
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
    def updateQuantity(bid, sid, newQuantity):
        print("bid: " + str(bid) + " sid: " + str(sid) + "nq: " + str(newQuantity))
        try:
            res = app.db.execute("""
UPDATE Carts
SET quantity = :newQuantity
WHERE Carts.buyer_id = :bid and Carts.seller_id = :sid;
""",
                                  bid=bid,
                                  sid=sid,
                                  newQuantity=newQuantity)
            print("Result: " + str(res))
            return res
        except Exception as e:
            print(str(e))
            return None
        
    @staticmethod
    def updateQuantity2(bid, sid, newQuantity):
        print("bid: " + str(bid) + " sid: " + str(sid) + "nq: " + str(newQuantity))
        res = app.db.execute("""
Select *
FROM Carts
WHERE Carts.buyer_id = :bid and Carts.seller_id = :sid;
""",
                                  bid=int(bid),
                                  sid=int(sid),
                                  newQuantity=int(newQuantity))
        print("Result: " + str(res))
        return res
