import json
from datetime import datetime, date
import os

# ============================================================
# LIBRARY MANAGEMENT SYSTEM
# File I/O using JSON
# ============================================================

BOOK_FILE = "books.json"
MEMBER_FILE = "members.json"
ISSUE_FILE = "issues.json"

FINE_PER_DAY = 5


# ============================================================
# FILE HANDLING FUNCTIONS
# ============================================================

def load_data(filename):
    """Load data from a JSON file."""
    try:
        if not os.path.exists(filename):
            return []

        with open(filename, "r") as file:
            data = json.load(file)

        return data

    except json.JSONDecodeError:
        print(f"Error: {filename} contains invalid JSON data.")
        return []

    except Exception as e:
        print("Error while reading file:", e)
        return []


def save_data(filename, data):
    """Save data to a JSON file."""
    try:
        with open(filename, "w") as file:
            json.dump(data, file, indent=4)

    except Exception as e:
        print("Error while saving data:", e)


# ============================================================
# LOAD DATA
# ============================================================

books = load_data(BOOK_FILE)
members = load_data(MEMBER_FILE)
issues = load_data(ISSUE_FILE)


# ============================================================
# ADD BOOK
# ============================================================

def add_book():
    print("\n========== ADD BOOK ==========")

    book_id = input("Enter Book ID: ").strip()

    # PRIMARY KEY VALIDATION
    # Book ID must be unique
    for book in books:
        if book["book_id"] == book_id:
            print("Error: Book ID already exists!")
            print("Duplicate Book IDs are not allowed.")
            return

    title = input("Enter Book Title: ").strip()
    author = input("Enter Author Name: ").strip()

    if not book_id or not title or not author:
        print("Book ID, Title and Author cannot be empty.")
        return

    book = {
        "book_id": book_id,
        "title": title,
        "author": author,
        "status": "Available"
    }

    books.append(book)
    save_data(BOOK_FILE, books)

    print("Book added successfully!")


# ============================================================
# REGISTER MEMBER
# ============================================================

def register_member():
    print("\n========== REGISTER MEMBER ==========")

    member_id = input("Enter Member ID: ").strip()

    # Prevent duplicate Member ID
    for member in members:
        if member["member_id"] == member_id:
            print("Error: Member ID already exists!")
            return

    name = input("Enter Member Name: ").strip()
    phone = input("Enter Phone Number: ").strip()

    if not member_id or not name or not phone:
        print("Member ID, Name and Phone cannot be empty.")
        return

    member = {
        "member_id": member_id,
        "name": name,
        "phone": phone
    }

    members.append(member)
    save_data(MEMBER_FILE, members)

    print("Member registered successfully!")


# ============================================================
# ISSUE BOOK
# ============================================================

def issue_book():
    print("\n========== ISSUE BOOK ==========")

    book_id = input("Enter Book ID: ").strip()
    member_id = input("Enter Member ID: ").strip()

    # Check whether book exists
    book = None

    for b in books:
        if b["book_id"] == book_id:
            book = b
            break

    if book is None:
        print("Book not found!")
        return

    # Check book availability
    if book["status"] != "Available":
        print("Book is already issued!")
        return

    # Check whether member exists
    member = None

    for m in members:
        if m["member_id"] == member_id:
            member = m
            break

    if member is None:
        print("Member not found!")
        return

    # Enter due date
    due_date = input(
        "Enter Due Date (YYYY-MM-DD): "
    ).strip()

    try:
        due = datetime.strptime(due_date, "%Y-%m-%d").date()

        if due <= date.today():
            print("Due date must be a future date.")
            return

    except ValueError:
        print("Invalid date format!")
        print("Please use YYYY-MM-DD.")
        return

    # Create issue record
    issue = {
        "book_id": book_id,
        "member_id": member_id,
        "issue_date": str(date.today()),
        "due_date": due_date
    }

    issues.append(issue)

    # Change book status
    book["status"] = "Issued"

    save_data(BOOK_FILE, books)
    save_data(ISSUE_FILE, issues)

    print("Book issued successfully!")
    print("Issue Date:", date.today())
    print("Due Date:", due_date)


# ============================================================
# RETURN BOOK
# ============================================================

