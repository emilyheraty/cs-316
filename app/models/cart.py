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
SELECT buyer_id, name, seller_id, product_id, quantity, Carts.price                             
FROM Carts, Products
WHERE Carts.buyer_id = :id and Carts.product_id = Products.id
''',
                              id=id)
        # perhaps shold make it so price updates from product table as well as name
        return [Cart(*row) for row in rows] if rows else []


    @staticmethod
    def addToCart(bid, sid, pid, quant, price):
        try:
            rows = app.db.execute("""
INSERT INTO Carts(
    bid, sid, pid, quant, price)
VALUES(:bid, :sid, :pid, :quant, :price)
RETURNING id
""",
                                  bid=bid,
                                  sid=sid,
                                  pid=pid, quant=quant, price=price)
            id = bid
            return Cart.get(id)
        except Exception as e:
            # likely email already in use; better error checking and reporting needed;
            # the following simply prints the error to the console:
            print(str(e))
            return None

