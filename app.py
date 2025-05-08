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
    credentials_path = "/tmp/vision-key.json"  # Temporary path for the file
    with open(credentials_path, "wb") as f:
        f.write(base64.b64decode(credentials_base64))
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_path

# Vytvoření databázových tabulek - dělá se migrací, není třeba

UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER     # nahrávání obrázků
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

if not os.path.exists(UPLOAD_FOLDER):
    print(f"❌ Upload folder not created: {UPLOAD_FOLDER}")
else:
    print(f"✅ Upload folder exists: {UPLOAD_FOLDER}")

@app.route("/", methods=["GET", "POST"])
def index():
    print("Vše - index.html se spustilo v pořádku.  Route '/' accessed.")
    if request.method == "POST":
        print("✅ POST request received.")
        file = request.files.get("image")
        if not file:
            print("❌ Nenahráli jste soubor s obrázky knih.")
            return render_template("index.html", error="Nenahráli jste soubor s obrázky knih.")
       
        filename = secure_filename(file.filename)
        if not filename:
            print("❌ Chyba: Nahraný soubor nemá platný název.")
            return render_template("index.html", error="Nahraný soubor nemá platný název.")
   
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        try:
            file.save(filepath)
            print(f"✅ Soubor byl úspěšně uložen: {filepath}")
        except Exception as e:
            print(f"❌ Chyba při ukládání souboru: {e}")
            return render_template("index.html", error="Chyba při ukládání souboru.")

        
        text = detect_text_from_file(filepath)  # získáme text, zavolá se AI API na detekci textu z obrázku
        if "Error" in text:
            return render_template("index.html", error=text)  # pokud je chyba, vrátí se na index.html

        books = get_books_and_authors(text)     # zavolá se OpenAI na rozpoznání autora a názvu z textu
        if not books:
            return render_template("index.html", error="Nebyly rozpoznány žádné knihy.") 
        # print(books)
        
        # # Uložení do db - funguje
        try:
            for item in books:
                title = item.get('title') or "Bez názvu"
                author = item.get('author') or "Neznámý" 
                book = Book(title=title, author=author)
                db.session.add(book)
            db.session.commit()
            print("✅ Data byla úspěšně uložena do databáze.")
        except Exception as e:
            print(f"❌ Chyba při ukládání do databáze: {e}")
            db.session.rollback()  # vrátí poslední změny v db
            return render_template("index.html", error="Chyba při ukládání do databáze.")
        return redirect(url_for("books"))  # přesměrování na knihy
    return render_template("index.html")  # pokud je GET, vrátí se na index.html


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

