import sqlite3
import os
import random
from datetime import datetime, timedelta
from faker import Faker
import uuid
import json
import string

# Database file path
DB_FILE = "ecommerce.db"

def generate_product_name(category, brand):
    """Generate a realistic product name"""
    adjectives = ['Pro', 'Elite', 'Premium', 'Ultra', 'Smart', 'Advanced', 'Essential']
    specs = ['4K', 'HD', 'Wireless', 'Bluetooth', 'Gaming', 'Professional', 'Enterprise']
    
    return f"{brand} {random.choice(adjectives)} {category} {random.choice(specs)}"

def init_database():
    """Initialize the database if it doesn't exist, otherwise just connect to it"""
    
    db_exists = os.path.exists(DB_FILE)
    
    # Connect to the database (creates it if it doesn't exist)
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Only create tables and populate with data if the database doesn't exist
    if not db_exists:
        print(f"Creating new database: {DB_FILE}")
        
        # Create tables
        create_tables(cursor)
        
        # Populate with sample data
        populate_products(cursor, 1000)
        populate_purchases(cursor, 1000)
        
        # Commit changes
        conn.commit()
        print("Database initialized with sample data.")
    else:
        print(f"Using existing database: {DB_FILE}")
    
    return conn, cursor

def create_tables(cursor):
    """Create the database tables"""
    
    # Create products table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS products (
        sku TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        category TEXT NOT NULL,
        brand TEXT NOT NULL,
        base_price DECIMAL(10,2) NOT NULL,
        current_price DECIMAL(10,2) NOT NULL,
        stock_quantity INTEGER NOT NULL,
        status TEXT,
        specifications JSON NOT NULL,
        description TEXT,
        release_day INTEGER,
        release_month INTEGER,
        release_year INTEGER,
        last_updated TIMESTAMP
    )
    ''')
    
    # Create purchases table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS purchases (
        purchase_id TEXT PRIMARY KEY,
        product_sku TEXT NOT NULL,
        purchase_day INTEGER,
        purchase_month INTEGER,
        purchase_year INTEGER,
        quantity INTEGER NOT NULL,
        unit_price DECIMAL(10,2) NOT NULL,
        total_amount DECIMAL(10,2) NOT NULL,
        basket_id TEXT NOT NULL,
        basket_status TEXT,
        basket_creation_day INTEGER,
        basket_creation_month INTEGER,
        basket_creation_year INTEGER,
        client_first_name TEXT NOT NULL,
        client_last_name TEXT NOT NULL,
        client_country TEXT NOT NULL,
        product_name TEXT NOT NULL,
        product_category TEXT NOT NULL,
        product_brand TEXT NOT NULL,
        product_specs JSON NOT NULL
    )
    ''')

