import mysql.connector
from datetime import date, timedelta


# ---------------- DATABASE CONNECTION ----------------

def connect_database():
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="Jardine@7221",
            database="library_db"
        )

        return connection

    except mysql.connector.Error as error:
        print("Database connection error:", error)
        return None


# ---------------- ADD BOOK ----------------

def add_book():
    connection = connect_database()

    if connection is None:
        return

    cursor = connection.cursor()

    try:
        book_id = int(input("Enter Book ID: "))
        title = input("Enter Book Title: ")
        author = input("Enter Author Name: ")
        quantity = int(input("Enter Quantity: "))

        # Check duplicate Book ID
        cursor.execute(
            "SELECT book_id FROM books WHERE book_id = %s",
            (book_id,)
        )

        if cursor.fetchone():
            print("Error: Book ID already exists!")
            return

        query = """
        INSERT INTO books
        (book_id, title, author, quantity, available_quantity)
        VALUES (%s, %s, %s, %s, %s)
        """

        cursor.execute(
            query,
            (book_id, title, author, quantity, quantity)
        )

        connection.commit()

        print("Book added successfully.")

    except ValueError:
        print("Please enter valid numeric values.")

    except mysql.connector.Error as error:
        print("Error:", error)

    finally:
        cursor.close()
        connection.close()


# ---------------- ADD MEMBER ----------------

def add_member():
    connection = connect_database()

    if connection is None:
        return

    cursor = connection.cursor()

    try:
        member_id = int(input("Enter Member ID: "))
        name = input("Enter Member Name: ")
        phone = input("Enter Phone Number: ")

        cursor.execute(
            "SELECT member_id FROM members WHERE member_id = %s",
            (member_id,)
        )

        if cursor.fetchone():
            print("Error: Member ID already exists!")
            return

        query = """
        INSERT INTO members
        (member_id, name, phone)
        VALUES (%s, %s, %s)
        """

        cursor.execute(query, (member_id, name, phone))

        connection.commit()

        print("Member added successfully.")

    except ValueError:
        print("Please enter a valid Member ID.")

    except mysql.connector.Error as error:
        print("Error:", error)

    finally:
        cursor.close()
        connection.close()


# ---------------- ISSUE BOOK ----------------

def issue_book():
    connection = connect_database()

    if connection is None:
        return

    cursor = connection.cursor()

    try:
        book_id = int(input("Enter Book ID: "))
        member_id = int(input("Enter Member ID: "))

        # Check book
        cursor.execute(
            "SELECT title, available_quantity FROM books WHERE book_id = %s",
            (book_id,)
        )

        book = cursor.fetchone()

        if book is None:
            print("Book not found.")
            return

        title, available_quantity = book

        if available_quantity <= 0:
            print("Book is currently unavailable.")
            return

        # Check member
        cursor.execute(
            "SELECT name FROM members WHERE member_id = %s",
            (member_id,)
        )

        member = cursor.fetchone()

        if member is None:
            print("Member not found.")
            return

        issue_date = date.today()

        # Book is due after 14 days
        due_date = issue_date + timedelta(days=14)

        query = """
        INSERT INTO issued_books
        (book_id, member_id, issue_date, due_date)
        VALUES (%s, %s, %s, %s)
        """

        cursor.execute(
            query,
            (book_id, member_id, issue_date, due_date)
        )

        # Decrease available quantity
        cursor.execute(
            """
            UPDATE books
            SET available_quantity = available_quantity - 1
            WHERE book_id = %s
            """,
            (book_id,)
        )

        connection.commit()

        print("\nBook issued successfully.")
        print("Book:", title)
        print("Issue Date:", issue_date)
        print("Due Date:", due_date)

    except ValueError:
        print("Please enter valid numeric values.")

    except mysql.connector.Error as error:
        print("Error:", error)

    finally:
        cursor.close()
        connection.close()


# ---------------- RETURN BOOK ----------------

