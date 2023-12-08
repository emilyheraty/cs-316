from flask import current_app as app


class Product:
    def __init__(self, id, description, category, sid, name, price, available):
        self.id = id
        self.sid = sid
        self.name = name
        self.description = description
        self.category = category
        self.price = price
        self.available = available

    @staticmethod
    def get_rating(id):
        result = app.db.execute('''
SELECT AVG(rating)
FROM Feedback
WHERE pid = :id
''', id=id)
        if result is not None:
            return "No Reviews"
        else:
            return round(result[0][0], 3)


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
    def get_all(available=True):
        rows = app.db.execute('''
SELECT *
FROM Products
WHERE available = :available
''',
                              available=available)
        
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
    def get_by_name(name):
        rows = app.db.execute('''
SELECT *
FROM Products
WHERE name = :name
''',
                              name=name)
        return Product(*(rows[0])) if rows is not None else None
    


                          
    
        

        
        
    



