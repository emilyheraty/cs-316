from flask import current_app as app


class Product:
    def __init__(self, id, name, description, category, price, review, rating, available, image):
        self.id = id
        self.name = name
        self.description = description
        self.category = category
        self.price = price
        self.review = review
        self.rating = rating
        self.available = available
        self.image = image

        
    @staticmethod
    def get(id):
        rows = app.db.execute('''
SELECT id, name, price, available
FROM Products
WHERE id = :id
''',
                              id=id)
        return Product(*(rows[0])) if rows is not None else None

    @staticmethod
    def get_all(available=True):
        rows = app.db.execute('''
SELECT id, name, price, available
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
SELECT id, name, price, available
FROM Products
WHERE name = :name
''',
                              name=name)
        return Product(*(rows[0])) if rows is not None else None
    


                          
    
        

        
        
    



