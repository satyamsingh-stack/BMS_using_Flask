import sqlite3

conn = sqlite3.connect('Bank_Database.db')

cur = conn.cursor()

cur.execute("CREATE TABLE IF NOT EXISTS Admin (user_id TEXT, password TEXT)") 
print("Admin table is created successfully")

cur.execute('''INSERT INTO Admin (user_id, password) VALUES (?,?)''', ("Admin", "Admin@123"))
cur.execute('''INSERT INTO Admin (user_id, password) VALUES (?, ?)''', ("Satyam","Satyam@123"))
conn.commit()

print("The data is inserted into the admin table")

cur.execute('''CREATE TABLE IF NOT EXISTS User (SSN TEXT, first TEXT, last TEXT, age INTEGER, city TEXT, gender TEXT, email TEXT, user_id TEXT, password TEXT, accNo INTEGER, balance REAL)''')
conn.commit()

print("Customers table is created successfully")
