from flask import Flask, render_template, redirect, request, url_for, g, session
import sqlite3
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash

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

def query_db(query, args=(), one=False, inserting=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    if inserting:
        get_db().commit()
        return cur.lastrowid
    else:
        return (rv[0] if rv else None) if one else rv

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/news")
def news():
    news = query_db("SELECT * FROM news")
    events = query_db("SELECT * FROM events")
    return render_template("news_events.html", news = news, events = events)



@app.route('/news/<int:news_id>')
def show_post(news_id):
    article = query_db("SELECT heading, date, article FROM news WHERE news_id = ?", [news_id], one=True)
    images = query_db("SELECT file_name, alt FROM images WHERE news_id = ?", [news_id], one=True)
    return render_template("news_article.html", article = article, images = images)

@app.route('/admin')
def admin():
    return render_template("admin_login.html",)

@app.post('/admin_login')
def admin_login():

    username = request.form['username']
    password = request.form['password']

    if not username or not password:
        error = "Username and password are required."
        return render_template("admin_login.html", error=error)

    user = query_db("SELECT username, password FROM logins WHERE username = ?", (username,), one=True)

    if user and check_password_hash(user[1], password):
        return redirect('/admin/dashboard')
    else:
        error = "Username or password is incorrect."
        return render_template("admin_login.html", error=error)


@app.route('/admin/dashboard')
def admin_dashboard():
    return render_template('admin.html')
            




@app.post('/add_item')
def add_item():
    
    uploadFolder = 'static/images/'
    
    file = request.files['file']
    heading = request.form['heading']
    date = request.form['date']
    sentence = request.form['article_sentence']
    text = request.form['article_text']
    alt_text = request.form['alt_text']

    filename = secure_filename(file.filename)
    file.save(uploadFolder+filename)

    sql = "INSERT INTO images (file_name, alt, news_id) VALUES (?, ?, ?);"  


    sql2 = """
        INSERT INTO news (heading, date, article_sentence, article)
        VALUES (?, ?, ?, ?);
    """

    id = query_db(sql2,(heading, date, sentence, text),inserting=True)


    query_db(sql,(filename, alt_text, id))


    get_db().commit()
    return redirect('/') 





if __name__ == "__main__":
    app.run(debug=True)

