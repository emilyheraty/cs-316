-- Feel free to modify this file to match your development goal.
-- Here we only create 3 tables for demo purpose.

CREATE TABLE Users (
    id INT NOT NULL PRIMARY KEY GENERATED BY DEFAULT AS IDENTITY,
    email VARCHAR UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    firstname VARCHAR(255) NOT NULL,
    lastname VARCHAR(255) NOT NULL,
    address VARCHAR(255) NOT NULL,
    balance DECIMAL(12, 2) NOT NULL,
    is_seller INT NOT NULL CHECK(is_seller IN (0, 1))
);

CREATE TABLE Sellers (
     id INT NOT NULL PRIMARY KEY REFERENCES Users(id)
);

CREATE TABLE Products (
    id INT NOT NULL PRIMARY KEY GENERATED BY DEFAULT AS IDENTITY,
    description VARCHAR(1000) NOT NULL,
    category VARCHAR(255) NOT NULL,
    creator_id INT NOT NULL REFERENCES Users(id),
    name VARCHAR(255) UNIQUE NOT NULL,
    price DECIMAL(12,2) NOT NULL,
    available BOOLEAN DEFAULT TRUE
);

CREATE TABLE Purchases (
    id INT NOT NULL PRIMARY KEY GENERATED BY DEFAULT AS IDENTITY,
    uid INT NOT NULL REFERENCES Users(id),
    pid INT NOT NULL REFERENCES Products(id),
    time_purchased timestamp without time zone NOT NULL DEFAULT (current_timestamp AT TIME ZONE 'UTC'),
    total_amount DECIMAL(12,2) NOT NULL,
    number_of_items INT NOT NULL,
    fulfillment_status INT NOT NULL CHECK(fulfillment_status IN (0, 1))
);

CREATE TABLE Carts (
    buyer_id INT NOT NULL REFERENCES Users(id),
    seller_id INT NOT NULL REFERENCES Users(id), -- TODO: check seller-d != buyer_id
    product_id INT NOT NULL REFERENCES Products(id),
    quantity INT NOT NULL,
    PRIMARY KEY (buyer_id, product_id)
);

CREATE TABLE Inventory (
    id INT NOT NULL REFERENCES Users(id),
    product_name VARCHAR(255) REFERENCES Products(name),
    number_available INT NOT NULL,
    PRIMARY KEY(id,product_name)
);

CREATE TABLE Feedback (
    id INT NOT NULL PRIMARY KEY GENERATED BY DEFAULT AS IDENTITY,
    user_id INT NOT NULL REFERENCES Users(id),
    pid INT NOT NULL REFERENCES Products(id),
    rating INT NOT NULL,
    comment TEXT,
    time_posted timestamp without time zone NOT NULL DEFAULT (current_timestamp AT TIME ZONE 'UTC')
);