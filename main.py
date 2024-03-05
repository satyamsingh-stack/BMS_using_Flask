from flask import Flask, render_template, url_for, request, redirect, session
import sqlite3
import random
import threading
conn = sqlite3.connect('Bank_Database.db', check_same_thread=False)
cur = conn.cursor()
app = Flask(__name__)
app.secret_key = "12345"

@app.route("/")
def dash():
    return render_template("welcome.html")
@app.route("/welcome")
def welcome():
    return render_template("welcome.html")
@app.route("/adminlogin", methods=["GET", "POST"])
def adminLogin():
    return render_template('adminlogin.html')
@app.route("/adminDash", methods=['GET', 'POST'])
def adminDash():
    global user_id2, user_id, password
    if request.method == 'POST':
        user_id = request.form['username']
        password = request.form['password']
        cur.execute('''SELECT user_id FROM Admin''')
        user_id2 = cur.fetchall()
        for i in user_id2:
            if user_id == i[0]:
                cur.execute('''SELECT password FROM Admin WHERE user_id = ?''', (user_id,))
                password2 = cur.fetchone()[0]
                if password == password2:
                    session['user_id'] = user_id
                    return render_template("adminDash.html")
                else:
                    return "Invalid ID and Password"
        # Moved this return statement outside the loop
        return "Invalid User Id And Password"
