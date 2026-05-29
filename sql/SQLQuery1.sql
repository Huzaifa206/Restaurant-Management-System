CREATE DATABASE RestaurantDatabase;
USE RestaurantDatabase;

CREATE TABLE branches (
    branch_id INT IDENTITY(1,1) PRIMARY KEY,
    branch_name NVARCHAR(100) NOT NULL,
    city NVARCHAR(100),
    country NVARCHAR(100),
    phone NVARCHAR(20),
    address NVARCHAR(255),
    is_active BIT DEFAULT 1,
    created_at DATETIME DEFAULT GETDATE()
);

CREATE TABLE staff (
    staff_id INT IDENTITY(1,1) PRIMARY KEY,
    branch_id INT FOREIGN KEY REFERENCES branches(branch_id),
    full_name NVARCHAR(100) NOT NULL,
    role NVARCHAR(50) NOT NULL,  -- Admin, Manager, Chef, Waiter
    username NVARCHAR(50) UNIQUE NOT NULL,
    password_hash NVARCHAR(255) NOT NULL,
    phone NVARCHAR(20),
    salary DECIMAL(10,2),
    hire_date DATE DEFAULT GETDATE(),
    is_active BIT DEFAULT 1
);

CREATE TABLE customers (
    customer_id INT IDENTITY(1,1) PRIMARY KEY,
    full_name NVARCHAR(100),
    phone NVARCHAR(20),
    email NVARCHAR(100),
    address NVARCHAR(255),
    created_at DATETIME DEFAULT GETDATE()
);

CREATE TABLE categories (
    category_id INT IDENTITY(1,1) PRIMARY KEY,
    category_name NVARCHAR(100) NOT NULL,
    description NVARCHAR(255)
);

CREATE TABLE menu_items (
    item_id INT IDENTITY(1,1) PRIMARY KEY,
    category_id INT FOREIGN KEY REFERENCES categories(category_id),
    item_name NVARCHAR(100) NOT NULL,
    description NVARCHAR(255),
    price DECIMAL(10,2) NOT NULL,
    is_available BIT DEFAULT 1
);

CREATE TABLE restaurant_tables (
    table_id INT IDENTITY(1,1) PRIMARY KEY,
    branch_id INT FOREIGN KEY REFERENCES branches(branch_id),
    table_number INT NOT NULL,
    capacity INT DEFAULT 4,
    status NVARCHAR(20) DEFAULT 'Available'  -- Available, Occupied, Reserved
);

CREATE TABLE reservations (
    reservation_id INT IDENTITY(1,1) PRIMARY KEY,
    table_id INT FOREIGN KEY REFERENCES restaurant_tables(table_id),
    customer_id INT FOREIGN KEY REFERENCES customers(customer_id),
    reservation_date DATETIME NOT NULL,
    party_size INT,
    status NVARCHAR(20) DEFAULT 'Confirmed',  -- Confirmed, Cancelled, Completed
    notes NVARCHAR(255)
);

CREATE TABLE orders (
    order_id INT IDENTITY(1,1) PRIMARY KEY,
    branch_id INT FOREIGN KEY REFERENCES branches(branch_id),
    table_id INT FOREIGN KEY REFERENCES restaurant_tables(table_id),
    customer_id INT FOREIGN KEY REFERENCES customers(customer_id),
    staff_id INT FOREIGN KEY REFERENCES staff(staff_id),
    order_type NVARCHAR(20) DEFAULT 'Dine-in',  -- Dine-in, Takeaway, Online
    status NVARCHAR(30) DEFAULT 'Pending',       -- Pending, In Progress, Completed, Cancelled
    order_time DATETIME DEFAULT GETDATE(),
    total_amount DECIMAL(10,2) DEFAULT 0
);

CREATE TABLE order_details (
    detail_id INT IDENTITY(1,1) PRIMARY KEY,
    order_id INT FOREIGN KEY REFERENCES orders(order_id),
    item_id INT FOREIGN KEY REFERENCES menu_items(item_id),
    quantity INT NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL,
    subtotal AS (quantity * unit_price)  
);