def return_book():
    print("\n========== RETURN BOOK ==========")

    book_id = input("Enter Book ID: ").strip()

    # Find issue record
    issue_record = None

    for issue in issues:
        if issue["book_id"] == book_id:
            issue_record = issue
            break

    if issue_record is None:
        print("This book is not currently issued.")
        return

    try:
        due_date = datetime.strptime(
            issue_record["due_date"],
            "%Y-%m-%d"
        ).date()

        return_date = date.today()

        # Calculate late days
        late_days = (return_date - due_date).days

        if late_days > 0:
            fine = late_days * FINE_PER_DAY
        else:
            late_days = 0
            fine = 0

    except ValueError:
        print("Invalid due date stored in JSON.")
        return

    # Update book status
    for book in books:
        if book["book_id"] == book_id:
            book["status"] = "Available"
            break

    # Remove issue record
    issues.remove(issue_record)

    save_data(BOOK_FILE, books)
    save_data(ISSUE_FILE, issues)

    print("\nBook returned successfully!")
    print("Return Date:", return_date)
    print("Due Date:", due_date)
    print("Late Days:", late_days)
    print("Fine: ₹", fine)


# ============================================================
# VIEW AVAILABLE BOOKS
# ============================================================

def view_available_books():
    print("\n========== AVAILABLE BOOKS ==========")

    found = False

    for book in books:
        if book["status"] == "Available":
            found = True

            print("--------------------------------")
            print("Book ID :", book["book_id"])
            print("Title   :", book["title"])
            print("Author  :", book["author"])
            print("Status  :", book["status"])

    if not found:
        print("No books are currently available.")


# ============================================================
# VIEW ISSUED BOOKS
# ============================================================

def view_issued_books():
    print("\n========== ISSUED BOOKS ==========")

    if not issues:
        print("No books are currently issued.")
        return

    for issue in issues:

        # Find book title
        title = "Unknown"

        for book in books:
            if book["book_id"] == issue["book_id"]:
                title = book["title"]
                break

        # Find member name
        member_name = "Unknown"

        for member in members:
            if member["member_id"] == issue["member_id"]:
                member_name = member["name"]
                break

        print("--------------------------------")
        print("Book ID     :", issue["book_id"])
        print("Book Title  :", title)
        print("Member ID   :", issue["member_id"])
        print("Member Name :", member_name)
        print("Issue Date  :", issue["issue_date"])
        print("Due Date    :", issue["due_date"])


# ============================================================
# VIEW MEMBERS
# ============================================================

def view_members():
    print("\n========== LIBRARY MEMBERS ==========")

    if not members:
        print("No members registered.")
        return

    for member in members:
        print("--------------------------------")
        print("Member ID :", member["member_id"])
        print("Name      :", member["name"])
        print("Phone     :", member["phone"])


# ============================================================
# VIEW ALL BOOKS
# ============================================================

def view_all_books():
    print("\n========== ALL BOOKS ==========")

    if not books:
        print("No books found.")
        return

    for book in books:
        print("--------------------------------")
        print("Book ID :", book["book_id"])
        print("Title   :", book["title"])
        print("Author  :", book["author"])
        print("Status  :", book["status"])


# ============================================================
# MAIN MENU
# ============================================================

def main():

    while True:

        print("\n")
        print("==============================================")
        print("       LIBRARY MANAGEMENT SYSTEM")
        print("       Python + JSON File I/O")
        print("==============================================")
        print("1. Add Book")
        print("2. Register Member")
        print("3. Issue Book")
        print("4. Return Book")
        print("5. View Available Books")
        print("6. View Issued Books")
        print("7. View Members")
        print("8. View All Books")
        print("9. Exit")
        print("==============================================")

        choice = input("Enter your choice: ").strip()

        if choice == "1":
            add_book()

        elif choice == "2":
            register_member()

        elif choice == "3":
            issue_book()

        elif choice == "4":
            return_book()

        elif choice == "5":
            view_available_books()

        elif choice == "6":
            view_issued_books()

        elif choice == "7":
            view_members()

        elif choice == "8":
            view_all_books()

        elif choice == "9":
            print("\nThank you for using Library Management System!")
            break

        else:
            print("Invalid choice! Please select 1-9.")


# ============================================================
# PROGRAM START
# ============================================================

if __name__ == "__main__":
    main()

