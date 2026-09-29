"""
AI-Based Resume Screening & Job Recommendation System
Main Flask Application Entrypoint with User Authentication (Signup, Login, Logout, Session & Route Protection)
"""

import os
import sqlite3
import datetime
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, flash, session, g
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
import pandas as pd

# Import project utilities and NLP model
from utils.resume_parser import parse_resume_file
from utils.skill_extractor import parse_resume_full
from model.matching_model import JobMatcher

# Initialize Flask application
app = Flask(__name__)
app.secret_key = 'super_secret_ai_resume_key_2026'

# Configuration paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
DATA_FOLDER = os.path.join(BASE_DIR, 'data')
SAMPLE_FOLDER = os.path.join(DATA_FOLDER, 'sample_resumes')
DATABASE_PATH = os.path.join(BASE_DIR, 'database.db')
JOBS_CSV_PATH = os.path.join(DATA_FOLDER, 'jobs.csv')

ALLOWED_EXTENSIONS = {'pdf', 'docx', 'doc'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB max upload limit

# Ensure necessary directories exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(SAMPLE_FOLDER, exist_ok=True)


def get_db_connection():
    """Helper function to obtain a sqlite3 database connection with Row factory."""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """
    Creates SQLite database tables if they do not exist:
    - users (Authentication)
    - jobs (Sample Job Postings)
    - resumes (Uploaded Candidate Resumes linked to users)
    - analysis_results (Historical match results)
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. Create Users Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # 2. Create Jobs Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_title TEXT NOT NULL,
            company TEXT NOT NULL,
            location TEXT NOT NULL,
            experience_level TEXT NOT NULL,
            required_skills TEXT NOT NULL,
            description TEXT NOT NULL
        )
    ''')

    # 3. Create Resumes Table (with user_id column)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS resumes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            filename TEXT NOT NULL,
            candidate_name TEXT NOT NULL,
            email TEXT NOT NULL,
            phone TEXT NOT NULL,
            extracted_skills TEXT NOT NULL,
            raw_text TEXT NOT NULL,
            education TEXT,
            experience TEXT,
            projects TEXT,
            uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')

    # Check if user_id column exists in resumes (migration safety for existing DBs)
    cursor.execute("PRAGMA table_info(resumes)")
    columns = [col[1] for col in cursor.fetchall()]
    if 'user_id' not in columns:
        cursor.execute("ALTER TABLE resumes ADD COLUMN user_id INTEGER REFERENCES users(id)")

    # 4. Create Analysis Results Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS analysis_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            resume_id INTEGER NOT NULL,
            top_job_title TEXT NOT NULL,
            top_match_score REAL NOT NULL,
            analyzed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (resume_id) REFERENCES resumes (id)
        )
    ''')

    conn.commit()

    # Seed Jobs from CSV if empty
    cursor.execute("SELECT COUNT(*) FROM jobs")
    job_count = cursor.fetchone()[0]

    if job_count == 0 and os.path.exists(JOBS_CSV_PATH):
        df = pd.read_csv(JOBS_CSV_PATH)
        for _, row in df.iterrows():
            cursor.execute('''
                INSERT INTO jobs (job_title, company, location, experience_level, required_skills, description)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                row['job_title'], row['company'], row['location'],
                row['experience_level'], row['required_skills'], row['description']
            ))
        conn.commit()

    conn.close()

    # Ensure sample resumes exist
    try:
        from data.create_sample_resumes import create_sample_docx, create_sample_docx_jane
        sample_john = os.path.join(SAMPLE_FOLDER, 'sample_resume_john_doe.docx')
        sample_jane = os.path.join(SAMPLE_FOLDER, 'sample_resume_jane_smith.docx')
        if not os.path.exists(sample_john):
            create_sample_docx(sample_john)
        if not os.path.exists(sample_jane):
            create_sample_docx_jane(sample_jane)
    except Exception as e:
        pass


def allowed_file(filename):
    """Check if uploaded file has a valid allowed extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def login_required(f):
    """Decorator to enforce user login for protected routes."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to your account to access this feature.', 'info')
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function


@app.before_request
def load_logged_in_user():
    """Load logged in user info into Flask global 'g' context before each request."""
    user_id = session.get('user_id')
    if user_id is None:
        g.user = None
    else:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, email, username FROM users WHERE id = ?", (user_id,))
        g.user = cursor.fetchone()
        conn.close()


# --------------------------------------------------------------------------
# Authentication Routes
# --------------------------------------------------------------------------

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    """User Registration Route."""
    if 'user_id' in session:
        return redirect(url_for('index'))

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        username = request.form.get('username', '').strip().lower()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')

        # Basic Form Validation
        if not name or not email or not username or not password:
            flash('All fields are required. Please fill out the full form.', 'error')
            return render_template('signup.html')

        if password != confirm_password:
            flash('Passwords do not match. Please re-enter your password.', 'error')
            return render_template('signup.html')

        if len(password) < 6:
            flash('Password must be at least 6 characters long.', 'error')
            return render_template('signup.html')

        conn = get_db_connection()
        cursor = conn.cursor()

        # Check for duplicate email or username
        cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
        if cursor.fetchone():
            conn.close()
            flash('An account with this email address already exists. Please log in.', 'error')
            return render_template('signup.html')

        cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
        if cursor.fetchone():
            conn.close()
            flash('This username is already taken. Please choose a different username.', 'error')
            return render_template('signup.html')

        # Hash password securely and create user record
        password_hash = generate_password_hash(password)
        cursor.execute('''
            INSERT INTO users (name, email, username, password_hash)
            VALUES (?, ?, ?, ?)
        ''', (name, email, username, password_hash))
        
        user_id = cursor.lastrowid
        conn.commit()
        conn.close()

        # Auto-login after successful registration
        session['user_id'] = user_id
        session['user_name'] = name
        session['user_username'] = username

        flash(f'Welcome, {name}! Your account has been created successfully.', 'success')
        return redirect(url_for('index'))

    return render_template('signup.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    """User Login Route."""
    if 'user_id' in session:
        return redirect(url_for('index'))

    if request.method == 'POST':
        identity = request.form.get('identity', '').strip().lower()
        password = request.form.get('password', '')

        if not identity or not password:
            flash('Please enter both your email/username and password.', 'error')
            return render_template('login.html')

        conn = get_db_connection()
        cursor = conn.cursor()
        # Query by email OR username
        cursor.execute("SELECT * FROM users WHERE email = ? OR username = ?", (identity, identity))
        user = cursor.fetchone()
        conn.close()

        if user and check_password_hash(user['password_hash'], password):
            # Login Success: set session state
            session['user_id'] = user['id']
            session['user_name'] = user['name']
            session['user_username'] = user['username']

            flash(f'Welcome back, {user["name"]}!', 'success')
            next_url = request.args.get('next')
            return redirect(next_url or url_for('index'))
        else:
            flash('Invalid login credentials. Please check your email/username and password.', 'error')
            return render_template('login.html')

    return render_template('login.html')


@app.route('/logout')
def logout():
    """User Logout Route."""
    session.clear()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('login'))


# --------------------------------------------------------------------------
# Main Core Routes
# --------------------------------------------------------------------------

@app.route('/')
def index():
    """Home Page Route."""
    return render_template('index.html')


@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    """
    Protected Resume Upload & Processing Route.
    Requires user login. Associates resume with current logged-in user.
    """
    if request.method == 'POST':
        if 'resume_file' not in request.files:
            flash('No file part provided in the request.', 'error')
            return redirect(request.url)

        file = request.files['resume_file']
        if file.filename == '':
            flash('No file selected for uploading.', 'error')
            return redirect(request.url)

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S_")
            saved_filename = timestamp + filename
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], saved_filename)
            file.save(filepath)

            try:
                raw_text, ext = parse_resume_file(filepath)
                parsed_data = parse_resume_full(raw_text)
                skills_str = ", ".join(parsed_data['skills'])

                user_id = session.get('user_id')

                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO resumes (user_id, filename, candidate_name, email, phone, extracted_skills, raw_text, education, experience, projects)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    user_id,
                    saved_filename,
                    parsed_data['name'],
                    parsed_data['email'],
                    parsed_data['phone'],
                    skills_str,
                    raw_text,
                    parsed_data['education'],
                    parsed_data['experience'],
                    parsed_data['projects']
                ))
                resume_id = cursor.lastrowid
                conn.commit()
                conn.close()

                session['last_resume_id'] = resume_id
                flash('Resume uploaded and analyzed successfully!', 'success')
                return redirect(url_for('result', resume_id=resume_id))

            except Exception as e:
                flash(f"Error processing resume file: {str(e)}", 'error')
                return redirect(request.url)
        else:
            flash('Invalid file format. Please upload a PDF (.pdf) or Word (.docx) file.', 'error')
            return redirect(request.url)

    return render_template('upload.html')


@app.route('/upload_sample/<sample_name>')
@login_required
def upload_sample(sample_name):
    """
    Protected Helper route to quickly test the application with sample resumes.
    Requires user login.
    """
    if sample_name == 'john_doe':
        sample_path = os.path.join(SAMPLE_FOLDER, 'sample_resume_john_doe.docx')
        filename = 'sample_resume_john_doe.docx'
    elif sample_name == 'jane_smith':
        sample_path = os.path.join(SAMPLE_FOLDER, 'sample_resume_jane_smith.docx')
        filename = 'sample_resume_jane_smith.docx'
    else:
        flash('Invalid sample resume requested.', 'error')
        return redirect(url_for('upload'))

    if not os.path.exists(sample_path):
        flash('Sample resume file missing.', 'error')
        return redirect(url_for('upload'))

    try:
        raw_text, ext = parse_resume_file(sample_path)
        parsed_data = parse_resume_full(raw_text)
        skills_str = ", ".join(parsed_data['skills'])
        user_id = session.get('user_id')

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO resumes (user_id, filename, candidate_name, email, phone, extracted_skills, raw_text, education, experience, projects)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            user_id,
            filename,
            parsed_data['name'],
            parsed_data['email'],
            parsed_data['phone'],
            skills_str,
            raw_text,
            parsed_data['education'],
            parsed_data['experience'],
            parsed_data['projects']
        ))
        resume_id = cursor.lastrowid
        conn.commit()
        conn.close()

        session['last_resume_id'] = resume_id
        flash(f"Sample resume ({filename}) loaded successfully!", 'success')
        return redirect(url_for('result', resume_id=resume_id))
    except Exception as e:
        flash(f"Failed to process sample resume: {str(e)}", 'error')
        return redirect(url_for('upload'))


@app.route('/result/<int:resume_id>')
@login_required
def result(resume_id):
    """Protected Resume Analysis View Route."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM resumes WHERE id = ?", (resume_id,))
    resume = cursor.fetchone()
    conn.close()

    if not resume:
        flash('Resume record not found.', 'error')
        return redirect(url_for('upload'))

    skills_list = [s.strip() for s in resume['extracted_skills'].split(',') if s.strip()]
    return render_template('result.html', resume=resume, skills=skills_list)


