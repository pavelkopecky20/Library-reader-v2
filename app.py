from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename
import os
from PIL import Image
from models import db, Book
from forms import BookForm

from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

from get_text import detect_text_from_file, get_books_and_authors

app = Flask(__name__)
app.config.from_object("config")

db.init_app(app)
migrate = Migrate(app, db)

# Vytvoření databázových tabulek - dělá se migrací, není třeba

UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER     # nahrávání obrázků
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/", methods=["GET", "POST"])
def index():
    print("Vše - index.html se spustilo v pořádku.")
    if request.method == "POST":
        file = request.files["image"]
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(filepath)
        
        text = detect_text_from_file(filepath)  # získáme text, zavolá se AI API na detekci textu z obrázku

        books = get_books_and_authors(text)     # zavolá se OpenAI na rozpoznání autora a názvu z textu 
        # print(books)
        
        # # Uložení do db - funguje
        if books:
            for item in books:
                title = item.get('title') or "Bez názvu"
                author = item.get('author') or "Neznámý" 
                book = Book(title=title, author=author)
                db.session.add(book)
                db.session.commit()
            print("✅ Data byla úspěšně uložena do databáze.")
            return redirect(url_for("books"))   
    return render_template("index.html")

@app.route("/books")
def books():
    books = Book.query.all()
    return render_template("books.html", books=books)

# filepath: c:\Users\m000xz009726\OneDrive\Programování\Library_reader\library_reader\app.py


@app.route("/edit_books", methods=["GET", "POST"])
def edit_books():
    print("Debug: Edit Books route accessed")
    form = BookForm()  # 
    books = Book.query.all()  # 

    if request.method == "POST":
        for book in books:
            title = request.form.get(f"title_{book.id}")
            author = request.form.get(f"author_{book.id}")
            is_read = request.form.get(f"is_read_{book.id}") == 'on'
            rating = request.form.get(f"rating_{book.id}")
            abstract = request.form.get(f"abstract_{book.id}")
            comment = request.form.get(f"comment_{book.id}")

            # 
            if rating:
                try:
                    rating = int(rating)
                    if 1 <= rating <= 10:
                        book.rating = rating
                    else:
                        raise ValueError("Rating must be between 1 and 10.")
                except ValueError:
                    print(f"Invalid rating for book {book.id}: {rating}")
                    continue  #
                
            # 
            book.title = title if title else book.title
            book.author = author if author else book.author
            book.is_read = is_read
            book.abstract = abstract if abstract else book.abstract
            book.comment = comment if comment else book.comment

        db.session.commit()  # uloží do db
        return redirect(url_for("books"))  # 

    return render_template("edit_books.html", books=books, form=form)
if __name__ == "__main__":
    app.run(debug=True)

