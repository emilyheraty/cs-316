from werkzeug.security import generate_password_hash
import csv
from faker import Faker
import re

num_users = 100
num_products = 1000
num_purchases = 2500
num_carts = 200
num_feedback = 800
num_inventory = 2000

Faker.seed(0)
fake = Faker()

def getState(address):
    regex = r',\s*([A-Za-z]{2})\s+\d{5}'
    state = re.search(regex, address)
    if state:
        return state.group(1)
    else:
        return

def get_csv_writer(f):
    return csv.writer(f, dialect='unix')


def gen_users(num_users):
    sellers = []

    with open('Users.csv', 'w') as f:
        writer = get_csv_writer(f)
        print('Users...', end=' ', flush=True)
        for uid in range(num_users):
            if uid % 10 == 0:
                print(f'{uid}', end=' ', flush=True)
            profile = fake.profile()
            email = profile['mail']
            # plain_password = f'pass{uid}'
            # password = generate_password_hash(plain_password)
            password = fake.sentence(nb_words=1)[:-1]
            name_components = profile['name'].split(' ')
            firstname = name_components[0]
            lastname = name_components[-1]
            address = profile['residence']
            state = getState(address)
            balance = fake.pyfloat(right_digits=2, positive=True, min_value = 0.01, max_value = 999999999.99)
            is_seller = fake.random_int(min=0,max=1)  # need to edit this!!!
            writer.writerow([uid, email, password, firstname, lastname, address, state, balance, is_seller])
            sellers.append(is_seller)
        print(f'{num_users} generated')
    return sellers

def gen_sellers(sellers):
    seller_ids = []
    with open('Sellers.csv', 'w') as f:
        writer = get_csv_writer(f)
        print('Sellers...', end=' ', flush=True)
        for sid in range(num_users):
            if sid % 10 == 0:
                print(f'{sid}', end=' ', flush=True)
            if sellers[sid] == 1:
                writer.writerow([sid])
                seller_ids.append(sid)
    return seller_ids

def gen_products(num_products, seller_ids):
    available_pids = []
    product_names = []
    nameset = set()

    name_elements = []
    description_elements = []

    with open('Woo_Product_Dummy_Data_Set_Simple_and_Variable.csv', newline='') as csvfile:
        data = csv.reader(csvfile)
        for row in data:
            name_elements.append(row[0])
            des = re.finditer(r'<p>.*?</p>', row[1])

    with open('Products.csv', 'w') as f:
        writer = get_csv_writer(f)
        print('Products...', end=' ', flush=True)
        for pid in range(num_products):
            if pid % 100 == 0:
                print(f'{pid}', end=' ', flush=True)
            name = fake.random_element(elements = name_elements)
            if name in nameset:
                pid-=1
                continue
            nameset.add(name)    
            cid = fake.random_element(elements=seller_ids)
            price = f'{str(fake.random_int(max=500))}.{fake.random_int(max=99):02}'
            description = fake.sentence(nb_words=50)[:-1]
            category = fake.random_element(elements=('food', 'household products', 'clothing', 'books'))
          #rating = f'{str(fake.random_int(max=4))}.{fake.random_int(max=.9):02}'
            available_pids.append(pid)
            product_names.append(name)
            writer.writerow([pid, description, category, cid, name, price])
        print(f'{num_products} generated; {len(available_pids)} available')
    return available_pids, product_names


def gen_purchases(num_purchases, available_pids):
    with open('Purchases.csv', 'w') as f:
        writer = get_csv_writer(f)
        print('Purchases...', end=' ', flush=True)
        for id in range(num_purchases):
            if id % 100 == 0:
                print(f'{id}', end=' ', flush=True)
            uid = fake.random_int(min=0, max=num_users-1)
            pid = fake.random_element(elements=available_pids)
            sid = fake.random_element(elements=seller_ids)
            time_purchased = fake.date_time()
            total_amount = fake.pyfloat(right_digits=2, positive=True, min_value = 0.01, max_value = 999999999.99)
            number_of_items = fake.random_int(min=0, max=100)
            fulfillment_status = fake.date_time()
            writer.writerow([id, uid, pid, sid, time_purchased, total_amount, number_of_items, fulfillment_status, 0])
        print(f'{num_purchases} generated')
    return

def gen_carts(num_carts, seller_ids):
    keyset = set()
    num = num_carts
    with open('Carts.csv', 'w') as f:
        writer = get_csv_writer(f)
        print('Carts...', end=' ', flush=True)
        for i in range(num_carts):
            if i % 100 == 0:
                print(f'{i}', end=' ', flush=True)
            bid = fake.random_int(min=0, max=num_users-1)
            sid = fake.random_element(elements=seller_ids)
            pid = fake.random_int(min=0, max=num_products-1)
            if (bid, pid) in keyset or bid==sid:
                num -= 1
                continue
            keyset.add((bid, pid))
            quantity = fake.random_int(min=1, max=1000)
            writer.writerow([bid, sid, pid, quantity])
        print(f'{num} generated')
    return


def gen_inventory(num_inventory, seller_ids, product_names):
    keyset = set()
    num = num_inventory
    with open('Inventory.csv', 'w') as f:
        writer = get_csv_writer(f)
        print('Inventory...', end=' ', flush=True)
        for i in range(num_inventory):
            if i % 100 == 0:
                print(f'{i}', end=' ', flush=True)
            sid = fake.random_element(elements=seller_ids)
            product_name = fake.random_element(elements=product_names)
            if (sid, product_name) in keyset:
                num -= 1
                continue
            keyset.add((sid, product_name))
            quantity = fake.random_int(min=0, max=1000)
            writer.writerow([sid, product_name, quantity])
        print(f'{num} generated')
    return


def gen_feedback(num_feedback, available_pids, seller_ids):
    with open('Feedback.csv', 'w') as f:
        writer = get_csv_writer(f)
        print('Feedback...', end=' ', flush=True)
        for i in range(num_feedback):
            if i % 100 == 0:
                print(f'{i}', end=' ', flush=True)
            id = i
            uid = fake.random_int(min=0, max=num_users-1)
            pid = fake.random_element(elements=available_pids)
            seller_id = fake.random_element(elements=seller_ids)
            review_type = fake.random_element(elements=('product','seller'))
            rating = fake.random_int(min=1, max=5)
            comment = fake.sentence(nb_words=5)[:-1]
            time_posted = fake.date_time()
            writer.writerow([id, uid, pid, seller_id, review_type, rating, comment, time_posted])
        print(f'{num_feedback} generated')
    return

sellers = gen_users(num_users)
seller_ids = gen_sellers(sellers)
available_pids, product_names = gen_products(num_products, seller_ids)
gen_purchases(num_purchases, available_pids)
gen_carts(num_carts, seller_ids)
gen_inventory(num_inventory, seller_ids, product_names)
gen_feedback(num_feedback, available_pids, seller_ids)
