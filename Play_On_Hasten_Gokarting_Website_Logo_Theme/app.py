import os
import sqlite3
import secrets
from datetime import datetime
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, session, flash, abort

APP_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.environ.get("DATABASE_PATH", os.path.join(APP_DIR, "play_on.db"))
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "change-this-before-deploying-" + secrets.token_hex(8))
ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "change-me-before-deploying")
BUSINESS_PHONE = os.environ.get("BUSINESS_PHONE", "Add business phone number")
BUSINESS_EMAIL = os.environ.get("BUSINESS_EMAIL", "Add business email")
MAPS_URL = "https://www.google.com/maps/search/?api=1&query=SyNo.144%2C+1%2C+Gurramguda+Rd%2C+Sri+Laxmi+Nagar%2C+Teachers+Colony%2C+Rajyalaxmi+Nagar-2%2C+Gurram+Guda%2C+Hyderabad%2C+Telangana+501510"

def db():
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    return con

def init_db():
    with db() as con:
        con.execute("""
            CREATE TABLE IF NOT EXISTS bookings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                full_name TEXT NOT NULL,
                email TEXT NOT NULL,
                phone TEXT NOT NULL,
                booking_date TEXT NOT NULL,
                time_slot TEXT NOT NULL,
                package TEXT NOT NULL,
                participants INTEGER NOT NULL,
                notes TEXT,
                status TEXT NOT NULL DEFAULT 'Pending',
                created_at TEXT NOT NULL
            )
        """)
init_db()

@app.context_processor
def inject_globals():
    return {
        "business_phone": BUSINESS_PHONE,
        "business_email": BUSINESS_EMAIL,
        "maps_url": MAPS_URL,
        "year": datetime.now().year
    }

def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not session.get("admin_logged_in"):
            return redirect(url_for("admin_login", next=request.path))
        return fn(*args, **kwargs)
    return wrapper

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/book", methods=["POST"])
def book():
    fields = ["full_name", "email", "phone", "booking_date", "time_slot", "package", "participants"]
    data = {key: request.form.get(key, "").strip() for key in fields}
    notes = request.form.get("notes", "").strip()
    if any(not data[k] for k in fields):
        flash("Please complete all required fields.", "error")
        return redirect(url_for("home") + "#booking")
    try:
        participants = int(data["participants"])
        if participants < 1 or participants > 20:
            raise ValueError()
        datetime.strptime(data["booking_date"], "%Y-%m-%d")
    except ValueError:
        flash("Please check the date and participant count (1–20).", "error")
        return redirect(url_for("home") + "#booking")
    with db() as con:
        cur = con.execute("""
            INSERT INTO bookings (full_name,email,phone,booking_date,time_slot,package,participants,notes,status,created_at)
            VALUES (?,?,?,?,?,?,?,?,?,?)
        """, (data["full_name"], data["email"], data["phone"], data["booking_date"],
              data["time_slot"], data["package"], participants, notes, "Pending",
              datetime.now().isoformat(timespec="seconds")))
        booking_id = cur.lastrowid
    return render_template("booking_success.html", booking_id=booking_id, booking=data)

@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")
        if secrets.compare_digest(username, ADMIN_USERNAME) and secrets.compare_digest(password, ADMIN_PASSWORD):
            session["admin_logged_in"] = True
            return redirect(request.args.get("next") or url_for("admin_dashboard"))
        flash("Incorrect admin username or password.", "error")
    return render_template("admin_login.html")

@app.route("/admin/logout", methods=["POST"])
def admin_logout():
    session.clear()
    return redirect(url_for("home"))

@app.route("/admin")
@admin_required
def admin_dashboard():
    status_filter = request.args.get("status", "All")
    with db() as con:
        if status_filter in ("Pending", "Confirmed", "Cancelled"):
            rows = con.execute("SELECT * FROM bookings WHERE status=? ORDER BY created_at DESC", (status_filter,)).fetchall()
        else:
            rows = con.execute("SELECT * FROM bookings ORDER BY created_at DESC").fetchall()
        total = con.execute("SELECT COUNT(*) FROM bookings").fetchone()[0]
        pending = con.execute("SELECT COUNT(*) FROM bookings WHERE status='Pending'").fetchone()[0]
        confirmed = con.execute("SELECT COUNT(*) FROM bookings WHERE status='Confirmed'").fetchone()[0]
    return render_template("admin_dashboard.html", bookings=rows, status_filter=status_filter,
                           total=total, pending=pending, confirmed=confirmed)

@app.route("/admin/booking/<int:booking_id>/status", methods=["POST"])
@admin_required
def update_status(booking_id):
    status = request.form.get("status", "")
    if status not in ("Pending", "Confirmed", "Cancelled"):
        abort(400)
    with db() as con:
        con.execute("UPDATE bookings SET status=? WHERE id=?", (status, booking_id))
    flash(f"Booking #{booking_id} updated to {status}.", "success")
    return redirect(url_for("admin_dashboard"))

@app.route("/health")
def health():
    return {"status": "ok"}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "5000")), debug=False)
