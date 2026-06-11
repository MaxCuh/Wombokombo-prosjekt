import pymysql
import os
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'fallback-nokkel')
app.config['SESSION_COOKIE_NAME'] = 'session'

def get_db():
    return pymysql.connect(
        host="localhost",
        user="quizuser",
        password="dittPassord123",
        database="quizapp"
    )

@app.route('/')
def index():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('index.html', username=session['username'], role=session['role'])

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        login_input = request.form['login_input']
        password = request.form['password']
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM user WHERE email = %s OR username = %s", (login_input, login_input))
        user = cursor.fetchone()
        db.close()
        if user and check_password_hash(user[3], password):
            session['username'] = user[1]
            session['role'] = user[4]
            return redirect('http://127.0.0.1:5001/dashboard') 
        return render_template('login.html', error='Feil brukernavn/epost eller passord')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm password']

        if password != confirm_password:
            return render_template('register.html', error='Passordene stemmer ikke', username=username, email=email)

        hashed_password = generate_password_hash(password)
        db = get_db()
        cursor = db.cursor()
        try:
            cursor.execute("INSERT INTO user (username, email, password, role) VALUES (%s, %s, %s, %s)",
                         (username, email, hashed_password, 'user'))
            db.commit()
            return redirect(url_for('login'))
        except:
            return render_template('register.html', error='Brukernavn eller epost er allerede tatt', username=username, email=email)
        finally:
            db.close()
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/admin')
def admin():
    if 'username' not in session:
        return redirect(url_for('login'))
    if session['role'] != 'admin':
        return 'Ingen tilgang', 403
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT id, username, email, role FROM user")
    users = cursor.fetchall()
    db.close()
    return render_template('admin.html', users=users)

if __name__ == '__main__':
    app.run(debug=True, port=5000)

