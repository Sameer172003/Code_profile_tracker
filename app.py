
from flask import Flask, render_template, url_for, request, session, flash, redirect
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from scraper_utils import fetch_leetcode_stats, fetch_gfg_stats

app = Flask(__name__)
app.secret_key = "my_secret_key"

# Initialize database
def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS profiles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            leetcode TEXT,
            gfg TEXT,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    ''')
    conn.commit()
    conn.close()

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == "POST":
        username = request.form['username']
        email = request.form['email']
        password = generate_password_hash(request.form['password'])

        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()

        try:
            cursor.execute('INSERT INTO users (username, email, password) VALUES (?, ?, ?)',
                           (username, email, password))
            conn.commit()
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Email already exists.', 'danger')
        finally:
            conn.close()

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        email = request.form['email']
        password = request.form['password']

        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
        user = cursor.fetchone()
        conn.close()

        if user and check_password_hash(user[3], password):
            session['user_id'] = user[0]
            session['username'] = user[1]
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid credentials.', 'danger')

    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    username = session['username']
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT leetcode, gfg FROM profiles WHERE user_id = ?", (session['user_id'],))
    result = cursor.fetchone()
    conn.close()

    leetcode_data = {}
    gfg_data = {}

    if result:
        leetcode_user, gfg_user = result

        if leetcode_user:
            leetcode_data = fetch_leetcode_stats(leetcode_user)

        if gfg_user:
            gfg_data = fetch_gfg_stats(gfg_user)
    
    total_solved = 0

    try:
        total_solved += int(leetcode_data.get('totalSolved', 0))
    except: pass

    try:
        total_solved += int(gfg_data.get('total_solved', 0))
    except: pass

    return render_template(
        'dashboard.html',
        username=username,
        leetcode_data=leetcode_data,
        gfg_data=gfg_data,
        total_solved=total_solved
    )

@app.route('/add_profiles', methods=['GET', 'POST'])
def add_profiles():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']

    if request.method == 'POST':
        leetcode = request.form['leetcode']
        gfg = request.form['gfg']

        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM profiles WHERE user_id = ?', (user_id,))
        existing = cursor.fetchone()

        if existing:
            cursor.execute('''
                UPDATE profiles
                SET leetcode=?, gfg=?
                WHERE user_id=?
            ''', (leetcode, gfg, user_id))
        else:
            cursor.execute('''
                INSERT INTO profiles (user_id, leetcode, gfg)
                VALUES (?, ?, ?)
            ''', (user_id, leetcode, gfg))

        conn.commit()
        conn.close()
        flash('Profiles saved successfully.', 'success')
        return redirect(url_for('dashboard'))

    return render_template('add_profiles.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == "__main__":
    init_db()
    app.run(debug=True)

