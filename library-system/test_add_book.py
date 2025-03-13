from models.books import add_book
from app import app  # Import the Flask app

def test_add_book():
    with app.app_context():  # Set up application context
        title = "PIMP1"  # Book title
        author = "Test uur"
        genre = "Fiction"
        isbn = "1333379999"
        copies = 1
        generate_barcode = True  # Set to True to test barcode generation

        result = add_book(title, author, genre, isbn, copies, generate_barcode)  # Call the add_book function

        if result:
            print("Book added successfully!")
        else:
            print("Failed to add book.")

if __name__ == "__main__":
    test_add_book()
