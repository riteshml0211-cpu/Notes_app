from flask import Flask, render_template, request, redirect

import sqlite3
import os

app = Flask(__name__)
app.secret_key = "secret123"

UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


# ---------------- CHECK LOGIN ----------------
def login_required():
    return 'user' in session


# ---------------- HOME ----------------
@app.route('/')
def home():
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("SELECT * FROM notes")
    notes = c.fetchall()
    conn.close()

    return render_template("index.html", notes=notes)


# ---------------- SIGNUP ----------------
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        u = request.form['username']
        p = request.form['password']

        conn = sqlite3.connect("database.db")
        c = conn.cursor()
        c.execute("INSERT INTO users(username,password) VALUES(?,?)", (u, p))
        conn.commit()
        conn.close()

        return redirect('/login')

    return render_template("signup.html")


# ---------------- LOGIN ----------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        u = request.form['username']
        p = request.form['password']

        conn = sqlite3.connect("database.db")
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username=? AND password=?", (u, p))
        user = c.fetchone()
        conn.close()

        if user:
            session['user'] = u
            return redirect('/')
        else:
            return "Invalid login"

    return render_template("login.html")


# ---------------- LOGOUT ----------------
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')


# ---------------- UPLOAD (LOGIN REQUIRED) ----------------
@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if not login_required():
        return redirect('/login')

    if request.method == 'POST':
        title = request.form['title']
        subject = request.form['subject']
        file = request.files['file']

        filename = file.filename
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        conn = sqlite3.connect("database.db")
        c = conn.cursor()
        c.execute("INSERT INTO notes(title,subject,filename,user) VALUES(?,?,?,?)",
                  (title, subject, filename, session['user']))
        conn.commit()
        conn.close()

        return redirect('/')

    return render_template("upload.html")


# ---------------- USER UPLOAD HISTORY ----------------
@app.route('/myuploads')
def myuploads():
    if not login_required():
        return redirect('/login')

    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("SELECT * FROM notes WHERE user=?", (session['user'],))
    notes = c.fetchall()
    conn.close()

    return render_template("myuploads.html", notes=notes)


if __name__ == "__main__":
    app.run(debug=True)
    
    from flask import Flask
import sqlite3

app = Flask(__name__)

# ---------- DATABASE ----------
def init_db():
    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        password TEXT
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS notes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        subject TEXT,
        filename TEXT,
        user TEXT
    )
    """)

    conn.commit()
    conn.close()

init_db()


if __name__ == "__main__":
    app.run(debug=True)
