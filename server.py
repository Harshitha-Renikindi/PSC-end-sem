from flask import Flask, render_template, request, redirect, url_for, flash
import psycopg2

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

# Function to create the users table if it doesn't exist
def create_table_if_not_exists():
    try:
        conn = psycopg2.connect(
            dbname='postgres',
            user='postgres',
            password='2004',
            host='localhost'
        )
        cur = conn.cursor()
        cur.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                password VARCHAR(100) NOT NULL
            )
        ''')
        conn.commit()
        cur.close()
        conn.close()
    except psycopg2.Error as e:
        print("Error creating users table:", e)

# Create the table if it doesn't exist
create_table_if_not_exists()

@app.route('/')
def login():
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        try:
            conn = psycopg2.connect(
                dbname='postgres',
                user='postgres',
                password='2004',
                host='localhost'
            )
            cur = conn.cursor()
            cur.execute('SELECT * FROM users WHERE username=%s', (username,))
            if cur.fetchone():
                flash('Username already exists. Please choose a different one.', 'error')
                cur.close()
                conn.close()
                return redirect(url_for('register'))

            cur.execute('INSERT INTO users (username, password) VALUES (%s, %s)', (username, password))
            conn.commit()
            cur.close()
            conn.close()

            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
        except psycopg2.Error as e:
            print("Error registering user:", e)
            flash('An error occurred while registering. Please try again later.', 'error')
            return redirect(url_for('register'))

    return render_template('register.html')

@app.route('/dashboard', methods=['POST'])
def dashboard():
    username = request.form['username']
    password = request.form['password']

    try:
        conn = psycopg2.connect(
            dbname='postgres',
            user='postgres',
            password='2004',
            host='localhost'
        )
        cur = conn.cursor()
        cur.execute('SELECT * FROM users WHERE username=%s AND password=%s', (username, password))
        user = cur.fetchone()
        cur.close()
        conn.close()

        if user:
            if 'teacher' in username:
                return redirect(url_for('teacher_dashboard'))
            else:
                return redirect(url_for('student_dashboard'))
        else:
            flash('Incorrect username or password. Please try again.', 'error')
            return redirect(url_for('login'))
    except psycopg2.Error as e:
        print("Error logging in:", e)
        flash('An error occurred while logging in. Please try again later.', 'error')
        return redirect(url_for('login'))

@app.route('/student/dashboard')
def student_dashboard():
    return render_template('student_dashboard.html')

@app.route('/teacher/dashboard')
def teacher_dashboard():
    return render_template('teacher_dashboard.html')

if __name__ == '__main__':
    app.run(debug=True)
