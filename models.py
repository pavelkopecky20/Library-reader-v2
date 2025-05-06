from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=True)
    author = db.Column(db.String(255), nullable=True)
    is_read = db.Column(db.Boolean, nullable=True) # ano X ne
    rating = db.Column(db.Integer, nullable=True)       # 1 - 10 hvězdiček
    abstract = db.Column(db.String(255), nullable=True)
    comment = db.Column(db.String(255), nullable=True)  # komentář
