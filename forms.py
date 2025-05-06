from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, BooleanField, TextAreaField, SubmitField, FileField, SubmitField
from wtforms.validators import DataRequired, NumberRange

class UploadForm(FlaskForm):
    image = FileField("Nahraj obrázek knihovny", validators=[DataRequired()])
    submit = SubmitField("Nahrát a rozpoznat")



class BookForm(FlaskForm):
    title = StringField("Název", validators=[DataRequired()])
    author = StringField("Autor")
    rating = IntegerField("Hodnocení", validators=[NumberRange(min=1, max=5)], default=3)
    is_read = BooleanField("Přečteno")
    abstract = TextAreaField("Abstrakt")
    submit = SubmitField("Uložit")
