from flask import current_app as app



class Feedback():
    def __init__(self, id, user_id, pid, seller_id, review_type, rating, comment, time_posted):
        self.id = id
        self.user_id = user_id
        self.pid = pid
        self.seller_id = seller_id
        self.review_type = review_type
        self.rating = rating
        self.comment = comment
        self.time_posted = time_posted


    @staticmethod
    def get_recent_feedback(user_id, limit):

        sql = """
        SELECT * FROM Feedback
        WHERE user_id = :user_id
        ORDER BY time_posted DESC
        LIMIT :limit
        """
        results = app.db.execute(sql, user_id=user_id, limit=limit)
        
        feedbacks = []
        for result in results:
            feedback = Feedback(
            id = result[0],
            user_id = result[1],
            pid = result[2],
            seller_id = result[3],
            review_type = result[4],
            rating = result[5],
            comment = result[6],
            time_posted = result[7])
            feedbacks.append(feedback)
        
        return feedbacks


    @staticmethod
    def get_all_feedback(user_id):
        rows = app.db.execute("""
        SELECT * 
        FROM Feedback
        WHERE user_id = :user_id
        ORDER BY time_posted DESC
        """,
        user_id=user_id)
        
        return [Feedback(*row) for row in rows]
    
    @staticmethod
    def get_all_feedback_p(user_id):
        rows = app.db.execute("""
        SELECT * 
        FROM Feedback
        WHERE user_id = :user_id
        AND review_type = 'product'
        ORDER BY time_posted DESC
        """,
        user_id=user_id)
        
        return [Feedback(*row) for row in rows]
    
    @staticmethod
    def check_past(pid, user_id):
        rows = app.db.execute("""
            SELECT *
            FROM Feedback
            WHERE user_id = :user_id
            AND pid = :pid
            AND review_type = 'product'""", user_id = user_id, pid = pid)
        return len(rows)>0
    
    @staticmethod
    def get_prod_recent_feedback(pid, limit):
        rows = app.db.execute( """
        SELECT * FROM Feedback
        WHERE pid = :pid
        ORDER BY time_posted DESC
        LIMIT :limit
        """, pid = pid, limit = limit)
        return rows
    
    
    @staticmethod
    def check_past_seller(seller_id, user_id):
        rows = app.db.execute("""
            SELECT *
            FROM Feedback
            WHERE user_id = :user_id
            AND seller_id = :seller_id
            AND review_type = 'seller'""", user_id = user_id, seller_id = seller_id)
        return len(rows)>0
    
    @staticmethod
    def check_purchased(seller_id, user_id):
        rows = app.db.execute("""
            SELECT *
            FROM Purchases, Products
            WHERE Purchases.uid = :user_id
            AND Products.id = Purchases.pid
            AND Products.creaor_id = :seller_id""", seller_id = seller_id, user_id = user_id)
        return len(rows)>0

    @staticmethod
    def add_product_feedback(user_id, pid, seller_id, review_type, rating, comment, time_posted):
        feedbackCount = app.db.execute("""
        SELECT
        COUNT(id)
        FROM Feedback                             
        """)
        rows = app.db.execute("""
        INSERT INTO Feedback(id, user_id, pid, seller_id, review_type, rating, comment, time_posted)
        VALUES(:id, :user_id, :pid, :seller_id, :review_type, :rating, :comment, :time_posted)
        RETURNING id
                              """,
            id=feedbackCount[0][0]+2, user_id = user_id, pid = pid, 
            seller_id = seller_id, review_type = review_type, rating = rating, comment = comment,
            time_posted = time_posted)
        return 1

    @staticmethod
    def edit_feedback(id, rating, comment, time_posted):
        new = app.db.execute("""
            UPDATE Feedback
            SET rating = :rating, comment = :comment, time_posted = :time_posted
            WHERE id = :id""", id = id, rating = rating, comment = comment, time_posted = time_posted)
        return new
    
    
    def delete_feedback(id):
        rows = app.db.execute("""
            DELETE FROM Feedback
            WHERE id = :id       
                               """, id = id)
        return 1
    
    
    def get_feedback_info(id):
        rows = app.db.execute("""
                 SELECT Feedback.rating, Feedback.comment, Feedback.id, Products.name, Feedback.pid
                 FROM Feedback, Products
                 WHERE Feedback.id = :id AND Feedback.pid = Products.id""", id = id)
        return rows

    @staticmethod
    def get_partial_feedback(user_id, per_page, off):
        rows = app.db.execute("""
            
            SELECT DISTINCT Feedback.id, Feedback.rating, Feedback.comment, Feedback.time_posted, Products.name, Feedback.pid, Feedback.review_type
            FROM Feedback, Purchases, Products, Inventory
            WHERE Feedback.user_id = :user_id AND
            Feedback.pid = Products.id AND
            Products.creator_id = Inventory.id                       
            ORDER BY time_posted DESC
            LIMIT :per_page
            OFFSET :off
                              """,
                              user_id = user_id, per_page = per_page, off = off)
        return rows
    

    @staticmethod
    def get_partial_feedback_s(user_id, per_page, off):
        rows = app.db.execute("""
            SELECT p.rating, p.comment, p.time_posted, p.name, p.pid, p.id 
            FROM (
                              SELECT Feedback.id, Feedback.rating, Feedback.comment, Feedback.time_posted, Products.name, Feedback.pid, Feedback.review_type
                              FROM Feedback 
                                    INNER JOIN Products ON Feedback.pid = Products.id
                              WHERE user_id = :user_id AND Feedback.review_type = 'seller'
                              ) as p
            ORDER BY time_posted DESC
            LIMIT :per_page
            OFFSET :off
                              """,
                              user_id = user_id, per_page = per_page, off = off)
        return rows
    
    @staticmethod
    def get_partial_feedback_p(user_id, per_page, off):
        rows = app.db.execute("""
            SELECT p.rating, p.comment, p.time_posted, p.name, p.pid, p.id 
            FROM (
                              SELECT Feedback.id, Feedback.rating, Feedback.comment, Feedback.time_posted, Products.name, Feedback.pid, Feedback.review_type
                              FROM Feedback 
                                    INNER JOIN Products ON Feedback.pid = Products.id
                              WHERE user_id = :user_id AND Feedback.review_type = 'product'
                              ) as p
            ORDER BY time_posted DESC
            LIMIT :per_page
            OFFSET :off

                              """,
                              user_id = user_id, per_page = per_page, off = off)
        return rows
    
   # @staticmethod
   # def get(id):
   #     rows = app.db.execute("""
   #         SELECT id, pid, rating
   #         FROM Feedback
   #         WHERE id = :id
   #         """, id = id)
   #     return Feedback(*(rows[0])) if rows else None
    
    @staticmethod
    def pending_products(uid):
        rows = app.db.execute("""
        SELECT DISTINCT Purchases.pid
        FROM Purchases, Feedback
        WHERE Purchases.uid = :uid 
        AND NOT EXISTS(
                              SELECT *
                              FROM Feedback, Purchases
                              WHERE Feedback.user_id = :uid AND Feedback.pid = Purchases.pid
        )
        """, uid = uid)
        return rows
    

    @staticmethod
    def get_seller(pid):
        rows = app.db.execute("""
        SELECT DISTINCT Products.creator_id
        FROM Products
        WHERE Products.id = :pid
                              """, pid = pid)

        return rows
    

    @staticmethod
    def avg_rating_product(pid):
        avg = app.db.execute("""
                SELECT AVG(Feedback.rating)
                FROM Feedback
                WHERE pid = :pid
                AND review_type = 'product'
                             """, pid = pid)
        return avg


    @staticmethod
    def avg_rating_seller(seller_id):
        avg = app.db.execute("""
                SELECT AVG(Feedback.rating)
                FROM Feedback
                WHERE seller_id = :seller_id
                AND review_type = 'seller'
                             """, seller_id = seller_id)
        return avg


    @staticmethod
    def num_rating_seller(seller_id):
        num = app.db.execute("""
                SELECT COUNT(*)
                FROM Feedback
                WHERE seller_id = :seller_id
                AND review_type = 'seller'
                             """, seller_id = seller_id)
        return num
    
    @staticmethod
    def num_rating_product(pid):
        num = app.db.execute("""
                SELECT COUNT(*)
                FROM Feedback
                WHERE pid = :pid
                AND review_type = 'product'
                             """, pid = pid)
        return num


    @staticmethod
    def get_partial_pending(uid, per_page, off):
        rows = app.db.execute("""
        SELECT DISTINCT p2.pid, p2.name
        FROM (
                    SELECT DISTINCT p.pid, p.name, p.fulfillment_status
                    FROM (SELECT name, p2.id, pid, uid, fulfillment_status 
                    FROM Products as p1
                    INNER JOIN Purchases as p2 ON p2.pid = p1.id 
                    WHERE uid = :uid) AS p 
        ) AS p2 
                              WHERE NOT EXISTS(SELECT *
                              FROM Feedback
                              WHERE Feedback.pid = p2.pid
                            ) AND p2.fulfillment_status = 1
        LIMIT :per_page
        OFFSET :off
        """, uid = uid, per_page = per_page, off = off)
        return rows
    
    @staticmethod
    def get_customer_feedback_seller(seller_id):
        rows = app.db.execute("""
            SELECT *
            FROM Feedback
            WHERE seller_id = :seller_id AND
            review_type = 'seller'
                              """, seller_id=seller_id)
        return rows
    

    @staticmethod
    def get_partial_customer_feedback_seller(seller_id, per_page, off):
        rows = app.db.execute("""
            SELECT *
            FROM Feedback
            WHERE seller_id = :seller_id AND
            review_type = 'seller'
            LIMIT :per_page
            OFFSET :off
                              """, seller_id = seller_id, per_page = per_page, off = off)
        return rows
    

    @staticmethod
    def seller_to_review(user_id):
        rows = app.db.execute(""" 
        SELECT DISTINCT Sellers.id
        FROM Feedback, Purchases, Products, Sellers
        WHERE Purchases.uid = :user_id
        AND Purchases.pid = Products.id
        AND Products.creator_id = Sellers.id
        AND NOT EXISTS (
                              SELECT *
                              FROM Feedback, Sellers
                              WHERE Feedback.seller_id = Sellers.id
                              AND Feedback.review_type = 'seller'

        )
        """, user_id = user_id)
        return rows
    

    @staticmethod
    def partial_seller_to_review(user_id, per_page, off):
        rows = app.db.execute(""" 
        SELECT DISTINCT Sellers.id
        FROM Feedback, Purchases, Products, Sellers
        WHERE Purchases.uid = :user_id
        AND Purchases.pid = Products.id
        AND Products.creator_id = Sellers.id
        AND NOT EXISTS (
                              SELECT *
                              FROM Feedback, Sellers
                              WHERE Feedback.seller_id = Sellers.id
                              AND Feedback.review_type = 'seller'

        )
            LIMIT :per_page
            OFFSET :off
        """, user_id = user_id, per_page = per_page, off = off)

        return rows
    

    @staticmethod
    def get_customer_feedback_product(seller_id):
        rows = app.db.execute("""
            SELECT *
            FROM Feedback
            WHERE seller_id = :seller_id AND
            review_type = 'product' 
                              """, seller_id=seller_id)
        return rows
    

    @staticmethod
    def get_partial_customer_feedback_product(seller_id, per_page, off):
        rows = app.db.execute("""
            SELECT *
            FROM Feedback
            WHERE seller_id = :seller_id AND
            review_type = 'product'
            LIMIT :per_page
            OFFSET :off
                              """, seller_id = seller_id, per_page = per_page, off = off)
        return rows


    @staticmethod
    def get_purchase_name_pending(uid):
        rows = app.db.execute("""
        SELECT DISTINCT p2.pid, p2.name
        FROM (
                    SELECT DISTINCT p.pid, p.name, p.fulfillment_status
                    FROM (SELECT name, p2.id, pid, uid, fulfillment_status 
                    FROM Products as p1
                    INNER JOIN Purchases as p2 ON p2.pid = p1.id 
                    WHERE uid = :uid) AS p 
        ) AS p2 
                              WHERE NOT EXISTS(SELECT *
                              FROM Feedback
                              WHERE Feedback.pid = p2.pid
                            ) AND p2.fulfillment_status = 1
        
                """, uid = uid)
        return rows
    

    @staticmethod
    def get_purchase_name_posted(uid):
        rows = app.db.execute("""
                SELECT DISTINCT p.pid, p.name
                FROM (SELECT name, p2.id, pid, uid 
                    FROM Products as p1
                    INNER JOIN Purchases as p2 ON p2.pid = p1.id 
                    WHERE uid = :uid) as p
                """, uid = uid)
        return rows
    

    @staticmethod
    def seller_review_check(seller_id):
        
        rows = app.db.execute("""
                        SELECT *
                        FROM Feedback
                        WHERE seller_id = :seller_id AND review_type = 'seller'""", seller_id = seller_id)
        return len(rows)>0
 

