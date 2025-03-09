import sqlite3
import random
from datetime import datetime, timedelta
from faker import Faker
import uuid
import json

def generate_product_name(category, brand):
    """Generate a realistic product name"""
    adjectives = ['Pro', 'Elite', 'Premium', 'Ultra', 'Smart', 'Advanced', 'Essential']
    specs = ['4K', 'HD', 'Wireless', 'Bluetooth', 'Gaming', 'Professional', 'Enterprise']
    
    return f"{brand} {random.choice(adjectives)} {category} {random.choice(specs)}"

def init_database():
    fake = Faker()
    conn = sqlite3.connect("ecommerce.db")
    cursor = conn.cursor()

    # Create products table with comprehensive information
    cursor.execute("DROP TABLE IF EXISTS products")
    cursor.execute("""
    CREATE TABLE products (
        sku TEXT PRIMARY KEY,                    -- Unique product identifier (e.g., SKU-A12B34CD)
        name TEXT NOT NULL,                      -- Full product name (e.g., Dell Pro Laptop Gaming)
        category TEXT NOT NULL,                  -- Product category (e.g., Laptops, Monitors)
        brand TEXT NOT NULL,                     -- Manufacturer (e.g., Dell, HP, Apple)
        base_price DECIMAL(10,2) NOT NULL,       -- Standard retail price
        current_price DECIMAL(10,2) NOT NULL,    -- Current selling price (may differ from base price)
        stock_quantity INTEGER NOT NULL,         -- Current inventory level
        status TEXT CHECK(                       -- Product availability status
            status IN ('in_stock', 'low_stock', 'out_of_stock', 'discontinued')
        ),
        specifications JSON NOT NULL,            -- Technical specifications as JSON
        description TEXT,                        -- Detailed product description
        release_day INTEGER CHECK(release_day BETWEEN 1 AND 31),    -- Day of release
        release_month INTEGER CHECK(release_month BETWEEN 1 AND 12), -- Month of release
        release_year INTEGER,                    -- Year of release
        last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP  -- Last record update time
    )
    """)

    # Define product categories and brands
    categories = [
        'Laptops', 'Desktop PCs', 'Monitors', 'Keyboards', 'Mice',
        'Headphones', 'Speakers', 'Webcams', 'Printers', 'Storage'
    ]
    
    brands = {
        'Laptops': ['Dell', 'HP', 'Lenovo', 'Apple', 'ASUS', 'Acer'],
        'Desktop PCs': ['Dell', 'HP', 'Lenovo', 'Apple', 'ASUS'],
        'Monitors': ['Dell', 'LG', 'Samsung', 'ASUS', 'BenQ'],
        'Keyboards': ['Logitech', 'Razer', 'Corsair', 'HyperX', 'SteelSeries'],
        'Mice': ['Logitech', 'Razer', 'Corsair', 'SteelSeries'],
        'Headphones': ['Sony', 'Bose', 'Sennheiser', 'JBL', 'Apple'],
        'Speakers': ['Bose', 'JBL', 'Sonos', 'Logitech', 'Harman Kardon'],
        'Webcams': ['Logitech', 'Microsoft', 'Razer', 'ASUS'],
        'Printers': ['HP', 'Epson', 'Canon', 'Brother'],
        'Storage': ['Samsung', 'Western Digital', 'Seagate', 'Crucial', 'Kingston']
    }

    # Generate 1000 products
    products_data = []
    for _ in range(1000):
        category = random.choice(categories)
        brand = random.choice(brands[category])
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

    # Create purchases table with enhanced basket and client information
    cursor.execute("DROP TABLE IF EXISTS purchases")
    cursor.execute("""
    CREATE TABLE purchases (
        purchase_id TEXT PRIMARY KEY,        -- Format: PUR-YYYYMM-XXXXX
        product_sku TEXT NOT NULL,           -- Reference to original product
        
        -- Purchase date information
        purchase_day INTEGER CHECK(purchase_day BETWEEN 1 AND 31),
        purchase_month INTEGER CHECK(purchase_month BETWEEN 1 AND 12),
        purchase_year INTEGER,
        
        -- Product purchase details
        quantity INTEGER NOT NULL,
        unit_price DECIMAL(10,2) NOT NULL,
        total_amount DECIMAL(10,2) NOT NULL,
        
        -- Basket information
        basket_id TEXT NOT NULL,
        basket_status TEXT CHECK(basket_status IN ('completed', 'pending', 'cancelled', 'refunded')),
        basket_creation_day INTEGER CHECK(basket_creation_day BETWEEN 1 AND 31),
        basket_creation_month INTEGER CHECK(basket_creation_month BETWEEN 1 AND 12),
        basket_creation_year INTEGER,
        
        -- Client information
        client_first_name TEXT NOT NULL,
        client_last_name TEXT NOT NULL,
        client_country TEXT NOT NULL,
        
        -- Product snapshot at purchase time
        product_name TEXT NOT NULL,
        product_category TEXT NOT NULL,
        product_brand TEXT NOT NULL,
        product_specs JSON NOT NULL,
        
        FOREIGN KEY (product_sku) REFERENCES products(sku)
    )
    """)

    # Generate 1000 purchases with enhanced information
    purchases_data = []
    used_purchase_ids = set()
    basket_info = {}  # Store basket information for reuse

    for _ in range(1000):
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
        unit_price = float(product[5])
        total_amount = quantity * unit_price

        # Extract relevant product specifications
        full_specs = json.loads(product[8])
        relevant_specs = {
            "color": full_specs.get("color"),
            "dimensions": full_specs.get("dimensions")
        }
        
        if product[2] == 'Laptops':
            relevant_specs.update({
                "screen_size": full_specs.get("screen_size"),
                "processor": full_specs.get("processor")
            })
        elif product[2] == 'Monitors':
            relevant_specs.update({
                "resolution": full_specs.get("resolution"),
                "refresh_rate": full_specs.get("refresh_rate")
            })

        purchases_data.append((
            purchase_id,
            product[0],                    # product_sku
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
            product[1],                    # product_name
            product[2],                    # product_category
            product[3],                    # product_brand
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

    # Commit changes
    conn.commit()
    return conn, cursor

if __name__ == "__main__":
    init_database() 