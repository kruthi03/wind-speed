import pandas as pd
import numpy as np
from hdfs.ext.kerberos import KerberosClient
import mysql.connector
 
# -------------------- 3️⃣ CONNECT TO HDFS --------------------
print("🔹 Connecting to HDFS...")
hdfs_client = KerberosClient('http://100.114.202.86:9000', mutual_auth='OPTIONAL')
 
# -------------------- 4️⃣ READ CSV FILES FROM HDFS --------------------
print("🔹 Reading CSV files from HDFS...")
 
with hdfs_client.read('/user/kruthi/webscrap/autoscout24_used_car_cleaned.csv') as reader:
    df_cars_com = pd.read_csv(reader, sep=',')
 
with hdfs_client.read('/user/kruthi/webscrap/cleaned_cars.com_final.csv') as reader:
    df_autoscout24 = pd.read_csv(reader, sep=',')
 
with hdfs_client.read('/user/kruthi/webscrap/edmunds_used_cars_cleanfinal.csv') as reader:
    df_edmunds = pd.read_csv(reader, sep=',')

# -------------------- 4️⃣ MERGE & CLEAN DATA --------------------
print("🔹 Merging CSV files into a single DataFrame...")
all_df = pd.concat([df_cars_com, df_autoscout24, df_edmunds], ignore_index=True)
all_df = all_df.replace(np.NaN, "")  # Replace NaN with empty strings or zeros
 
# Show sample data
print("🔹 Data Sample:\n", all_df.head())
print("🔹 Data Info:\n", all_df.info())
 
# -------------------- 5️⃣ CONNECT TO MYSQL DATABASE --------------------
print("🔹 Connecting to MySQL...")
db = mysql.connector.connect(
    host="192.168.56.102",  # Ensure this IP is correct for MySQL server on the master node
    user="root",
    password="b1234",
    database="automobile_db"
)
mycursor = db.cursor()
 
# -------------------- 6️⃣ CREATE TABLES --------------------
 
print("🔹 Creating tables if not exists...")
 
tables = {
    "Cars": """
        CREATE TABLE IF NOT EXISTS Cars (
            car_id VARCHAR(50) PRIMARY KEY,
            car_name VARCHAR(255),
            fuel_type VARCHAR(50),
            engine_size FLOAT,
            cylinders INT,
            performance_kw FLOAT,
            performance_ps FLOAT,
            transmission VARCHAR(50)
        );
    """,
    "Listings": """
        CREATE TABLE IF NOT EXISTS Listings (
            listing_id VARCHAR(50) PRIMARY KEY,
            car_id VARCHAR(50),
            price FLOAT,
            miles_driven INT,
            first_registration DATE,
            dealer_id VARCHAR(50),
            source VARCHAR(50),
            FOREIGN KEY (car_id) REFERENCES Cars(car_id),
            FOREIGN KEY (dealer_id) REFERENCES Dealers(dealer_id)
        );
    """,
    "Dealers": """
        CREATE TABLE IF NOT EXISTS Dealers (
            dealer_id VARCHAR(50) PRIMARY KEY,
            dealer_name VARCHAR(255),
            location VARCHAR(255),
            distance_miles FLOAT,
            saler_name VARCHAR(255)
        );
    """,
    "Car_History": """
        CREATE TABLE IF NOT EXISTS Car_History (
            history_id VARCHAR(50) PRIMARY KEY,
            car_id VARCHAR(50),
            accident_history TEXT,
            owner_count INT,
            usage_type VARCHAR(50),
            below_market_price BOOLEAN,
            FOREIGN KEY (car_id) REFERENCES Cars(car_id)
        );
    """,
    "Images": """
        CREATE TABLE IF NOT EXISTS Images (
            image_id VARCHAR(50) PRIMARY KEY,
            car_id VARCHAR(50),
            image_url TEXT,
            FOREIGN KEY (car_id) REFERENCES Cars(car_id)
        );
    """
}
 
# Execute table creation
for table, query in tables.items():
    mycursor.execute(query)
    print(f"✅ Table {table} created or already exists.")
 
# -------------------- 7️⃣ INSERT DATA INTO TABLES --------------------
 
print("🔹 Inserting data into tables...")
 
# ---- Insert Cars Data ----
insert_query_cars = """INSERT INTO Cars (car_id, car_name, fuel_type, engine_size, cylinders, performance_kw, performance_ps, transmission)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE car_name=VALUES(car_name);"""
 
cars_df = all_df[['car_id', 'car_name', 'fuel_type', 'engine_size', 'cylinders', 'performance_kw', 'performance_ps', 'transmission']].drop_duplicates()
for _, row in cars_df.iterrows():
    mycursor.execute(insert_query_cars, tuple(row))
 
# ---- Insert Listings Data ----
insert_query_listings = """INSERT INTO Listings (listing_id, car_id, price, miles_driven, first_registration, dealer_id, source)
VALUES (%s, %s, %s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE price=VALUES(price);"""
 
listings_df = all_df[['listing_id', 'car_id', 'price', 'miles_driven', 'first_registration', 'dealer_id', 'source']].drop_duplicates()
for _, row in listings_df.iterrows():
    mycursor.execute(insert_query_listings, tuple(row))
 
# ---- Insert Dealers Data ----
insert_query_dealers = """INSERT INTO Dealers (dealer_id, dealer_name, location, distance_miles, saler_name)
VALUES (%s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE dealer_name=VALUES(dealer_name);"""
 
dealers_df = all_df[['dealer_id', 'dealer_name', 'location', 'distance_miles', 'saler_name']].drop_duplicates()
for _, row in dealers_df.iterrows():
    mycursor.execute(insert_query_dealers, tuple(row))
 
# ---- Insert Car History Data ----
insert_query_car_history = """INSERT INTO Car_History (history_id, car_id, accident_history, owner_count, usage_type, below_market_price)
VALUES (%s, %s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE accident_history=VALUES(accident_history);"""
 
car_history_df = all_df[['history_id', 'car_id', 'accident_history', 'owner_count', 'usage_type', 'below_market_price']].drop_duplicates()
for _, row in car_history_df.iterrows():
    mycursor.execute(insert_query_car_history, tuple(row))
 
# ---- Insert Images Data ----
insert_query_images = """INSERT INTO Images (image_id, car_id, image_url)
VALUES (%s, %s, %s) ON DUPLICATE KEY UPDATE image_url=VALUES(image_url);"""
 
images_df = all_df[['image_id', 'car_id', 'image_url']].drop_duplicates()
for _, row in images_df.iterrows():
    mycursor.execute(insert_query_images, tuple(row))
 
# Commit all changes
db.commit()
print("✅ All data inserted successfully!")
 
# -------------------- 8️⃣ VERIFY DATA --------------------
 
print("🔹 Verifying data insertion...")
tables_to_check = ["Cars", "Listings", "Dealers", "Car_History", "Images"]
for table in tables_to_check:
    mycursor.execute(f"SELECT COUNT(*) FROM {table}")
    count = mycursor.fetchone()[0]
    print(f"✅ {table}: {count} records inserted.")
 
# -------------------- 9️⃣ CLOSE CONNECTION --------------------
 
db.close()
print("✅ All tasks completed successfully!")