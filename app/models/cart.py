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
SELECT buyer_id, name, Inventory.id, product_id, quantity, Carts.price                             
FROM Carts, Products, Inventory
WHERE Carts.buyer_id = :id and Carts.product_id = Products.id and Products.name=Inventory.product_name
''',
                              id=id)
        # perhaps shold make it so price updates from product table as well as name
        return [Cart(*row) for row in rows] if rows else []

    @staticmethod
    def getPartialCartByBuyerId(id, per_page, off):
        rows = app.db.execute('''
SELECT buyer_id, name, Inventory.id, product_id, quantity, Carts.price                             
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
    def addToCart(bid, sid, pid, quant, price):
        try:
            rows = app.db.execute("""
INSERT INTO Carts(
    buyer_id, seller_id, product_id, quantity, price)
VALUES(:buyer_id, :seller_id, :product_id, :quantity, :price)
""",
                                  buyer_id=bid,
                                  seller_id=sid,
                                  product_id=pid, quantity=quant, price=price)
            return Cart.getCartByBuyerId(bid)
        except Exception as e:
            print(str(e))
            return None

        


