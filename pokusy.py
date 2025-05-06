from models import db, Book

data =[
    {"title": "the body keeps the score", "author": "bessel van der kolk"},
   {"title": "outlive", "author": None},
   {"title": "dr peter attia", "author": None},
   {"title": "hector garcia and", "author": None},
   {"title": "hector garcia and", "author": None},
   {"title": "wifedom", "author": None},
   {"title": "prince harry spare", "author": None},
    {"title": "ingredients mediterranean", "author": "jamie oliver"},
    {"title": "ingredients mediterranean", "author": "jamie oliver"},
    {"title": "why has nobody told me this before?", "author": "anna funder"},
    {"title": "dr julie smith", "author": None},
    {"title": "question 7", "author": None},
    {"title": "richard", "author": "flanagan"},
    {"title": "atomic habits clear", "author": None},
    {"title": "12 rules for life", "author": "jordan b. peterson"}
]

    
with app.app_context():
    db.create_all()  # vytvoří tabulky pokud ještě nejsou
    for item in data:
        title = item['title']
        author = item['author'] if item['author'] else "Neznámý"
        book = Book(title=title, author=author)
        db.session.add(book)
    db.session.commit()
    print("✅ Data byla úspěšně uložena do databáze.")