@app.route("/customerRegistration", methods=['GET', 'POST'])
def customerRegistration():
    if request.method == 'POST':
        SSN = request.form['ssnid']
        first = request.form['first_name']
        last = request.form['last_name']
        age = request.form['age']
        city = request.form['city']
        gender = request.form['gender']
        email = request.form['email']
        user_id = request.form['user_id']
        password = request.form['password']
        balance = 1000.00
        num = random.random()
        num1 = num * 10000
        num2 = int(num1)
        accNo = 11110000 + num2
        
        cur.execute("INSERT INTO User (SSN, first, last, age, city, gender, email, user_id, password, accNo, balance) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (SSN, first, last, age, city, gender, email, user_id, password, accNo, balance))
        
        conn.commit()
        
        return render_template('adminDash.html')  # Redirect to admin dashboard after registration
    
    return render_template("customerRegistration.html")

@app.route("/viewAllCustomers")
def viewAllCustomers():
    cur.execute("SELECT * FROM User")
    customers = cur.fetchall()
    if not customers:
        return "No records found"
    else:
        return render_template("viewAllCustomers.html", customers=customers)

@app.route('/viewRecords', methods=['GET', 'POST'])
def view_records():
    if request.method == 'POST':
        account_number = request.form.get('account_number')  # Use get method to avoid KeyError
        if account_number:
            cur.execute("SELECT * FROM User WHERE accNo = ?", (account_number,))
            details = cur.fetchone()
            if details:
                return render_template('viewRecords.html', details=details)
            else:
                return "No records found for the provided account number."
        else:
            return "Please provide an account number."
    else:
        return render_template('viewRecords.html')  # Render the form page if the request method is GET

@app.route("/deleteAccount", methods=["GET", "POST"])
def delete_account():
    if request.method == "POST":
        account_number = request.form.get("account_number")
        if account_number:
            # Check if the account exists
            cur.execute("SELECT * FROM User WHERE accNo = ?", (account_number,))
            account = cur.fetchone()
            if account:
                # Account found, delete it from the database
                cur.execute("DELETE FROM User WHERE accNo = ?", (account_number,))
                conn.commit()
                return redirect(url_for("account_deleted"))
            else:
                return "No account found with the provided account number."
        else:
            return "Please provide an account number."
    else:
        return render_template("deleteAccount.html")

@app.route("/account_deleted")
def account_deleted():
    return "Account deleted successfully."

@app.route("/updateAccount", methods=["GET", "POST"])
def update_account():
    if request.method == "POST":
        account_number = request.form.get("account_number")
        new_password = request.form.get("new_password")
        if account_number and new_password:
            # Check if account number exists in the database
            cur.execute("SELECT * FROM User WHERE accNo = ?", (account_number,))
            account = cur.fetchone()
            if account:
                # Update password in the database
                cur.execute("UPDATE User SET password = ? WHERE accNo = ?", (new_password, account_number))
                conn.commit()
                return redirect(url_for("password_updated"))
            else:
                return "No account found with the provided account number."
        else:
            return "Please provide an account number and new password."
    else:
        return render_template("updateAccount.html")

@app.route("/password_updated")
def password_updated():
    return "Password updated successfully."

@app.route("/customerLogin", methods=["GET", "POST"])
def customerLogin():
    return render_template('customerLogin.html')

@app.route("/customerDash", methods=["POST"])
def customerDash():
    user_id = request.form["user_id"]
    password = request.form["password"]
    
    # Check if user ID exists in the database and if the password matches
    cur.execute("SELECT * FROM User WHERE user_id = ? AND password = ?", (user_id, password))
    admin = cur.fetchone()
    if admin:
        session["user_id"] = user_id # Store user ID in session
        # return redirect(url_for("customerDash"))
        return render_template('customerDash.html')
    else:
        return "Invalid credentials. Please try again."

@app.route("/self")
def self():
    user_id = session.get("user_id")  # Get the user ID from the session
    if user_id:
        # Retrieve the customer's record from the database based on their user ID
        cur.execute("SELECT * FROM User WHERE user_id = ?", (user_id,))
        record = cur.fetchone()
        if record:
            return render_template("self.html", record=record)
        else:
            return "No record found for the logged-in user."
    else:
        return "User not logged in."

@app.route("/updateCustomer", methods=["GET", "POST"])
def updateCustomer():
    if request.method == "POST":
        user_id = session.get("user_id")  # Retrieve user ID from session
        if user_id:
            first_name = request.form.get("first_name")
            last_name = request.form.get("last_name")
            password = request.form.get("password")
            city = request.form.get("city")
            age = request.form.get("age")
            
            if first_name and last_name and password and city and age:
                conn = sqlite3.connect('Bank_Database.db')
                cur = conn.cursor()
                # Update customer's information in the database
                cur.execute("UPDATE User SET first = ?, last = ?, password = ?, city = ?, age = ? WHERE user_id = ?",
                            (first_name, last_name, password, city, age, user_id))
                conn.commit()
                conn.close()
                return "Information updated successfully."
            else:
                return "Please fill in all fields."
        else:
            return "User not logged in."
    else:
        return render_template("updateCustomer.html")

@app.route("/withdraw", methods=["GET", "POST"])
def withdraw():
    if request.method == "POST":
        user_id = session.get("user_id")  # Retrieve user ID from session
        if user_id:
            amount = float(request.form.get("amount"))
            if amount > 0:  # Check if the withdrawal amount is valid (greater than 0)
                conn = sqlite3.connect('Bank_Database.db')
                cur = conn.cursor()
                # Retrieve the user's record from the database
                cur.execute("SELECT * FROM User WHERE user_id = ?", (user_id,))
                user = cur.fetchone()
                if user:
                    current_balance = user[10]  # Get the current balance from the record
                    if current_balance >= amount:  # Check if the user has sufficient balance
                        new_balance = current_balance - amount  # Calculate new balance after withdrawal
                        if new_balance >= 500:  # Check if the new balance meets the minimum requirement
                            # Update the balance in the database
                            cur.execute("UPDATE User SET balance = ? WHERE user_id = ?", (new_balance, user_id))
                            conn.commit()
                            conn.close()
                            return "Withdrawal successful. Your new balance is: Rs{}".format(new_balance)
                        else:
                            return "Minimum balance requirement not met. You must maintain a balance of at least Rupees 500."
                    else:
                        return "Insufficient balance."
                else:
                    return "User not found in the database."
            else:
                return "Withdrawal amount must be greater than 0."
        else:
            return "User not logged in."
    else:
        return render_template("withdraw.html")

@app.route("/deposit", methods=["GET", "POST"])
def deposit():
    if request.method == "POST":
        user_id = session.get("user_id")  # Retrieve user ID from session
        if user_id:
            amount = float(request.form.get("amount"))
            if amount > 0:  # Check if the deposit amount is valid (greater than 0)
                conn = sqlite3.connect('Bank_Database.db')
                cur = conn.cursor()
                # Retrieve the user's record from the database
                cur.execute("SELECT * FROM User WHERE user_id = ?", (user_id,))
                user = cur.fetchone()
                if user:
                    current_balance = user[10]  # Get the current balance from the record
                    new_balance = current_balance + amount  # Calculate new balance after deposit
                    # Update the balance in the database
                    cur.execute("UPDATE User SET balance = ? WHERE user_id = ?", (new_balance, user_id))
                    conn.commit()
                    conn.close()
                    return "Deposit successful. Your new balance is: Rs{}".format(new_balance)
                else:
                    return "User not found in the database."
            else:
                return "Deposit amount must be greater than 0."
        else:
            return "User not logged in."
    else:
        return render_template("deposit.html")

@app.route("/confirmDelete", methods=["GET", "POST"])
def confirmDelete():
    return render_template("confirmDelete.html")

@app.route("/deleteConfirmed", methods=["Get","POST"])
def deleteConfirmed():
    user_id = session.get("user_id")
    if user_id:
        cur.execute("DELETE FROM User WHERE user_id = ?", (user_id,))
        conn.commit()
        session.pop("user_id")  # Clear the session after account deletion
        return "Your account has been successfully deleted."
    else:
        return "User not logged in."

if __name__ == "__main__":
    app.run(debug=True)