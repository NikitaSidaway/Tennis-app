from flask import Flask, render_template,g
import sqlite3

app = Flask(__name__)

DATABASE = 'database.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

@app.route("/")
def home():
    news = query_db("SELECT * FROM news")
    events = query_db("SELECT * FROM events")
    return render_template("index.html", news = news, events = events)



@app.route('/news/<int:news_id>')
def show_post(news_id):
    article = query_db("SELECT heading, date, article FROM news WHERE news_id = ?", [news_id], one=True)
    images = query_db("SELECT file_name, alt FROM images WHERE news_id = ?", [news_id], one=True)
    return render_template("news_article.html", article = article, images = images)


if __name__ == "__main__":
    app.run(debug=True)