def populate_products(cursor, num_products):
    fake = Faker()
    products_data = []
    for _ in range(num_products):
        category = random.choice(['Laptops', 'Desktop PCs', 'Monitors', 'Keyboards', 'Mice',
                                 'Headphones', 'Speakers', 'Webcams', 'Printers', 'Storage'])
        brand = random.choice(['Dell', 'HP', 'Lenovo', 'Apple', 'ASUS', 'Acer', 'LG', 'Samsung', 'BenQ', 'Logitech',
                               'Razer', 'Corsair', 'HyperX', 'SteelSeries', 'Sony', 'Bose', 'Sennheiser', 'JBL', 'Sonos',
                               'Harman Kardon'])
        base_price = round(random.uniform(50, 5000), 2)
        
        # Generate realistic specifications based on category
        specs = {
            "color": fake.color_name(),
            "weight": f"{random.randint(1, 10)} kg",
            "dimensions": f"{random.randint(10, 50)}x{random.randint(10, 50)}x{random.randint(2, 10)} cm"
        }
        
        # Add category-specific specifications
        if category == 'Laptops':
            specs.update({
                "screen_size": f"{random.choice([13, 14, 15, 16, 17])} inch",
                "processor": f"Intel Core i{random.randint(3, 9)} Gen {random.randint(10, 13)}",
                "ram": f"{random.choice([8, 16, 32, 64])}GB",
                "storage": f"{random.choice([256, 512, 1024, 2048])}GB SSD"
            })
        elif category == 'Monitors':
            specs.update({
                "resolution": random.choice(['1920x1080', '2560x1440', '3840x2160']),
                "refresh_rate": f"{random.choice([60, 75, 144, 165, 240])}Hz",
                "panel_type": random.choice(['IPS', 'VA', 'TN', 'OLED'])
            })

        # Get release date components
        release_date = fake.date_between(start_date='-2y', end_date='today')
        
        products_data.append((
            f"SKU-{uuid.uuid4().hex[:8].upper()}",
            generate_product_name(category, brand),
            category,
            brand,
            base_price,
            round(base_price * random.uniform(0.8, 1.2), 2),  # Current price varies ±20%
            random.randint(0, 1000),
            random.choice(['in_stock', 'low_stock', 'out_of_stock', 'discontinued']),
            json.dumps(specs),
            fake.text(max_nb_chars=200),
            release_date.day,      # Day component
            release_date.month,    # Month component
            release_date.year,     # Year component
            datetime.now()
        ))

    # Insert the products
    cursor.executemany("""
    INSERT INTO products (
        sku, name, category, brand, base_price, current_price, stock_quantity,
        status, specifications, description, release_day, release_month, release_year, last_updated
    )
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, products_data)

def populate_purchases(cursor, num_purchases):
    fake = Faker()
    products_data = cursor.execute("SELECT sku, current_price FROM products").fetchall()
    purchases_data = []
    used_purchase_ids = set()
    basket_info = {}  # Store basket information for reuse

    for _ in range(num_purchases):
        product = random.choice(products_data)
        purchase_date = fake.date_time_between(start_date='-5y')
        
        # Generate unique purchase ID
        while True:
            purchase_id = f"PUR-{purchase_date.strftime('%Y%m')}-{random.randint(10000, 99999)}"
            if purchase_id not in used_purchase_ids:
                used_purchase_ids.add(purchase_id)
                break

        # Generate or reuse basket information (30% chance to reuse existing basket)
        if basket_info and random.random() < 0.3:
            basket_id = random.choice(list(basket_info.keys()))
            basket_data = basket_info[basket_id]
        else:
            basket_id = f"BSKT-{purchase_date.strftime('%Y%m')}-{random.randint(1000, 9999)}"
            basket_creation_date = fake.date_time_between(
                start_date=purchase_date - timedelta(days=7),
                end_date=purchase_date
            )
            basket_data = {
                'status': random.choice(['completed', 'pending', 'cancelled', 'refunded']),
                'creation_day': basket_creation_date.day,
                'creation_month': basket_creation_date.month,
                'creation_year': basket_creation_date.year,
                'client_first_name': fake.first_name(),
                'client_last_name': fake.last_name(),
                'client_country': fake.country()
            }
            basket_info[basket_id] = basket_data

        # Calculate purchase details
        quantity = random.randint(1, 5)
        unit_price = float(product['current_price'])
        total_amount = quantity * unit_price

        # Extract relevant product specifications
        full_specs = json.loads(product['specifications'])
        relevant_specs = {
            "color": full_specs.get("color"),
            "dimensions": full_specs.get("dimensions")
        }
        
        if product['category'] == 'Laptops':
            relevant_specs.update({
                "screen_size": full_specs.get("screen_size"),
                "processor": full_specs.get("processor")
            })
        elif product['category'] == 'Monitors':
            relevant_specs.update({
                "resolution": full_specs.get("resolution"),
                "refresh_rate": full_specs.get("refresh_rate")
            })

        purchases_data.append((
            purchase_id,
            product['sku'],                    # product_sku
            purchase_date.day,
            purchase_date.month,
            purchase_date.year,
            quantity,
            unit_price,
            total_amount,
            basket_id,
            basket_data['status'],
            basket_data['creation_day'],
            basket_data['creation_month'],
            basket_data['creation_year'],
            basket_data['client_first_name'],
            basket_data['client_last_name'],
            basket_data['client_country'],
            product['name'],                    # product_name
            product['category'],                    # product_category
            product['brand'],                    # product_brand
            json.dumps(relevant_specs)
        ))

    # Insert the enhanced purchases data
    cursor.executemany("""
    INSERT INTO purchases (
        purchase_id, product_sku, 
        purchase_day, purchase_month, purchase_year,
        quantity, unit_price, total_amount,
        basket_id, basket_status, 
        basket_creation_day, basket_creation_month, basket_creation_year,
        client_first_name, client_last_name, client_country,
        product_name, product_category, product_brand, product_specs
    )
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, purchases_data)

if __name__ == "__main__":
    # If run directly, force recreate the database
    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)
        print(f"Deleted existing database: {DB_FILE}")
    
    conn, cursor = init_database()
    conn.close()
    print("Database initialization complete.") 