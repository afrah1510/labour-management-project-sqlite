from flask import Flask, render_template, request, redirect, url_for, flash, session, g
from functools import wraps
import sqlite3
import config

app = Flask(__name__)
app.secret_key = "team2_data_dynamics_dbms"  # for session and flash

# ===================== DATABASE CONNECTION =====================

def get_db():
    """Get a connection to the SQLite database"""
    if 'db' not in g:
        g.db = sqlite3.connect(config.DATABASE_PATH)
        g.db.row_factory = sqlite3.Row  # access columns by name
    return g.db

@app.teardown_appcontext
def close_db(exception):
    """Close the database connection at the end of the request"""
    db = g.pop('db', None)
    if db is not None:
        db.close()

# ===================== LOGIN REQUIRED DECORATOR =====================
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "admin_id" not in session:
            flash("Please log in first.", "warning")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function

# ===================== INDEX =====================
@app.route("/")
def index():
    return render_template("index.html")

# ===================== ADMIN =====================
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        db = get_db()
        try:
            db.execute("INSERT INTO admin (username, password) VALUES (?, ?)", (username, password))
            db.commit()
            flash("Admin registered successfully!", "success")
            return redirect(url_for("login"))
        except sqlite3.Error as e:
            db.rollback()
            return render_template("error.html", message="Database error: " + str(e))
    return render_template("signup.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        db = get_db()
        admin = db.execute("SELECT * FROM admin WHERE username=? AND password=?", (username, password)).fetchone()

        if admin:
            session["admin_id"] = admin["admin_id"]
            session["username"] = admin["username"]
            flash("Login successful!", "success")
            return redirect(url_for("home"))
        else:
            flash("Invalid credentials", "danger")
    return render_template("login.html")


@app.route("/forgetpassword", methods=["GET", "POST"])
def forgetpassword():
    if request.method == "POST":
        username = request.form["username"]
        new_password = request.form["new_password"]

        db = get_db()
        try:
            db.execute("UPDATE admin SET password=? WHERE username=?", (new_password, username))
            db.commit()
            flash("Password updated successfully!", "success")
            return redirect(url_for("login"))
        except sqlite3.Error as e:
            db.rollback()
            return render_template("error.html", message="Database error: " + str(e))
    return render_template("forgetpassword.html")


@app.route("/logout")
@login_required
def logout():
    session.clear()
    flash("Logged out successfully!", "success")
    return redirect(url_for("index"))


@app.route("/home")
@login_required
def home():
    return render_template("home.html")

# ===================== LABOUR =====================
@app.route("/register_labour", methods=["GET", "POST"])
@login_required
def register_labour():
    if request.method == "POST":
        db = get_db()
        try:
            db.execute("""
                INSERT INTO labour (name, gender, age, contact, address, skill)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                request.form["name"],
                request.form["gender"],
                request.form["age"],
                request.form["contact"],
                request.form["address"],
                request.form["skill"]
            ))
            db.commit()
            flash("Labour registered successfully!", "success")
            return redirect(url_for("home"))
        except sqlite3.Error as e:
            db.rollback()
            return render_template("error.html", message="Error registering labour: " + str(e))
    return render_template("register_labour.html")


@app.route("/view_labour", methods=["GET", "POST"])
@login_required
def view_labour():
    db = get_db()
    searched = False
    labours = []
    try:
        if request.method == "POST":
            labour_id = request.form.get("labour_id")
            if labour_id:
                labours = db.execute("SELECT * FROM labour WHERE labour_id=?", (labour_id,)).fetchall()
            else:
                labours = db.execute("SELECT * FROM labour").fetchall()
            searched = True
        else:
            labours = db.execute("SELECT * FROM labour").fetchall()
    except sqlite3.Error as e:
        return render_template("error.html", message="Error loading labour data: " + str(e))
    return render_template("view_labour.html", labours=labours, searched=searched)

# ===================== PROJECT =====================
@app.route("/add_project", methods=["GET", "POST"])
@login_required
def add_project():
    if request.method == "POST":
        db = get_db()
        try:
            db.execute("""
                INSERT INTO project (name, location, start_date, end_date, status)
                VALUES (?, ?, ?, ?, ?)
            """, (
                request.form.get("name"),
                request.form.get("location"),
                request.form.get("start_date"),
                request.form.get("end_date"),
                request.form.get("status", "Ongoing")
            ))
            db.commit()
            flash("Project added successfully!", "success")
            return redirect(url_for("view_project"))
        except sqlite3.Error as e:
            db.rollback()
            return render_template("error.html", message="Error adding project: " + str(e))
    return render_template("add_project.html")


@app.route("/view_project", methods=["GET"])
@login_required
def view_project():
    db = get_db()
    project_id = request.args.get("project_id")
    try:
        if project_id:
            projects = db.execute("SELECT * FROM project WHERE project_id=?", (project_id,)).fetchall()
        else:
            projects = db.execute("SELECT * FROM project").fetchall()
    except sqlite3.Error as e:
        return render_template("error.html", message="Error loading projects: " + str(e))
    return render_template("view_project.html", projects=projects)

# ===================== ASSIGN PROJECT =====================
@app.route("/assign_project", methods=["GET", "POST"])
@login_required
def assign_project():
    db = get_db()
    try:
        labours = db.execute("SELECT labour_id, name FROM labour").fetchall()
        projects = db.execute("SELECT project_id, name FROM project").fetchall()

        if request.method == "POST":
            db.execute("""
                INSERT INTO assignment (labour_id, project_id, assigned_date)
                VALUES (?, ?, ?)
            """, (
                request.form["labour_id"],
                request.form["project_id"],
                request.form.get("assigned_date")
            ))
            db.commit()
            flash("Labour assigned to project!", "success")
            return redirect(url_for("assign_project"))

        assignments = db.execute("""
            SELECT a.assignment_id, l.name AS labour_name, p.name AS project_name, a.assigned_date
            FROM assignment a
            JOIN labour l ON a.labour_id = l.labour_id
            JOIN project p ON a.project_id = p.project_id
        """).fetchall()
    except sqlite3.Error as e:
        db.rollback()
        return render_template("error.html", message="Error assigning project: " + str(e))
    return render_template("assign_project.html", labours=labours, projects=projects, assignments=assignments)

# ===================== ATTENDANCE =====================
@app.route("/mark_attendance", methods=["GET", "POST"])
@login_required
def mark_attendance():
    db = get_db()
    labours = db.execute("SELECT labour_id, name FROM labour").fetchall()
    if request.method == "POST":
        try:
            db.execute("""
                INSERT INTO attendance (labour_id, date, status)
                VALUES (?, ?, ?)
            """, (
                request.form["labour_id"],
                request.form["date"],
                request.form["status"]
            ))
            db.commit()
            flash("Attendance marked!", "success")
            return redirect(url_for("mark_attendance"))
        except sqlite3.Error as e:
            db.rollback()
            return render_template("error.html", message="Error marking attendance: " + str(e))
    return render_template("mark_attendance.html", labours=labours)


@app.route("/view_attendance", methods=["GET", "POST"])
@login_required
def view_attendance():
    db = get_db()
    searched = False
    try:
        if request.method == "POST":
            labour_id = request.form.get("labour_id")
            attendances = db.execute("""
                SELECT a.attendance_id, l.name AS labour_name, a.date, a.status
                FROM attendance a
                JOIN labour l ON a.labour_id = l.labour_id
                WHERE a.labour_id = ?
            """, (labour_id,)).fetchall()
            searched = True
        else:
            attendances = db.execute("""
                SELECT a.attendance_id, l.name AS labour_name, a.date, a.status
                FROM attendance a
                JOIN labour l ON a.labour_id = l.labour_id
            """).fetchall()
    except sqlite3.Error as e:
        return render_template("error.html", message="Error loading attendance: " + str(e))
    return render_template("view_attendance.html", attendances=attendances, searched=searched)

# ===================== WAGES =====================
@app.route("/add_wages", methods=["GET", "POST"])
@login_required
def add_wages():
    db = get_db()
    labours = db.execute("SELECT labour_id, name FROM labour").fetchall()
    if request.method == "POST":
        try:
            db.execute("""
                INSERT INTO wages (labour_id, amount, payment_date)
                VALUES (?, ?, ?)
            """, (
                request.form["labour_id"],
                request.form["amount"],
                request.form.get("payment_date")
            ))
            db.commit()
            flash("Wages added successfully!", "success")
            return redirect(url_for("add_wages"))
        except sqlite3.Error as e:
            db.rollback()
            return render_template("error.html", message="Error adding wages: " + str(e))
    return render_template("add_wages.html", labours=labours)


@app.route("/view_wages", methods=["GET"])
@login_required
def view_wages():
    db = get_db()
    labour_id = request.args.get("labour_id")
    try:
        if labour_id:
            wages = db.execute("""
                SELECT w.wage_id, l.name AS labour_name, w.amount, w.payment_date
                FROM wages w
                JOIN labour l ON w.labour_id = l.labour_id
                WHERE w.labour_id = ?
            """, (labour_id,)).fetchall()
        else:
            wages = db.execute("""
                SELECT w.wage_id, l.name AS labour_name, w.amount, w.payment_date
                FROM wages w
                JOIN labour l ON w.labour_id = l.labour_id
            """).fetchall()
    except sqlite3.Error as e:
        return render_template("error.html", message="Error loading wages: " + str(e))
    return render_template("view_wages.html", wages=wages)

# ===================== GLOBAL ERROR HANDLER =====================
@app.errorhandler(Exception)
def handle_exception(e):
    return render_template("error.html", message="Unexpected error: " + str(e)), 500

# ===================== RUN APP =====================
if __name__ == "__main__":
    app.run(debug=True)