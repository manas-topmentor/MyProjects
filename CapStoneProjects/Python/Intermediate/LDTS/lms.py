from datetime import datetime, timedelta

# ============================================================
# LIBRARY MANAGEMENT SYSTEM
# ============================================================

# Dictionary to store books
# book_id -> book details
books = {}

# Dictionary to store members
# member_id -> member details
members = {}

# Dictionary to store issued books
# book_id -> issue details
issued_books = {}

# List to maintain book IDs
book_id_list = []

# List to maintain member IDs
member_id_list = []

# Fine charged per late day
FINE_PER_DAY = 5


# ============================================================
# 1. ADD BOOK
# ============================================================

def add_book():
    print("\n========== ADD BOOK ==========")

    book_id = input("Enter Book ID: ").strip()

    # Prevent duplicate Book IDs
    if book_id in books:
        print("Error: Book ID already exists!")
        return

    title = input("Enter Book Title: ").strip()
    author = input("Enter Author Name: ").strip()

    if title == "" or author == "":
        print("Book title and author cannot be empty.")
        return

    # Tuple used for storing book information
    book_info = (title, author, "Available")

    books[book_id] = book_info
    book_id_list.append(book_id)

    print("Book added successfully!")


# ============================================================
# 2. REGISTER MEMBER
# ============================================================

def register_member():
    print("\n========== REGISTER MEMBER ==========")

    member_id = input("Enter Member ID: ").strip()

    if member_id in members:
        print("Error: Member ID already exists!")
        return

    name = input("Enter Member Name: ").strip()
    phone = input("Enter Phone Number: ").strip()

    if name == "":
        print("Member name cannot be empty.")
        return

    # Tuple used for member information
    member_info = (name, phone)

    members[member_id] = member_info
    member_id_list.append(member_id)

    print("Member registered successfully!")


# ============================================================
# 3. ISSUE BOOK
# ============================================================

def issue_book():
    print("\n========== ISSUE BOOK ==========")

    if len(books) == 0:
        print("No books are available in the library.")
        return

    book_id = input("Enter Book ID: ").strip()

    if book_id not in books:
        print("Error: Book ID does not exist!")
        return

    # Check whether book is already issued
    if book_id in issued_books:
        print("Error: This book is already issued.")
        return

    member_id = input("Enter Member ID: ").strip()

    if member_id not in members:
        print("Error: Member does not exist!")
        return

    # Set issue date
    issue_date = datetime.now().date()

    # Due date = 14 days from issue date
    due_date = issue_date + timedelta(days=14)

    # Store issue information in dictionary
    issued_books[book_id] = {
        "member_id": member_id,
        "issue_date": issue_date,
        "due_date": due_date
    }

    # Update book status
    title, author, status = books[book_id]

    books[book_id] = (title, author, "Issued")

    print("\nBook issued successfully!")
    print("Book ID   :", book_id)
    print("Member ID :", member_id)
    print("Issue Date:", issue_date)
    print("Due Date  :", due_date)


# ============================================================
# 4. RETURN BOOK
# ============================================================

def return_book():
    print("\n========== RETURN BOOK ==========")

    book_id = input("Enter Book ID: ").strip()

    if book_id not in books:
        print("Error: Book ID does not exist!")
        return

    if book_id not in issued_books:
        print("Error: This book is not currently issued.")
        return

    # Get issue information
    issue_details = issued_books[book_id]

    due_date = issue_details["due_date"]
    return_date = datetime.now().date()

    # Calculate late days
    late_days = (return_date - due_date).days

    if late_days > 0:
        fine = late_days * FINE_PER_DAY
    else:
        late_days = 0
        fine = 0

    # Update book status
    title, author, status = books[book_id]

    books[book_id] = (title, author, "Available")

    # Remove book from issued books
    del issued_books[book_id]

    print("\n========== RETURN DETAILS ==========")
    print("Book ID    :", book_id)
    print("Return Date:", return_date)
    print("Due Date   :", due_date)
    print("Late Days  :", late_days)
    print("Fine       : Rs.", fine)

    if fine > 0:
        print("The book was returned late.")
    else:
        print("Book returned on time.")

    print("Book returned successfully!")


# ============================================================
# 5. VIEW AVAILABLE BOOKS
# ============================================================

def view_available_books():
    print("\n========== AVAILABLE BOOKS ==========")

    found = False

    for book_id, book_info in books.items():

        title, author, status = book_info

        if status == "Available":
            found = True

            print("--------------------------------")
            print("Book ID :", book_id)
            print("Title   :", title)
            print("Author  :", author)
            print("Status  :", status)

    if not found:
        print("No books are currently available.")


# ============================================================
# 6. VIEW ISSUED BOOKS
# ============================================================

def view_issued_books():
    print("\n========== ISSUED BOOKS ==========")

    if len(issued_books) == 0:
        print("No books are currently issued.")
        return

    for book_id, details in issued_books.items():

        title, author, status = books[book_id]

        print("--------------------------------")
        print("Book ID    :", book_id)
        print("Title      :", title)
        print("Author     :", author)
        print("Member ID  :", details["member_id"])
        print("Issue Date :", details["issue_date"])
        print("Due Date   :", details["due_date"])


# ============================================================
# 7. VIEW MEMBERS
# ============================================================

def view_members():
    print("\n========== MEMBERS ==========")

    if len(members) == 0:
        print("No members registered.")
        return

    for member_id, member_info in members.items():

        name, phone = member_info

        print("--------------------------------")
        print("Member ID :", member_id)
        print("Name      :", name)
        print("Phone     :", phone)


# ============================================================
# 8. VIEW ALL BOOKS
# ============================================================

def view_all_books():
    print("\n========== ALL BOOKS ==========")

    if len(books) == 0:
        print("No books found.")
        return

    for book_id, book_info in books.items():

        title, author, status = book_info

        print("--------------------------------")
        print("Book ID :", book_id)
        print("Title   :", title)
        print("Author  :", author)
        print("Status  :", status)


# ============================================================
# 9. MAIN MENU
# ============================================================

def main():

    while True:

        print("\n")
        print("==========================================")
        print("       LIBRARY MANAGEMENT SYSTEM")
        print("==========================================")
        print("1. Add Book")
        print("2. Register Member")
        print("3. Issue Book")
        print("4. Return Book")
        print("5. View Available Books")
        print("6. View Issued Books")
        print("7. View Members")
        print("8. View All Books")
        print("9. Exit")
        print("==========================================")

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
            print("\nThank you for using the Library Management System!")
            break

        else:
            print("Invalid choice! Please enter a number from 1 to 9.")


# ============================================================
# PROGRAM START
# ============================================================