@app.route('/recommendations/<int:resume_id>')
@login_required
def recommendations(resume_id):
    """Protected Job Recommendation Route."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM resumes WHERE id = ?", (resume_id,))
    resume = cursor.fetchone()

    if not resume:
        conn.close()
        flash('Resume not found.', 'error')
        return redirect(url_for('upload'))

    cursor.execute("SELECT * FROM jobs")
    jobs_records = cursor.fetchall()
    conn.close()

    jobs_list = [dict(job) for job in jobs_records]
    candidate_skills = [s.strip() for s in resume['extracted_skills'].split(',') if s.strip()]

    matcher = JobMatcher()
    top_recommendations = matcher.calculate_matches(
        resume_text=resume['raw_text'],
        jobs_list=jobs_list,
        candidate_skills=candidate_skills,
        top_n=5
    )

    if top_recommendations:
        top_rec = top_recommendations[0]
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO analysis_results (resume_id, top_job_title, top_match_score)
            VALUES (?, ?, ?)
        ''', (resume_id, top_rec['job_title'], top_rec['match_percentage']))
        conn.commit()
        conn.close()

    return render_template('recommendations.html', resume=resume, recommendations=top_recommendations)


@app.route('/dashboard/<int:resume_id>')
@login_required
def dashboard(resume_id):
    """Protected Candidate Dashboard Route."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM resumes WHERE id = ?", (resume_id,))
    resume = cursor.fetchone()

    if not resume:
        conn.close()
        flash('Resume record not found.', 'error')
        return redirect(url_for('upload'))

    cursor.execute("SELECT COUNT(*) FROM jobs")
    total_jobs_count = cursor.fetchone()[0]

    cursor.execute("SELECT * FROM jobs")
    jobs_records = cursor.fetchall()
    conn.close()

    jobs_list = [dict(job) for job in jobs_records]
    candidate_skills = [s.strip() for s in resume['extracted_skills'].split(',') if s.strip()]

    matcher = JobMatcher()
    top_recommendations = matcher.calculate_matches(
        resume_text=resume['raw_text'],
        jobs_list=jobs_list,
        candidate_skills=candidate_skills,
        top_n=5
    )

    top_match = top_recommendations[0] if top_recommendations else None

    return render_template(
        'dashboard.html',
        resume=resume,
        skills=candidate_skills,
        total_jobs_count=total_jobs_count,
        top_match=top_match,
        recommendations=top_recommendations
    )


@app.route('/jobs')
def browse_jobs():
    """Public Browse Job Database Route."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM jobs")
    jobs = cursor.fetchall()
    conn.close()
    return render_template('jobs.html', jobs=jobs)


# --------------------------------------------------------------------------
# Main Execution Entrypoint
# --------------------------------------------------------------------------
if __name__ == '__main__':
    print("Initializing Database & Authentication Tables...")
    init_db()
    print("Starting Flask Development Server on http://127.0.0.1:5000")
    app.run(debug=True, host='127.0.0.1', port=5000)
