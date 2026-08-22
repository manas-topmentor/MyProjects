import mysql.connector
from mysql.connector import Error
from datetime import date
import math


# ============================================================
# DATABASE CONFIGURATION
# ============================================================

DB_HOST = "localhost"
DB_USER = "root"
DB_PASSWORD = "Jardine@7221"      # Change this to your MySQL password
DB_NAME = "bank_db"

# Late penalty charged per overdue day
LATE_PENALTY_PER_DAY = 50.0


# ============================================================
# DATABASE CONNECTION
# ============================================================

def get_connection(database=None):
    try:
        config = {
            "host": DB_HOST,
            "user": DB_USER,
            "password": DB_PASSWORD
        }

        if database:
            config["database"] = database

        return mysql.connector.connect(**config)

    except Error as e:
        print("Database connection error:", e)
        return None


# ============================================================
# CREATE DATABASE AND TABLES
# ============================================================

def setup_database():

    conn = get_connection()

    if conn is None:
        return False

    try:
        cursor = conn.cursor()

        cursor.execute(
            f"CREATE DATABASE IF NOT EXISTS {DB_NAME}"
        )

        cursor.close()
        conn.close()

        conn = get_connection(DB_NAME)

        if conn is None:
            return False

        cursor = conn.cursor()

        # ----------------------------------------------------
        # ACCOUNTS TABLE
        # ----------------------------------------------------

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS accounts (
                account_no VARCHAR(20) PRIMARY KEY,
                customer_name VARCHAR(100) NOT NULL,
                phone VARCHAR(15) NOT NULL,
                email VARCHAR(100) UNIQUE,
                address VARCHAR(255),
                account_type ENUM('Savings', 'Current') NOT NULL,
                balance DECIMAL(15,2) DEFAULT 0.00,
                status ENUM('ACTIVE', 'CLOSED') DEFAULT 'ACTIVE',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # ----------------------------------------------------
        # TRANSACTIONS TABLE
        # ----------------------------------------------------

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                transaction_id INT AUTO_INCREMENT PRIMARY KEY,
                account_no VARCHAR(20) NOT NULL,
                transaction_type ENUM(
                    'DEPOSIT',
                    'WITHDRAW',
                    'TRANSFER_IN',
                    'TRANSFER_OUT'
                ) NOT NULL,
                amount DECIMAL(15,2) NOT NULL,
                description VARCHAR(255),
                transaction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

                FOREIGN KEY (account_no)
                REFERENCES accounts(account_no)
            )
        """)

        # ----------------------------------------------------
        # LOANS TABLE
        # ----------------------------------------------------

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS loans (
                loan_id INT AUTO_INCREMENT PRIMARY KEY,
                account_no VARCHAR(20) NOT NULL,
                principal DECIMAL(15,2) NOT NULL,
                interest_rate DECIMAL(5,2) NOT NULL,
                tenure_months INT NOT NULL,
                emi DECIMAL(15,2) NOT NULL,
                outstanding_amount DECIMAL(15,2) NOT NULL,
                start_date DATE NOT NULL,
                status ENUM('ACTIVE', 'CLOSED') DEFAULT 'ACTIVE',

                FOREIGN KEY (account_no)
                REFERENCES accounts(account_no)
            )
        """)

        # ----------------------------------------------------
        # LOAN PAYMENTS TABLE
        # ----------------------------------------------------

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS loan_payments (
                payment_id INT AUTO_INCREMENT PRIMARY KEY,
                loan_id INT NOT NULL,
                emi_number INT NOT NULL,
                due_date DATE NOT NULL,
                payment_date DATE NOT NULL,
                emi_amount DECIMAL(15,2) NOT NULL,
                late_days INT DEFAULT 0,
                penalty DECIMAL(15,2) DEFAULT 0.00,
                total_paid DECIMAL(15,2) NOT NULL,

                FOREIGN KEY (loan_id)
                REFERENCES loans(loan_id),

                UNIQUE(loan_id, emi_number)
            )
        """)

        conn.commit()

        cursor.close()
        conn.close()

        return True

    except Error as e:
        print("Error creating database/tables:", e)

        if conn:
            conn.rollback()
            conn.close()

        return False


# ============================================================
# INPUT HELPERS
# ============================================================

def get_amount(message):

    while True:
        try:
            amount = float(input(message))

            if amount <= 0:
                print("Amount must be greater than zero.")
                continue

            return amount

        except ValueError:
            print("Please enter a valid amount.")


def get_integer(message):

    while True:
        try:
            value = int(input(message))
            return value

        except ValueError:
            print("Please enter a valid number.")


# ============================================================
# CHECK ACCOUNT
# ============================================================

def account_exists(account_no):

    conn = get_connection(DB_NAME)

    if conn is None:
        return False

    try:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT account_no
            FROM accounts
            WHERE account_no = %s
        """, (account_no,))

        result = cursor.fetchone()

        cursor.close()
        conn.close()

        return result is not None

    except Error as e:
        print("Error:", e)
        conn.close()
        return False