CREATE TABLE suppliers (
    supplier_id INT IDENTITY(1,1) PRIMARY KEY,
    supplier_name NVARCHAR(100) NOT NULL,
    contact_person NVARCHAR(100),
    phone NVARCHAR(20),
    email NVARCHAR(100),
    address NVARCHAR(255),
    is_active BIT DEFAULT 1
);

CREATE TABLE inventory (
    inventory_id INT IDENTITY(1,1) PRIMARY KEY,
    branch_id INT FOREIGN KEY REFERENCES branches(branch_id),
    item_name NVARCHAR(100) NOT NULL,
    unit NVARCHAR(20),         
    quantity_in_stock DECIMAL(10,2) DEFAULT 0,
    reorder_level DECIMAL(10,2) DEFAULT 10,   -- Alert threshold
    last_updated DATETIME DEFAULT GETDATE()
);

CREATE TABLE purchases (
    purchase_id INT IDENTITY(1,1) PRIMARY KEY,
    supplier_id INT FOREIGN KEY REFERENCES suppliers(supplier_id),
    inventory_id INT FOREIGN KEY REFERENCES inventory(inventory_id),
    quantity DECIMAL(10,2) NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL,
    total_cost AS (quantity * unit_price),
    purchase_date DATETIME DEFAULT GETDATE(),
    status NVARCHAR(20) DEFAULT 'Ordered'    -- Ordered, Delivered
);

CREATE TABLE payments (
    payment_id INT IDENTITY(1,1) PRIMARY KEY,
    order_id INT FOREIGN KEY REFERENCES orders(order_id),
    amount_paid DECIMAL(10,2) NOT NULL,
    payment_method NVARCHAR(30) DEFAULT 'Cash',
    payment_time DATETIME DEFAULT GETDATE()
);

CREATE TABLE invoices (
    invoice_id INT IDENTITY(1,1) PRIMARY KEY,
    order_id INT FOREIGN KEY REFERENCES orders(order_id),
    payment_id INT FOREIGN KEY REFERENCES payments(payment_id),
    subtotal DECIMAL(10,2),
    tax_rate DECIMAL(5,2) DEFAULT 17.00,     -- 17% GST (Pakistan)
    tax_amount DECIMAL(10,2),
    total_amount DECIMAL(10,2),
    generated_at DATETIME DEFAULT GETDATE()
);

CREATE TABLE attendance (
    attendance_id INT IDENTITY(1,1) PRIMARY KEY,
    staff_id INT FOREIGN KEY REFERENCES staff(staff_id),
    check_in DATETIME,
    check_out DATETIME,
    date DATE DEFAULT CAST(GETDATE() AS DATE),
    status NVARCHAR(20) DEFAULT 'Present'  
);


INSERT INTO branches (branch_name, city, country, phone, address)
VALUES ('Main Branch', 'Karachi', 'Pakistan', '021-1234567', 'Clifton, Karachi');

INSERT INTO categories (category_name) VALUES ('Starters'), ('Main Course'), ('Beverages'), ('Desserts');

INSERT INTO staff (branch_id, full_name, role, username, password_hash, salary)
VALUES 
(1, 'Admin User', 'Admin', 'admin', 'admin123', 100000),
(1, 'Branch Manager', 'Manager', 'manager', 'manager123', 60000),
(1, 'Head Chef', 'Chef', 'chef', 'chef123', 45000),
(1, 'Waiter', 'Waiter', 'waiter', 'waiter123', 25000),
(1, 'Walk-in Customer', 'Customer', 'customer', 'customer123', 0),
(1, 'Main Supplier', 'Supplier', 'supplier', 'supplier123', 0);

INSERT INTO menu_items (category_id, item_name, price) VALUES
(1, 'Chicken Tikka', 350),
(1, 'Seekh Kebab', 280),
(2, 'Biryani', 450),
(2, 'Karahi', 600),
(3, 'Soft Drink', 80),
(3, 'Mineral Water', 60),
(4, 'Gulab Jamun', 120);

INSERT INTO restaurant_tables (branch_id, table_number, capacity) VALUES
(1, 1, 4), (1, 2, 4), (1, 3, 6), (1, 4, 2), (1, 5, 8);

select 