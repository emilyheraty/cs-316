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
    def getSellerName(id):
        sid = app.db.execute('''
SELECT DISTINCT firstname
FROM Inventory,Users
WHERE Inventory.id=:id AND Users.id=:id
''',
                                id=id)
        return sid # edit this for listing product name and num available