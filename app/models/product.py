from flask import current_app as app


class Product:
    def __init__(self, id, description, category, cid, name, price):
        self.id = id
        self.cid = cid
        self.name = name
        self.description = description
        self.category = category
        self.price = price

    @staticmethod
    def get_rating(id):
        result = app.db.execute('''
SELECT AVG(rating)
FROM Feedback
WHERE pid = :id
''', id=id)
        if result[0][0] is None:
            return "No Reviews"
        else:
            return round(result[0][0], 1)

    @staticmethod
    def get(id):
        rows = app.db.execute('''
SELECT *
FROM Products
WHERE id = :id
''',
                              id=id)
        return Product(*(rows[0])) if rows is not None else None

    @staticmethod
    def get_all():
        rows = app.db.execute('''
SELECT *
FROM Products
''')
        
        return [Product(*row) for row in rows]
    
    @staticmethod
    def get_k_products(k):
        rows = app.db.execute('''
SELECT *
FROM Products                             
ORDER BY price DESC
LIMIT :k;
''',
                              k=k)
    
        return rows
    
    @staticmethod
    def get_product_by_name(name):
        rows = app.db.execute('''
SELECT *
FROM Products
WHERE name = :name
''',
                              name=name)
        return Product(*(rows[0])) if rows is not None else None
    
    @staticmethod
    def get_cid_by_pid(pid):
        res = app.db.execute('''
SELECT creator_id
FROM Products
WHERE id = :id
''',
                              id=pid)
        return res[0][0] if res is not None else None
