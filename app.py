from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename
import os
from PIL import Image
from models import db, Book
from forms import BookForm

from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate, upgrade

from get_text import detect_text_from_file, get_books_and_authors
import base64

app = Flask(__name__)
app.config.from_object("config")

db.init_app(app)
migrate = Migrate(app, db)

import os
import base64

# Decode the Base64 string - uloží to jako soubor
credentials_base64 = os.getenv("GOOGLE_APPLICATION_CREDENTIALS_BASE64")
if credentials_base64:
    try:
        credentials_path = "/tmp/vision-key.json"  # Temporary path for the file
        with open(credentials_path, "wb") as f:
            f.write(base64.b64decode(credentials_base64))
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_path
        print(f"✅ Credentials file created at: {credentials_path}")
    except Exception as e:
        print(f"❌ Error decoding Base64 credentials: {e}")
else:
    print("❌ GOOGLE_APPLICATION_CREDENTIALS_BASE64 is not set.")

if not os.path.exists("/tmp/library_reader.db"):
    with open("/tmp/library_reader.db", "w"):
        pass

# Vytvoření databázových tabulek - dělá se migrací, není třeba

UPLOAD_FOLDER = "/tmp/uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

if not os.path.exists(UPLOAD_FOLDER):
    print(f"❌ Upload folder not created: {UPLOAD_FOLDER}")
else:
    print(f"✅ Upload folder exists: {UPLOAD_FOLDER}")

from flask_migrate import upgrade

@app.before_first_request       # pro db - migrace 
def apply_migrations():
    try:
        print("🔄 Applying database migrations...")
        upgrade()
        print("✅ Migrations applied successfully.")
    except Exception as e:
        print(f"❌ Error applying migrations: {e}")


@app.route("/", methods=["GET", "POST"])
def index():
    print("✅ Route '/' accessed.")
    if request.method == "POST":
        print("✅ POST request received.")
        file = request.files.get("image")
        if not file:
            print("❌ No file uploaded.")
            return render_template("index.html", error="Nenahráli jste soubor s obrázky knih.")
        
        filename = secure_filename(file.filename)
        if not filename:
            print("❌ Invalid file name.")
            return render_template("index.html", error="Nahraný soubor nemá platný název.")
        
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        try:
            file.save(filepath)
            print(f"✅ File successfully saved: {filepath}")
        except Exception as e:
            print(f"❌ Error saving file: {e}")
            return render_template("index.html", error="Chyba při ukládání souboru.")
        
        # Process the file
        print("✅ File processing started.")
        try:
            text = detect_text_from_file(filepath)
            print(f"✅ Text detected: {text}")
        except Exception as e:
            print(f"❌ Error detecting text: {e}")
            return render_template("index.html", error="Chyba při zpracování obrázku.")
        
        try:
            books = get_books_and_authors(text)
            print(f"✅ Books detected: {books}")
        except Exception as e:
            print(f"❌ Error detecting books: {e}")
            return render_template("index.html", error="Chyba při rozpoznávání knih.")
        
        if not books:
            print("❌ No books detected.")
            return render_template("index.html", error="Nebyly rozpoznány žádné knihy.")
        
        # Save to database
        try:
            for item in books:
                title = item.get('title') or "Bez názvu"
                author = item.get('author') or "Neznámý"
                book = Book(title=title, author=author)
                db.session.add(book)
            db.session.commit()
            print("✅ Data successfully saved to the database.")
        except Exception as e:
            print(f"❌ Error saving to database: {e}")
            db.session.rollback()
            return render_template("index.html", error="Chyba při ukládání do databáze.")
        
        return redirect(url_for("books"))
    return render_template("index.html")

@app.route("/books")
def books():
    try:
        books = Book.query.all()
        return render_template("books.html", books=books)
    except Exception as e:
        print(f"❌ Chyba při načítání knih: {e}")
        return render_template("books.html", error="Chyba při načítání knih.")

# filepath: c:\Users\m000xz009726\OneDrive\Programování\Library_reader\library_reader\app.py

@app.route("/edit_books", methods=["GET", "POST"])
def edit_books():
    print("Debug: Edit Books route accessed")
    form = BookForm()  #
    try: 
        books = Book.query.all()  # 
    except Exception as e:
        print(f"❌ Chyba při načítání knih: {e}")
        return render_template("edit_books.html", error="Chyba při načítání knih.")

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
        try:
            db.session.commit()  # uloží do db
            print("✅ Knihy byly úspěšně aktualizovány do db.")          
        except Exception as e:
            print(f"❌ Chyba při aktualizaci knih do db: {e}")
            db.session.rollback()
            return render_template("edit_books.html", error="Chyba při aktualizaci knih do databáze.")

        return redirect(url_for("books"))  # 

    return render_template("edit_books.html", books=books, form=form)
if __name__ == "__main__":
    app.run(debug=True)