def return_book():
    connection = connect_database()

    if connection is None:
        return

    cursor = connection.cursor()

    try:
        issue_id = int(input("Enter Issue ID: "))

        # Find issued book
        query = """
        SELECT book_id, due_date, return_date
        FROM issued_books
        WHERE issue_id = %s
        """

        cursor.execute(query, (issue_id,))

        record = cursor.fetchone()

        if record is None:
            print("Issue record not found.")
            return

        book_id, due_date, return_date = record

        if return_date is not None:
            print("This book has already been returned.")
            return

        return_date = date.today()

        # Calculate late days
        late_days = (return_date - due_date).days

        # Fine = ₹10 per late day
        fine_per_day = 10

        if late_days > 0:
            fine = late_days * fine_per_day
        else:
            fine = 0

        # Update issue record
        query = """
        UPDATE issued_books
        SET return_date = %s,
            fine = %s
        WHERE issue_id = %s
        """

        cursor.execute(
            query,
            (return_date, fine, issue_id)
        )

        # Increase available quantity
        cursor.execute(
            """
            UPDATE books
            SET available_quantity = available_quantity + 1
            WHERE book_id = %s
            """,
            (book_id,)
        )

        connection.commit()

        print("\nBook returned successfully.")
        print("Return Date:", return_date)

        if late_days > 0:
            print("Late by:", late_days, "days")
            print("Fine: ₹", fine)
        else:
            print("Returned on time.")
            print("Fine: ₹0")

    except ValueError:
        print("Please enter a valid Issue ID.")

    except mysql.connector.Error as error:
        print("Error:", error)

    finally:
        cursor.close()
        connection.close()


# ---------------- VIEW BOOKS ----------------

def view_books():
    connection = connect_database()

    if connection is None:
        return

    cursor = connection.cursor()

    cursor.execute("""
        SELECT book_id, title, author,
               quantity, available_quantity
        FROM books
        ORDER BY book_id
    """)

    books = cursor.fetchall()

    print("\n----------- BOOK LIST -----------")

    if not books:
        print("No books found.")
    else:
        for book in books:
            print(
                "ID:", book[0],
                "| Title:", book[1],
                "| Author:", book[2],
                "| Total:", book[3],
                "| Available:", book[4]
            )

    cursor.close()
    connection.close()


# ---------------- VIEW MEMBERS ----------------

def view_members():
    connection = connect_database()

    if connection is None:
        return

    cursor = connection.cursor()

    cursor.execute("""
        SELECT member_id, name, phone
        FROM members
        ORDER BY member_id
    """)

    members = cursor.fetchall()

    print("\n----------- MEMBER LIST -----------")

    if not members:
        print("No members found.")
    else:
        for member in members:
            print(
                "ID:", member[0],
                "| Name:", member[1],
                "| Phone:", member[2]
            )

    cursor.close()
    connection.close()


# ---------------- VIEW ISSUED BOOKS ----------------

def view_issued_books():
    connection = connect_database()

    if connection is None:
        return

    cursor = connection.cursor()

    query = """
    SELECT
        i.issue_id,
        b.title,
        m.name,
        i.issue_date,
        i.due_date,
        i.return_date,
        i.fine
    FROM issued_books i
    JOIN books b
        ON i.book_id = b.book_id
    JOIN members m
        ON i.member_id = m.member_id
    ORDER BY i.issue_id
    """

    cursor.execute(query)

    records = cursor.fetchall()

    print("\n----------- ISSUE RECORDS -----------")

    if not records:
        print("No issue records found.")
    else:
        for record in records:
            print("\nIssue ID:", record[0])
            print("Book:", record[1])
            print("Member:", record[2])
            print("Issue Date:", record[3])
            print("Due Date:", record[4])
            print("Return Date:", record[5])
            print("Fine: ₹", record[6])

    cursor.close()
    connection.close()


# ---------------- MAIN MENU ----------------

def main():

    while True:

        print("\n===================================")
        print("       LIBRARY MANAGEMENT SYSTEM")
        print("===================================")

        print("1. Add Book")
        print("2. Add Member")
        print("3. Issue Book")
        print("4. Return Book")
        print("5. View Books")
        print("6. View Members")
        print("7. View Issued Books")
        print("8. Exit")

        choice = input("\nEnter your choice: ")

        if choice == "1":
            add_book()

        elif choice == "2":
            add_member()

        elif choice == "3":
            issue_book()

        elif choice == "4":
            return_book()

        elif choice == "5":
            view_books()

        elif choice == "6":
            view_members()

        elif choice == "7":
            view_issued_books()

        elif choice == "8":
            print("Thank you for using the Library Management System.")
            break

        else:
            print("Invalid choice. Please try again.")


# Start program
main()