# ============================================================
# CREATE ACCOUNT
# ============================================================

def create_account():

    print("\n========== CREATE ACCOUNT ==========")

    account_no = input("Enter account number: ").strip()

    if not account_no:
        print("Account number cannot be empty.")
        return

    # Duplicate account prevention
    if account_exists(account_no):
        print("ERROR: Account number already exists.")
        print("Duplicate accounts are not allowed.")
        return

    name = input("Enter customer name: ").strip()
    phone = input("Enter phone number: ").strip()
    email = input("Enter email: ").strip()
    address = input("Enter address: ").strip()

    print("\n1. Savings")
    print("2. Current")

    choice = input("Select account type: ")

    if choice == "1":
        account_type = "Savings"

    elif choice == "2":
        account_type = "Current"

    else:
        print("Invalid account type.")
        return

    initial_deposit = get_amount(
        "Enter initial deposit: "
    )

    conn = get_connection(DB_NAME)

    if conn is None:
        return

    try:

        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO accounts
            (
                account_no,
                customer_name,
                phone,
                email,
                address,
                account_type,
                balance
            )
            VALUES (%s,%s,%s,%s,%s,%s,%s)
        """, (
            account_no,
            name,
            phone,
            email,
            address,
            account_type,
            initial_deposit
        ))

        # Record initial deposit
        cursor.execute("""
            INSERT INTO transactions
            (
                account_no,
                transaction_type,
                amount,
                description
            )
            VALUES (%s, 'DEPOSIT', %s, %s)
        """, (
            account_no,
            initial_deposit,
            "Initial account deposit"
        ))

        conn.commit()

        print("\nAccount created successfully.")
        print("Account Number:", account_no)

    except Error as e:

        conn.rollback()

        if "Duplicate" in str(e):
            print("Duplicate account/email is not allowed.")
        else:
            print("Error:", e)

    finally:
        cursor.close()
        conn.close()


# ============================================================
# DEPOSIT MONEY
# ============================================================

def deposit_money():

    print("\n========== DEPOSIT MONEY ==========")

    account_no = input("Enter account number: ").strip()

    amount = get_amount("Enter deposit amount: ")

    conn = get_connection(DB_NAME)

    if conn is None:
        return

    try:

        cursor = conn.cursor()

        cursor.execute("""
            SELECT balance, status
            FROM accounts
            WHERE account_no = %s
            FOR UPDATE
        """, (account_no,))

        account = cursor.fetchone()

        if account is None:
            print("Account not found.")
            conn.close()
            return

        balance, status = account

        if status == "CLOSED":
            print("Account is closed.")
            conn.close()
            return

        cursor.execute("""
            UPDATE accounts
            SET balance = balance + %s
            WHERE account_no = %s
        """, (amount, account_no))

        cursor.execute("""
            INSERT INTO transactions
            (
                account_no,
                transaction_type,
                amount,
                description
            )
            VALUES (%s, 'DEPOSIT', %s, %s)
        """, (
            account_no,
            amount,
            "Cash deposit"
        ))

        conn.commit()

        print("Deposit successful.")
        print("Amount deposited: ₹", format(amount, ".2f"))

    except Error as e:

        conn.rollback()
        print("Error:", e)

    finally:
        cursor.close()
        conn.close()


# ============================================================
# WITHDRAW MONEY
# ============================================================

def withdraw_money():

    print("\n========== WITHDRAW MONEY ==========")

    account_no = input("Enter account number: ").strip()

    amount = get_amount("Enter withdrawal amount: ")

    conn = get_connection(DB_NAME)

    if conn is None:
        return

    try:

        cursor = conn.cursor()

        cursor.execute("""
            SELECT balance, status
            FROM accounts
            WHERE account_no = %s
            FOR UPDATE
        """, (account_no,))

        account = cursor.fetchone()

        if account is None:
            print("Account not found.")
            conn.close()
            return

        balance, status = account

        if status == "CLOSED":
            print("Account is closed.")
            conn.close()
            return

        if float(balance) < amount:
            print("Insufficient balance.")
            conn.close()
            return

        cursor.execute("""
            UPDATE accounts
            SET balance = balance - %s
            WHERE account_no = %s
        """, (amount, account_no))

        cursor.execute("""
            INSERT INTO transactions
            (
                account_no,
                transaction_type,
                amount,
                description
            )
            VALUES (%s, 'WITHDRAW', %s, %s)
        """, (
            account_no,
            amount,
            "Cash withdrawal"
        ))

        conn.commit()

        print("Withdrawal successful.")
        print("Amount withdrawn: ₹", format(amount, ".2f"))

    except Error as e:

        conn.rollback()
        print("Error:", e)

    finally:
        cursor.close()
        conn.close()


# ============================================================
# BALANCE ENQUIRY
# ============================================================

def balance_enquiry():

    print("\n========== BALANCE ENQUIRY ==========")

    account_no = input("Enter account number: ").strip()

    conn = get_connection(DB_NAME)

    if conn is None:
        return

    try:

        cursor = conn.cursor()

        cursor.execute("""
            SELECT customer_name, balance, status
            FROM accounts
            WHERE account_no = %s
        """, (account_no,))

        result = cursor.fetchone()

        if result is None:
            print("Account not found.")

        else:

            name, balance, status = result

            print("\nCustomer Name :", name)
            print("Account Number:", account_no)
            print("Balance       : ₹", format(float(balance), ".2f"))
            print("Status        :", status)

    except Error as e:
        print("Error:", e)

    finally:
        cursor.close()
        conn.close()


# ============================================================
# TRANSFER MONEY
# ============================================================

def transfer_money():

    print("\n========== TRANSFER MONEY ==========")

    from_account = input(
        "Enter sender account number: "
    ).strip()

    to_account = input(
        "Enter receiver account number: "
    ).strip()

    if from_account == to_account:
        print("Sender and receiver accounts must be different.")
        return

    amount = get_amount("Enter transfer amount: ")

    conn = get_connection(DB_NAME)

    if conn is None:
        return

    try:

        cursor = conn.cursor()

        # Lock both accounts in a consistent order
        accounts = sorted([from_account, to_account])

        for acc in accounts:

            cursor.execute("""
                SELECT account_no, balance, status
                FROM accounts
                WHERE account_no = %s
                FOR UPDATE
            """, (acc,))

            if cursor.fetchone() is None:
                print("One or both accounts do not exist.")
                conn.rollback()
                return

        cursor.execute("""
            SELECT balance, status
            FROM accounts
            WHERE account_no = %s
            FOR UPDATE
        """, (from_account,))

        sender = cursor.fetchone()

        cursor.execute("""
            SELECT status
            FROM accounts
            WHERE account_no = %s
            FOR UPDATE
        """, (to_account,))

        receiver = cursor.fetchone()

        sender_balance, sender_status = sender
        receiver_status = receiver[0]

        if sender_status == "CLOSED":
            print("Sender account is closed.")
            conn.rollback()
            return

        if receiver_status == "CLOSED":
            print("Receiver account is closed.")
            conn.rollback()
            return

        if float(sender_balance) < amount:
            print("Insufficient balance.")
            conn.rollback()
            return

        # Deduct from sender
        cursor.execute("""
            UPDATE accounts
            SET balance = balance - %s
            WHERE account_no = %s
        """, (amount, from_account))

        # Add to receiver
        cursor.execute("""
            UPDATE accounts
            SET balance = balance + %s
            WHERE account_no = %s
        """, (amount, to_account))

        # Sender transaction
        cursor.execute("""
            INSERT INTO transactions
            (
                account_no,
                transaction_type,
                amount,
                description
            )
            VALUES (%s, 'TRANSFER_OUT', %s, %s)
        """, (
            from_account,
            amount,
            f"Transfer to {to_account}"
        ))

        # Receiver transaction
        cursor.execute("""
            INSERT INTO transactions
            (
                account_no,
                transaction_type,
                amount,
                description
            )
            VALUES (%s, 'TRANSFER_IN', %s, %s)
        """, (
            to_account,
            amount,
            f"Transfer from {from_account}"
        ))

        conn.commit()

        print("\nTransfer successful.")
        print("Amount transferred: ₹", format(amount, ".2f"))

    except Error as e:

        conn.rollback()
        print("Transfer failed:", e)

    finally:
        cursor.close()
        conn.close()


# ============================================================
# VIEW ACCOUNT DETAILS
# ============================================================

def view_account_details():

    print("\n========== ACCOUNT DETAILS ==========")

    account_no = input("Enter account number: ").strip()

    conn = get_connection(DB_NAME)

    if conn is None:
        return

    try:

        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                account_no,
                customer_name,
                phone,
                email,
                address,
                account_type,
                balance,
                status,
                created_at
            FROM accounts
            WHERE account_no = %s
        """, (account_no,))

        result = cursor.fetchone()

        if result is None:
            print("Account not found.")
            return

        (
            acc_no,
            name,
            phone,
            email,
            address,
            acc_type,
            balance,
            status,
            created
        ) = result

        print("\n-----------------------------------")
        print("Account Number :", acc_no)
        print("Customer Name  :", name)
        print("Phone          :", phone)
        print("Email          :", email)
        print("Address        :", address)
        print("Account Type   :", acc_type)
        print("Balance        : ₹", format(float(balance), ".2f"))
        print("Status         :", status)
        print("Created On     :", created)
        print("-----------------------------------")

    except Error as e:
        print("Error:", e)

    finally:
        cursor.close()
        conn.close()


