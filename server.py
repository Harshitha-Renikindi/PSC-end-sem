from flask import Flask, render_template, request, redirect, url_for, flash, session
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

# Function to create the enrollments table if it doesn't exist
def create_enrollments_table_if_not_exists():
    try:
        conn = psycopg2.connect(
            dbname='postgres',
            user='postgres',
            password='2004',
            host='localhost'
        )
        cur = conn.cursor()
        cur.execute('''
            CREATE TABLE IF NOT EXISTS enrollments (
                id SERIAL PRIMARY KEY,
                student_id INTEGER,
                course_id INTEGER,
                FOREIGN KEY (student_id) REFERENCES users(id),
                FOREIGN KEY (course_id) REFERENCES courses(id)
            )
        ''')
        conn.commit()
        cur.close()
        conn.close()
    except psycopg2.Error as e:
        print("Error creating enrollments table:", e)

# Create the tables if they don't exist
create_table_if_not_exists()
create_courses_table_if_not_exists()
create_enrollments_table_if_not_exists()

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
            session['username'] = username
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
    if 'username' not in session:
        flash('You must be logged in to access this page.', 'error')
        return redirect(url_for('login'))

    try:
        conn = psycopg2.connect(
            dbname='postgres',
            user='postgres',
            password='2004',
            host='localhost'
        )
        cur = conn.cursor()
        cur.execute('''
            SELECT courses.id, courses.name, courses.duration 
            FROM courses 
            INNER JOIN enrollments ON courses.id = enrollments.course_id 
            WHERE enrollments.student_id = (
                SELECT id FROM users WHERE username=%s
            )
        ''', (session['username'],))
        courses = cur.fetchall()
        cur.close()
        conn.close()

        return render_template('student_dashboard.html', courses=courses)
    except psycopg2.Error as e:
        print("Error fetching enrolled courses:", e)
        flash('An error occurred while fetching enrolled courses. Please try again later.', 'error')
        return redirect(url_for('login'))

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

# Route for enrolling in a course
@app.route('/enroll', methods=['POST'])
def enroll_course():
    if 'username' not in session:
        flash('You must be logged in to enroll in a course.', 'error')
        return redirect(url_for('login'))

    # Get the course ID from the form
    course_id = request.form.get('course_id')

    try:
        # Retrieve the course details from the database
        conn = psycopg2.connect(
            dbname='postgres',
            user='postgres',
            password='2004',
            host='localhost'
        )
        cur = conn.cursor()

        # Check if the student is already enrolled in the course
        cur.execute('''
            SELECT * FROM enrollments 
            WHERE student_id = (SELECT id FROM users WHERE username=%s) 
            AND course_id = %s
        ''', (session['username'], course_id))
        enrollment = cur.fetchone()

        if enrollment:
            flash('You are already enrolled in this course.', 'error')
            return redirect(url_for('student_dashboard'))

        # Enroll the student in the course
        cur.execute('''
            INSERT INTO enrollments (student_id, course_id) 
            VALUES ((SELECT id FROM users WHERE username=%s), %s)
        ''', (session['username'], course_id))
        conn.commit()

        flash('Course enrolled successfully!', 'success')
    except psycopg2.Error as e:
        print("Error enrolling in course:", e)
        flash('An error occurred while enrolling in the course. Please try again later.', 'error')

    return redirect(url_for('student_dashboard'))

# Route for dropping a course
@app.route('/drop', methods=['POST'])
def drop_course():
    if 'username' not in session:
        flash('You must be logged in to drop a course.', 'error')
        return redirect(url_for('login'))

    # Get the course ID from the form
    course_id = request.form.get('course_id')

    try:
        # Retrieve the course details from the database
        conn = psycopg2.connect(
            dbname='postgres',
            user='postgres',
            password='2004',
            host='localhost'
        )
        cur = conn.cursor()

        # Drop the course from the student's enrollment
        cur.execute('''
            DELETE FROM enrollments 
            WHERE student_id = (SELECT id FROM users WHERE username=%s) 
            AND course_id = %s
        ''', (session['username'], course_id))
        conn.commit()

        flash('Course dropped successfully!', 'success')
    except psycopg2.Error as e:
        print("Error dropping course:", e)
        flash('An error occurred while dropping the course. Please try again later.', 'error')

    return redirect(url_for('student_dashboard'))

if __name__ == '__main__':
    app.run(debug=True)
