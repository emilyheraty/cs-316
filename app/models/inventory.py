from flask import current_app as app


class Inventory:
    def __init__(self, id, product_name, number_available):
        self.id = id
        self.product_name = product_name
        self.number_available = number_available
    
    @staticmethod
    def getInventory(id):
        rows = app.db.execute('''
SELECT id, product_name, number_available
FROM Inventory
WHERE id = :id
ORDER BY number_available DESC
''',
                                id=id)
        return [Inventory(*row) for row in rows] # edit this for listing product name and num available
    

    @staticmethod
    def getPartialInventory(id, per_page, off):
        rows = app.db.execute('''
SELECT id, product_name, number_available
FROM Inventory
WHERE id = :id
ORDER BY number_available DESC
LIMIT :per_page
OFFSET :off
''',
                                id=id,
                                per_page=per_page,
                                off=off)
        return [Inventory(*row) for row in rows] # edit this for listing product name and num available


    @staticmethod
    def getInventoryProducts(str, per_page, off, id):
        print("trying out this")
        rows = app.db.execute('''
SELECT id, product_name, number_available
FROM Inventory
WHERE product_name LIKE '%' || :str || '%'
AND id=:id
ORDER BY number_available DESC
LIMIT :per_page
OFFSET :off
''',
                                id=id,
                                str=str,
                                per_page=per_page,
                                off=off)
        print("still trying man")
        return [Inventory(*row) for row in rows]

    @staticmethod
    def getSellerInfo(id):
        sid = app.db.execute('''
SELECT DISTINCT id, firstname
FROM Users
WHERE Users.id=:id
''',
                                id=id)
        print(sid)
        return sid # edit this for listing product name and num available

    @staticmethod
    def isSeller(id):
        bool = app.db.execute('''
SELECT DISTINCT is_seller
FROM Users
WHERE Users.id=:id
''',
                                id=id)
        return bool

    @staticmethod
    def addToInventory(id, product_name, number_available):
        try:
            rows = app.db.execute('''
INSERT INTO Inventory
VALUES (:id, :product_name, :number_available)
''', 
                                product_name=product_name,
                                number_available=number_available,
                                id=id)
            return 1
        except Exception as e:
            print("Cannot add this product to inventory. Check if this product is already in inventory.")
            return 0

    @staticmethod
    def removeProductFromInventory(id, product_name):
        res = app.db.execute('''
DELETE FROM Inventory
WHERE Inventory.id = :id AND Inventory.product_name = :product_name
''',
                                product_name=product_name,
                                id=id)
        return res


    @staticmethod
    def updateProductQuantity(id, product_name, number_available):
        print("hereeeee")
        res = app.db.execute('''
UPDATE Inventory
SET number_available = :number_available
WHERE Inventory.id = :id AND Inventory.product_name = :product_name
''',
                                product_name=product_name,
                                number_available=number_available,
                                id=id)
        print("updating")
        return res


#     @staticmethod
#     def addProductToInventory(id, product_name, number_available):
#         sid = app.db.execute('''
# INSERT INTO Inventory
# (SELECT :id, :product_name, :number_available
# FROM Products, Sellers
# WHERE Products.name = :product_name
# AND Sellers.id = :id)
# ''',
#                                 id=id)
class Listing:
    def __init__(self, sid, sfirstname, slastname, qty):
        self.sid = sid
        self.sfirstname = sfirstname
        self.slastname = slastname
        self.qty = qty
    
    @staticmethod
    def get_listings_by_product_name(name):
        rows = app.db.execute('''
SELECT Inventory.id, Users.firstname, Users.lastname, Inventory.number_available
FROM Inventory, Users
WHERE Inventory.product_name = :name and Inventory.id = Users.id
''',
                              name=name)
        return [Listing(*row) for row in rows] if rows is not None else None