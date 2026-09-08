"""
GreenEdu - Green Technology Awareness Platform
Flask + MySQL (XAMPP)
"""

import MySQLdb
import bcrypt
from flask import (Flask, render_template, request, redirect, url_for,
                   session, flash, abort)
from functools import wraps
from datetime import datetime
import config

app = Flask(__name__)
app.config.from_object(config)


# ==================== DATABASE ====================
def get_db():
    return MySQLdb.connect(
        host=config.MYSQL_HOST,
        user=config.MYSQL_USER,
        passwd=config.MYSQL_PASSWORD,
        db=config.MYSQL_DB,
        port=config.MYSQL_PORT,
        charset='utf8mb4'
    )


# ==================== AUTH ====================
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        if session.get('role') not in ['admin', 'researcher']:
            flash('Admin access required.', 'danger')
            return redirect(url_for('home'))
        return f(*args, **kwargs)
    return decorated


# ==================== PUBLIC ROUTES ====================

@app.route('/')
def home():
    return render_template('home.html')


@app.route('/about')
def about():
    return render_template('about.html')


def compute_green_score(solar, wind, grid, diesel, water, waste):
    """Compute a green score (0-100) from energy/resource values.

    Higher renewable (solar+wind) and recycling, lower diesel/grid = better score.
    """
    try:
        solar = float(solar or 0)
        wind = float(wind or 0)
        grid = float(grid or 0)
        diesel = float(diesel or 0)
        water = float(water or 0)
        waste = float(waste or 0)
    except (ValueError, TypeError):
        return 0

    total_energy = solar + wind + grid
    if total_energy <= 0:
        return 0

    renewable_ratio = (solar + wind) / total_energy  # 0-1
    renewable_score = renewable_ratio * 50  # up to 50 pts

    # Lower diesel = better
    diesel_score = max(0, 20 - (diesel / 10))  # up to 20 pts

    # Water score: lower is better
    water_score = max(0, 15 - (water / 2000))  # up to 15 pts

    # Waste recycled: higher is better
    waste_score = min(15, waste / 10)  # up to 15 pts

    total = renewable_score + diesel_score + water_score + waste_score
    return min(100, int(total))


