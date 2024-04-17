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

# Function to create the courses table if it doesn't exist
def create_courses_table_if_not_exists():
    try:
        conn = psycopg2.connect(
            dbname='postgres',
            user='postgres',
            password='2004',
            host='localhost'
        )
        cur = conn.cursor()
        cur.execute('''
            CREATE TABLE IF NOT EXISTS courses (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                duration FLOAT NOT NULL
            )
        ''')
        conn.commit()
        cur.close()
        conn.close()
    except psycopg2.Error as e:
        print("Error creating courses table:", e)

# Create the tables if they don't exist
create_table_if_not_exists()
create_courses_table_if_not_exists()

# Route for the login page
@app.route('/')
def login():
    return render_template('login.html')

# Route for handling the login form submission
@app.route('/login', methods=['POST'])
def login_submit():
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

# Route for the registration page
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

# Route for the regular dashboard
@app.route('/student/dashboard')
def student_dashboard():
    return render_template('student_dashboard.html')

# Route for the teacher dashboard
@app.route('/teacher/dashboard')
def teacher_dashboard():
    try:
        conn = psycopg2.connect(
            dbname='postgres',
            user='postgres',
            password='2004',
            host='localhost'
        )
        cur = conn.cursor()
        cur.execute('SELECT * FROM courses')
        courses = cur.fetchall()
        cur.close()
        conn.close()

        return render_template('teacher_dashboard.html', courses=courses)
    except psycopg2.Error as e:
        print("Error fetching courses:", e)
        flash('An error occurred while fetching courses. Please try again later.', 'error')
        return redirect(url_for('teacher_dashboard'))

# Route for creating a course
@app.route('/create', methods=['POST'])
def create_course():
    name = request.form['name']
    duration = request.form['duration']
    print(name,duration)
    try:
        conn = psycopg2.connect(
            dbname='postgres',
            user='postgres',
            password='2004',
            host='localhost'
        )
        cur = conn.cursor()
        cur.execute('INSERT INTO courses (name, price) VALUES (%s, %s)', (name, duration))
        conn.commit()
        cur.close()
        conn.close()


        flash('Course created successfully!', 'success')
    except psycopg2.Error as e:
        print("Error creating course:", e)
        flash('An error occurred while creating the course. Please try again later.', 'error')

    return redirect(url_for('teacher_dashboard'))

# Route for updating a course
@app.route('/update', methods=['POST'])
def update_course():
    id = request.form['id']
    name = request.form['name']
    duration = request.form['duration']

    try:
        conn = psycopg2.connect(
            dbname='postgres',
            user='postgres',
            password='2004',
            host='localhost'
        )
        cur = conn.cursor()
        cur.execute('UPDATE courses SET name=%s, duration=%s WHERE id=%s', (name, duration, id))
        conn.commit()
        cur.close()
        conn.close()

        flash('Course updated successfully!', 'success')
    except psycopg2.Error as e:
        print("Error updating course:", e)
        flash('An error occurred while updating the course. Please try again later.', 'error')

    return redirect(url_for('teacher_dashboard'))

# Route for deleting a course
@app.route('/delete', methods=['POST'])
def delete_course():
    id = request.form['id']

    try:
        conn = psycopg2.connect(
            dbname='postgres',
            user='postgres',
            password='2004',
            host='localhost'
        )
        cur = conn.cursor()
        cur.execute('DELETE FROM courses WHERE id=%s', (id,))
        conn.commit()
        cur.close()
        conn.close()

        flash('Course deleted successfully!', 'success')
    except psycopg2.Error as e:
        print("Error deleting course:", e)
        flash('An error occurred while deleting the course. Please try again later.', 'error')

    return redirect(url_for('teacher_dashboard'))

# Route for displaying the index page with all courses
@app.route('/index')
def index():
    try:
        conn = psycopg2.connect(
            dbname='postgres',
            user='postgres',
            password='2004',
            host='localhost'
        )
        cur = conn.cursor()
        cur.execute('SELECT * FROM courses')
        data = cur.fetchall()
        cur.close()
        conn.close()

        return render_template('index.html', data=data)
    except psycopg2.Error as e:
        print("Error fetching courses:", e)
        flash('An error occurred while fetching courses. Please try again later.', 'error')
        return redirect(url_for('teacher_dashboard'))

if __name__ == '__main__':
    app.run(debug=True)