# ============================================================
# TRANSACTION HISTORY
# ============================================================

def transaction_history():

    print("\n========== TRANSACTION HISTORY ==========")

    account_no = input("Enter account number: ").strip()

    conn = get_connection(DB_NAME)

    if conn is None:
        return

    try:

        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                transaction_id,
                transaction_type,
                amount,
                description,
                transaction_date
            FROM transactions
            WHERE account_no = %s
            ORDER BY transaction_date DESC
        """, (account_no,))

        results = cursor.fetchall()

        if not results:
            print("No transactions found.")
            return

        print("\n")
        print(
            f"{'ID':<6}"
            f"{'TYPE':<18}"
            f"{'AMOUNT':<15}"
            f"{'DESCRIPTION':<30}"
            f"{'DATE':<22}"
        )

        print("-" * 91)

        for row in results:

            transaction_id, trans_type, amount, description, trans_date = row

            print(
                f"{transaction_id:<6}"
                f"{trans_type:<18}"
                f"₹{float(amount):<14.2f}"
                f"{description:<30}"
                f"{str(trans_date):<22}"
            )

    except Error as e:
        print("Error:", e)

    finally:
        cursor.close()
        conn.close()


# ============================================================
# EMI CALCULATION
# ============================================================

def calculate_emi(principal, annual_rate, months):

    monthly_rate = annual_rate / 12 / 100

    if monthly_rate == 0:
        return principal / months

    emi = (
        principal
        * monthly_rate
        * math.pow(1 + monthly_rate, months)
        /
        (math.pow(1 + monthly_rate, months) - 1)
    )

    return emi


# ============================================================
# CREATE LOAN
# ============================================================

def create_loan():

    print("\n========== CREATE LOAN ==========")

    account_no = input("Enter account number: ").strip()

    conn = get_connection(DB_NAME)

    if conn is None:
        return

    try:

        cursor = conn.cursor()

        cursor.execute("""
            SELECT status
            FROM accounts
            WHERE account_no = %s
        """, (account_no,))

        account = cursor.fetchone()

        if account is None:
            print("Account not found.")
            return

        if account[0] == "CLOSED":
            print("Cannot create loan for a closed account.")
            return

        principal = get_amount(
            "Enter loan amount: "
        )

        interest_rate = get_amount(
            "Enter annual interest rate (%): "
        )

        tenure = get_integer(
            "Enter tenure in months: "
        )

        if tenure <= 0:
            print("Tenure must be greater than zero.")
            return

        emi = calculate_emi(
            principal,
            interest_rate,
            tenure
        )

        cursor.execute("""
            INSERT INTO loans
            (
                account_no,
                principal,
                interest_rate,
                tenure_months,
                emi,
                outstanding_amount,
                start_date
            )
            VALUES (%s,%s,%s,%s,%s,%s,%s)
        """, (
            account_no,
            principal,
            interest_rate,
            tenure,
            emi,
            principal,
            date.today()
        ))

        loan_id = cursor.lastrowid

        conn.commit()

        print("\nLoan created successfully.")
        print("Loan ID          :", loan_id)
        print("Principal        : ₹", format(principal, ".2f"))
        print("Interest Rate    :", interest_rate, "%")
        print("Tenure           :", tenure, "months")
        print("Monthly EMI      : ₹", format(emi, ".2f"))

    except Error as e:

        conn.rollback()
        print("Error:", e)

    finally:
        cursor.close()
        conn.close()


# ============================================================
# RECORD LOAN / EMI PAYMENT
# ============================================================

def record_emi_payment():

    print("\n========== RECORD EMI PAYMENT ==========")

    loan_id = get_integer("Enter Loan ID: ")

    conn = get_connection(DB_NAME)

    if conn is None:
        return

    try:

        cursor = conn.cursor()

        # Get loan details
        cursor.execute("""
            SELECT
                account_no,
                principal,
                emi,
                outstanding_amount,
                start_date,
                tenure_months,
                status
            FROM loans
            WHERE loan_id = %s
            FOR UPDATE
        """, (loan_id,))

        loan = cursor.fetchone()

        if loan is None:
            print("Loan not found.")
            return

        (
            account_no,
            principal,
            emi,
            outstanding,
            start_date,
            tenure,
            status
        ) = loan

        if status == "CLOSED":
            print("This loan is already closed.")
            return

        # Find the next EMI number
        cursor.execute("""
            SELECT
                COALESCE(MAX(emi_number), 0)
            FROM loan_payments
            WHERE loan_id = %s
        """, (loan_id,))

        last_emi = cursor.fetchone()[0]
        emi_number = last_emi + 1

        if emi_number > tenure:
            print("All EMI payments have already been recorded.")
            return

        # Due date = 1 month approximation using 30 days
        # This keeps the system simple for a console project.
        from datetime import timedelta

        due_date = start_date + timedelta(
            days=30 * emi_number
        )

        payment_date = date.today()

        late_days = max(
            0,
            (payment_date - due_date).days
        )

        penalty = late_days * LATE_PENALTY_PER_DAY

        emi_amount = min(
            float(emi),
            float(outstanding)
        )

        total_paid = emi_amount + penalty

        print("\n----------- PAYMENT DETAILS -----------")
        print("EMI Number       :", emi_number)
        print("Due Date         :", due_date)
        print("Payment Date     :", payment_date)
        print("EMI Amount       : ₹", format(emi_amount, ".2f"))
        print("Late Days        :", late_days)
        print("Late Penalty     : ₹", format(penalty, ".2f"))
        print("Total Payment    : ₹", format(total_paid, ".2f"))
        print("---------------------------------------")

        confirm = input(
            "Confirm payment? (Y/N): "
        ).upper()

        if confirm != "Y":
            print("Payment cancelled.")
            conn.rollback()
            return

        # Check bank account balance
        cursor.execute("""
            SELECT balance, status
            FROM accounts
            WHERE account_no = %s
            FOR UPDATE
        """, (account_no,))

        account = cursor.fetchone()

        if account is None:
            print("Linked account not found.")
            conn.rollback()
            return

        balance, account_status = account

        if account_status == "CLOSED":
            print("Linked account is closed.")
            conn.rollback()
            return

        if float(balance) < total_paid:
            print("Insufficient account balance for EMI payment.")
            conn.rollback()
            return

        # Deduct payment from account
        cursor.execute("""
            UPDATE accounts
            SET balance = balance - %s
            WHERE account_no = %s
        """, (
            total_paid,
            account_no
        ))

        # Reduce loan outstanding
        new_outstanding = max(
            0,
            float(outstanding) - emi_amount
        )

        new_status = (
            "CLOSED"
            if new_outstanding <= 0
            else "ACTIVE"
        )

        cursor.execute("""
            UPDATE loans
            SET
                outstanding_amount = %s,
                status = %s
            WHERE loan_id = %s
        """, (
            new_outstanding,
            new_status,
            loan_id
        ))

        # Record EMI payment
        cursor.execute("""
            INSERT INTO loan_payments
            (
                loan_id,
                emi_number,
                due_date,
                payment_date,
                emi_amount,
                late_days,
                penalty,
                total_paid
            )
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
        """, (
            loan_id,
            emi_number,
            due_date,
            payment_date,
            emi_amount,
            late_days,
            penalty,
            total_paid
        ))

        # Record bank transaction
        cursor.execute("""
            INSERT INTO transactions
            (
                account_no,
                transaction_type,
                amount,
                description
            )
            VALUES (%s, 'WITHDRAW', %s, %s)
        """, (
            account_no,
            total_paid,
            f"Loan EMI #{emi_number}, Penalty ₹{penalty:.2f}"
        ))

        conn.commit()

        print("\nEMI payment recorded successfully.")

        if penalty > 0:
            print(
                "Late-payment penalty charged: ₹",
                format(penalty, ".2f")
            )
        else:
            print("No late-payment penalty.")

        print(
            "Remaining loan amount: ₹",
            format(new_outstanding, ".2f")
        )

        if new_status == "CLOSED":
            print("Congratulations! Loan has been fully paid.")

    except Error as e:

        conn.rollback()
        print("Error:", e)

    finally:
        cursor.close()
        conn.close()


# ============================================================
# CLOSE ACCOUNT
# ============================================================

def close_account():

    print("\n========== CLOSE ACCOUNT ==========")

    account_no = input(
        "Enter account number: "
    ).strip()

    conn = get_connection(DB_NAME)

    if conn is None:
        return

    try:

        cursor = conn.cursor()

        cursor.execute("""
            SELECT balance, status
            FROM accounts
            WHERE account_no = %s
            FOR UPDATE
        """, (account_no,))

        account = cursor.fetchone()

        if account is None:
            print("Account not found.")
            return

        balance, status = account

        if status == "CLOSED":
            print("Account is already closed.")
            return

        if float(balance) != 0:
            print(
                "Account cannot be closed because balance is not zero."
            )
            print(
                "Current balance: ₹",
                format(float(balance), ".2f")
            )
            return

        # Check active loans
        cursor.execute("""
            SELECT COUNT(*)
            FROM loans
            WHERE account_no = %s
            AND status = 'ACTIVE'
        """, (account_no,))

        active_loans = cursor.fetchone()[0]

        if active_loans > 0:
            print(
                "Account cannot be closed because there are "
                "active loans."
            )
            return

        cursor.execute("""
            UPDATE accounts
            SET status = 'CLOSED'
            WHERE account_no = %s
        """, (account_no,))

        conn.commit()

        print("Account closed successfully.")

    except Error as e:

        conn.rollback()
        print("Error:", e)

    finally:
        cursor.close()
        conn.close()


# ============================================================
# MAIN MENU
# ============================================================

def main():

    print("\n==============================================")
    print("       BANKING MANAGEMENT SYSTEM")
    print("             PYTHON + MYSQL")
    print("==============================================")

    if not setup_database():

        print("\nUnable to setup database.")
        print("Please check your MySQL username/password.")

        return

    print("\nDatabase connected successfully.")

    while True:

        print("\n==============================================")
        print("                 MAIN MENU")
        print("==============================================")

        print("1.  Create Account")
        print("2.  Deposit Money")
        print("3.  Withdraw Money")
        print("4.  Balance Enquiry")
        print("5.  Transfer Money")
        print("6.  View Account Details")
        print("7.  Transaction History")
        print("8.  Create Loan")
        print("9.  Record Loan / EMI Payment")
        print("10. Close Account")
        print("11. Exit")

        choice = input(
            "\nEnter your choice: "
        ).strip()

        if choice == "1":
            create_account()

        elif choice == "2":
            deposit_money()

        elif choice == "3":
            withdraw_money()

        elif choice == "4":
            balance_enquiry()

        elif choice == "5":
            transfer_money()

        elif choice == "6":
            view_account_details()

        elif choice == "7":
            transaction_history()

        elif choice == "8":
            create_loan()

        elif choice == "9":
            record_emi_payment()

        elif choice == "10":
            close_account()

        elif choice == "11":

            print("\nThank you for using Banking Management System.")
            break

        else:
            print("Invalid choice. Please try again.")


# ============================================================
# PROGRAM START
# ============================================================

if __name__ == "__main__":
    main()