@app.route('/colleges', methods=['GET', 'POST'])
def colleges():
    """Public page: list of colleges + form to submit energy data."""
    db = get_db()
    cursor = db.cursor(MySQLdb.cursors.DictCursor)

    if request.method == 'POST':
        college_name = request.form.get('college_name', '').strip()
        contact_person = request.form.get('contact_person', '').strip()
        contact_email = request.form.get('contact_email', '').strip()
        location = request.form.get('location', '').strip()
        student_count = request.form.get('student_count', 0)
        solar = request.form.get('solar_kwh', 0)
        wind = request.form.get('wind_kwh', 0)
        grid = request.form.get('grid_kwh', 0)
        diesel = request.form.get('diesel_liters', 0)
        water = request.form.get('water_liters_per_day', 0)
        waste = request.form.get('waste_recycled_kg', 0)
        notes = request.form.get('notes', '').strip()

        if not college_name:
            flash('College name is required.', 'danger')
            return redirect(url_for('colleges'))

        score = compute_green_score(solar, wind, grid, diesel, water, waste)

        cursor.execute("""
            INSERT INTO energy_data
              (college_name, contact_person, contact_email, location, student_count,
               solar_kwh, wind_kwh, grid_kwh, diesel_liters,
               water_liters_per_day, waste_recycled_kg, green_score, notes, submitted_by)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (college_name, contact_person, contact_email, location,
              int(student_count or 0),
              float(solar or 0), float(wind or 0), float(grid or 0),
              float(diesel or 0), float(water or 0), float(waste or 0),
              score, notes, contact_person or 'Public'))
        db.commit()
        flash(f'Thank you! Energy data for {college_name} saved successfully. Green score: {score}/100', 'success')
        cursor.close()
        db.close()
        return redirect(url_for('colleges'))

    # GET - list all energy data sorted by green score
    cursor.execute("SELECT * FROM energy_data ORDER BY green_score DESC, created_at DESC")
    records = cursor.fetchall()

    # Aggregated stats
    cursor.execute("SELECT COUNT(*) AS c FROM energy_data")
    total_colleges = cursor.fetchone()['c']
    cursor.execute("SELECT IFNULL(SUM(solar_kwh + wind_kwh), 0) AS c FROM energy_data")
    total_renewable = float(cursor.fetchone()['c'])
    cursor.execute("SELECT IFNULL(AVG(green_score), 0) AS c FROM energy_data")
    avg_score = int(cursor.fetchone()['c'])
    cursor.execute("SELECT IFNULL(SUM(waste_recycled_kg), 0) AS c FROM energy_data")
    total_waste = float(cursor.fetchone()['c'])

    cursor.close()
    db.close()

    return render_template('colleges.html',
                           records=records,
                           total_colleges=total_colleges,
                           total_renewable=total_renewable,
                           avg_score=avg_score,
                           total_waste=total_waste)


@app.route('/survey', methods=['GET', 'POST'])
def survey():
    if request.method == 'POST':
        student_name = request.form.get('student_name', '').strip()
        institution_name = request.form.get('institution_name', '').strip()
        solar = request.form.get('solar_energy')
        energy = request.form.get('energy_saving')
        water = request.form.get('water_conservation')
        waste = request.form.get('waste_management')
        comments = request.form.get('comments', '').strip()

        if not student_name:
            flash('Please enter your name.', 'danger')
            return redirect(url_for('survey'))

        # Compute awareness level
        try:
            scores = [int(solar or 0), int(energy or 0), int(water or 0), int(waste or 0)]
            avg = sum(scores) / len(scores)
            if avg >= 4:
                level = 'High'
            elif avg >= 2.5:
                level = 'Medium'
            else:
                level = 'Low'
        except (ValueError, TypeError):
            level = 'Medium'

        db = get_db()
        cursor = db.cursor()
        cursor.execute("""
            INSERT INTO surveys (student_name, institution_name, solar_energy,
                                 energy_saving, water_conservation, waste_management,
                                 awareness_level, comments, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 'Completed')
        """, (student_name, institution_name, solar or 0, energy or 0,
              water or 0, waste or 0, level, comments))
        db.commit()
        cursor.close()
        db.close()

        flash('Thank you! Your survey has been submitted successfully.', 'success')
        return redirect(url_for('survey'))

    return render_template('survey.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').encode('utf-8')

        db = get_db()
        cursor = db.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()
        cursor.close()
        db.close()

        if user:
            stored_hash = user['password_hash']
            if isinstance(stored_hash, str):
                stored_hash = stored_hash.encode('utf-8')

            # Skip placeholder hash (for first run)
            if stored_hash == b'placeholder':
                flash('Please register the admin account first via /register', 'warning')
                return redirect(url_for('register'))

            if bcrypt.checkpw(password, stored_hash):
                session['user_id'] = user['id']
                session['username'] = user['username']
                session['role'] = user['role']
                flash(f"Welcome, {user['username']}!", 'success')
                return redirect(url_for('admin_dashboard'))

        flash('Invalid email or password.', 'danger')
        return render_template('login.html')

    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    """Register an admin/researcher (for first setup)."""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm = request.form.get('confirm_password', '')

        if not username or not email or not password:
            flash('All fields are required.', 'danger')
            return render_template('register.html')

        if len(password) < 6:
            flash('Password must be at least 6 characters.', 'danger')
            return render_template('register.html')

        if password != confirm:
            flash('Passwords do not match.', 'danger')
            return render_template('register.html')

        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        db = get_db()
        cursor = db.cursor(MySQLdb.cursors.DictCursor)
        try:
            cursor.execute("""
                INSERT INTO users (username, email, password_hash, role)
                VALUES (%s, %s, %s, 'admin')
            """, (username, email, password_hash))
            db.commit()
            flash('Account created! Please log in.', 'success')
            return redirect(url_for('login'))
        except MySQLdb.IntegrityError:
            db.rollback()
            flash('Email already exists.', 'danger')
            return render_template('register.html')
        finally:
            cursor.close()
            db.close()

    return render_template('register.html')


@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully.', 'info')
    return redirect(url_for('home'))


# ==================== ADMIN ROUTES ====================

@app.route('/admin')
@admin_required
def admin_dashboard():
    db = get_db()
    cursor = db.cursor(MySQLdb.cursors.DictCursor)

    # Stats
    cursor.execute("SELECT COUNT(*) AS c FROM institutions WHERE status='Active'")
    total_institutions = cursor.fetchone()['c']
    cursor.execute("SELECT COUNT(*) AS c FROM surveys")
    total_respondents = cursor.fetchone()['c']
    cursor.execute("SELECT AVG(green_score) AS avg_score FROM institutions")
    avg_row = cursor.fetchone()
    green_tech_adoption = int(avg_row['avg_score']) if avg_row['avg_score'] else 0
    cursor.execute("SELECT COUNT(*) AS c FROM surveys WHERE status='Pending'")
    pending_surveys = cursor.fetchone()['c']

    # Recent activity
    cursor.execute("SELECT * FROM activities ORDER BY created_at DESC LIMIT 4")
    activities = cursor.fetchall()

    # Green tech adoption
    cursor.execute("SELECT * FROM green_tech ORDER BY adoption_percent DESC")
    green_techs = cursor.fetchall()

    # Top 4 technologies
    top_techs = green_techs[:4]

    # Upcoming
    cursor.execute("SELECT * FROM upcoming ORDER BY event_date ASC LIMIT 3")
    upcoming_events = cursor.fetchall()

    # Quote of the day
    cursor.execute("SELECT * FROM quotes ORDER BY RAND() LIMIT 1")
    quote = cursor.fetchone()

    cursor.close()
    db.close()

    return render_template('admin/dashboard.html',
                           total_institutions=total_institutions,
                           total_respondents=total_respondents,
                           green_tech_adoption=green_tech_adoption,
                           pending_surveys=pending_surveys,
                           activities=activities,
                           green_techs=green_techs,
                           top_techs=top_techs,
                           upcoming_events=upcoming_events,
                           quote=quote)


@app.route('/admin/survey')
@admin_required
def admin_survey():
    db = get_db()
    cursor = db.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM surveys ORDER BY submitted_at DESC")
    surveys = cursor.fetchall()
    cursor.close()
    db.close()
    return render_template('admin/survey.html', surveys=surveys)


@app.route('/admin/reports')
@admin_required
def admin_reports():
    db = get_db()
    cursor = db.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM green_tech ORDER BY adoption_percent DESC")
    techs = cursor.fetchall()
    cursor.execute("SELECT * FROM institutions ORDER BY green_score DESC")
    institutions = cursor.fetchall()
    cursor.close()
    db.close()
    return render_template('admin/reports.html',
                           techs=techs,
                           institutions=institutions)


@app.route('/admin/institutions')
@admin_required
def admin_institutions():
    db = get_db()
    cursor = db.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM institutions ORDER BY name")
    institutions = cursor.fetchall()
    cursor.close()
    db.close()
    return render_template('admin/institutions.html', institutions=institutions)


@app.route('/admin/students')
@admin_required
def admin_students():
    db = get_db()
    cursor = db.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("""
        SELECT s.*, i.name AS institution_name
        FROM students s
        LEFT JOIN institutions i ON s.institution_id = i.id
        ORDER BY s.created_at DESC
    """)
    students = cursor.fetchall()
    cursor.close()
    db.close()
    return render_template('admin/students.html', students=students)


@app.route('/admin/greentech')
@admin_required
def admin_greentech():
    db = get_db()
    cursor = db.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM green_tech ORDER BY name")
    techs = cursor.fetchall()
    cursor.close()
    db.close()
    return render_template('admin/greentech.html', techs=techs)


@app.route('/admin/energy', methods=['GET', 'POST'])
@admin_required
def admin_energy():
    """Admin page: view, add, edit, delete college energy data."""
    db = get_db()
    cursor = db.cursor(MySQLdb.cursors.DictCursor)

    if request.method == 'POST':
        # Add or edit a record
        edit_id = request.form.get('edit_id')
        college_name = request.form.get('college_name', '').strip()
        contact_person = request.form.get('contact_person', '').strip()
        contact_email = request.form.get('contact_email', '').strip()
        location = request.form.get('location', '').strip()
        student_count = request.form.get('student_count', 0)
        solar = request.form.get('solar_kwh', 0)
        wind = request.form.get('wind_kwh', 0)
        grid = request.form.get('grid_kwh', 0)
        diesel = request.form.get('diesel_liters', 0)
        water = request.form.get('water_liters_per_day', 0)
        waste = request.form.get('waste_recycled_kg', 0)
        notes = request.form.get('notes', '').strip()

        if not college_name:
            flash('College name is required.', 'danger')
            return redirect(url_for('admin_energy'))

        score = compute_green_score(solar, wind, grid, diesel, water, waste)

        if edit_id:
            cursor.execute("""
                UPDATE energy_data SET
                    college_name=%s, contact_person=%s, contact_email=%s, location=%s,
                    student_count=%s, solar_kwh=%s, wind_kwh=%s, grid_kwh=%s,
                    diesel_liters=%s, water_liters_per_day=%s, waste_recycled_kg=%s,
                    green_score=%s, notes=%s
                WHERE id=%s
            """, (college_name, contact_person, contact_email, location,
                  int(student_count or 0), float(solar or 0), float(wind or 0),
                  float(grid or 0), float(diesel or 0), float(water or 0),
                  float(waste or 0), score, notes, edit_id))
            flash('Energy record updated.', 'success')
        else:
            cursor.execute("""
                INSERT INTO energy_data
                  (college_name, contact_person, contact_email, location, student_count,
                   solar_kwh, wind_kwh, grid_kwh, diesel_liters,
                   water_liters_per_day, waste_recycled_kg, green_score, notes, submitted_by)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (college_name, contact_person, contact_email, location,
                  int(student_count or 0), float(solar or 0), float(wind or 0),
                  float(grid or 0), float(diesel or 0), float(water or 0),
                  float(waste or 0), score, notes, session.get('username', 'admin')))
            flash(f'Energy record for {college_name} added. Green score: {score}/100', 'success')

        db.commit()
        cursor.close()
        db.close()
        return redirect(url_for('admin_energy'))

    # GET: list all records
    cursor.execute("SELECT * FROM energy_data ORDER BY green_score DESC, created_at DESC")
    records = cursor.fetchall()

    # Stats
    cursor.execute("SELECT COUNT(*) AS c, IFNULL(AVG(green_score),0) AS avg_s, IFNULL(SUM(solar_kwh+wind_kwh),0) AS ren FROM energy_data")
    s = cursor.fetchone()
    total_records = s['c']
    avg_score = int(s['avg_s'])
    total_renewable = float(s['ren'])

    edit_record = None
    edit_id = request.args.get('edit')
    if edit_id:
        cursor.execute("SELECT * FROM energy_data WHERE id = %s", (edit_id,))
        edit_record = cursor.fetchone()

    cursor.close()
    db.close()

    return render_template('admin/energy.html',
                           records=records,
                           total_records=total_records,
                           avg_score=avg_score,
                           total_renewable=total_renewable,
                           edit_record=edit_record)


@app.route('/admin/energy/delete/<int:record_id>', methods=['POST'])
@admin_required
def admin_energy_delete(record_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM energy_data WHERE id = %s", (record_id,))
    db.commit()
    cursor.close()
    db.close()
    flash('Energy record deleted.', 'info')
    return redirect(url_for('admin_energy'))


@app.route('/admin/settings')
@admin_required
def admin_settings():
    return render_template('admin/settings.html')


# ==================== CONTEXT PROCESSOR ====================
@app.context_processor
def inject_globals():
    return dict(current_year=datetime.now().year)


# ==================== ERROR HANDLERS ====================
@app.errorhandler(404)
def not_found(e):
    return render_template('404.html'), 404


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
