from app import db

class WikiWoods(db.Model):
    __bind_key__ = 'wikiwoods'
    id = db.Column(db.Integer, primary_key=True)
    word =db.Column(db.UnicodeText(64))
    vector = db.Column(db.Text)
