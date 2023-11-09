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
''',
                                id=id)
        return [Inventory(*row) for row in rows] # edit this for listing product name and num available

    @staticmethod
    def getSellerInfo(id):
        sid = app.db.execute('''
SELECT DISTINCT Sellers.id, firstname
FROM Inventory,Sellers,Users
WHERE Inventory.id=:id AND Sellers.id=:id AND Users.id=:id
''',
                                id=id)
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
        rows = app.db.execute('''
INSERT INTO Inventory
VALUES (:id, :product_name, :number_available)
''', 
                                product_name=product_name,
                                number_available=number_available,
                                id=id)
    # make this into a try/catch

    @staticmethod
    def removeProductFromInventory(id, product_name):
        sid = app.db.execute('''
DELETE FROM Inventory
WHERE Inventory.id = :id AND Inventory.product_name = :product_name
''',
                                product_name=product_name,
                                id=id)
        # return sid # edit this for listing product name and num available

    @staticmethod
    def updateProductQuantity(id, product_name, number_available):
        sid = app.db.execute('''
UPDATE Inventory
SET number_available = :number_available
WHERE Inventory.id = :id AND Inventory.product_name = :product_name
''',
                                product_name=product_name,
                                number_available=number_available,
                                id=id)
        # return sid # edit this for listing product name and num available


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