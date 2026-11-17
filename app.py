import pymysql
pymysql.install_as_MySQLdb()

from flask import Flask, render_template, request, redirect, url_for
from flask_mysqldb import MySQL
from config import Config

app = Flask(__name__, static_folder="static")

# MySQL Configuration
app.config.from_object(Config)
mysql = MySQL(app)

# ---------------- HOME ----------------

@app.route("/")
def home():
    return redirect(url_for("login"))

# ---------------- LOGIN ----------------

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        if username == "admin" and password == "1234":
            return redirect(url_for("dashboard"))
        else:
            return "Invalid Username or Password"

    return render_template("login.html")


# ---------------- REGISTER ----------------

@app.route("/register")
def register():
    return render_template("register.html")



# ---------------- DASHBOARD ----------------

@app.route("/dashboard")
def dashboard():

    cur = mysql.connection.cursor()

    # Total Doctors
    cur.execute("SELECT COUNT(*) FROM doctors")
    doctor_count = cur.fetchone()[0]

    # Total Patients from appointments
    cur.execute("SELECT COUNT(DISTINCT patient_name) FROM appointments")
    patient_count = cur.fetchone()[0]

    # Total Appointments
    cur.execute("SELECT COUNT(*) FROM appointments")
    appointment_count = cur.fetchone()[0]

    # Revenue
    cur.execute("SELECT SUM(amount) FROM billing")
    revenue = cur.fetchone()[0]

    if revenue is None:
        revenue = 0

    # Recent Appointments
    cur.execute("SELECT * FROM appointments ORDER BY id DESC LIMIT 5")
    recent_appointments = cur.fetchall()

    cur.close()

    return render_template(
        "dashboard.html",
        doctor_count=doctor_count,
        patient_count=patient_count,
        appointment_count=appointment_count,
        revenue=revenue,
        recent_appointments=recent_appointments
    )


# ---------------- ADMIN ----------------

@app.route("/admin", methods=["GET", "POST"])
def admin():

    cur = mysql.connection.cursor()

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        phone = request.form["phone"]

        cur.execute(
            "INSERT INTO admin(name,email,phone) VALUES(%s,%s,%s)",
            (name, email, phone)
        )

        mysql.connection.commit()

        cur.close()

        return redirect(url_for("admin"))


    cur.execute("SELECT * FROM admin ORDER BY id DESC")

    admins = cur.fetchall()

    cur.close()

    return render_template("admin.html", admins=admins)


# ---------------- DOCTORS ----------------

@app.route("/doctors", methods=["GET", "POST"])
def doctors():

    if request.method == "POST":

        name = request.form["name"]
        specialization = request.form["specialization"]
        email = request.form["email"]
        phone = request.form["phone"]

        cur = mysql.connection.cursor()

        cur.execute(
            "INSERT INTO doctors(name,specialization,email,phone) VALUES(%s,%s,%s,%s)",
            (name, specialization, email, phone)
        )

        mysql.connection.commit()

        cur.close()

        return redirect(url_for("doctors"))

    cur = mysql.connection.cursor()

    cur.execute("SELECT * FROM doctors")

    doctors = cur.fetchall()

    cur.close()

    return render_template("doctors.html", doctors=doctors)


# ---------------- APPOINTMENTS ----------------

@app.route("/appointments", methods=["GET","POST"])
def appointments():

    cur = mysql.connection.cursor()

    if request.method == "POST":

        patient_name = request.form["patient_name"]
        doctor_name = request.form["doctor_name"]
        date = request.form["date"]
        time = request.form["time"]
        status = request.form["status"]

        cur.execute(
            "INSERT INTO appointments(patient_name, doctor_name, date, time, status) VALUES(%s,%s,%s,%s,%s)",
            (patient_name, doctor_name, date, time, status)
        )

        mysql.connection.commit()

        cur.close()

        return redirect(url_for("appointments"))

    cur.execute("SELECT * FROM appointments ORDER BY id DESC")

    data = cur.fetchall()

    cur.close()

    return render_template("appointments.html", appointments=data)
    cur.execute("SELECT * FROM appointments")
    data = cur.fetchall()

    cur.close()

    return render_template("appointments.html", appointments=data)


# ---------------- BILLING ----------------

@app.route("/billing", methods=["GET", "POST"])
def billing():

    cur = mysql.connection.cursor()

    if request.method == "POST":

        patient_name = request.form["patient_name"]
        amount = request.form["amount"]
        payment_status = request.form["payment_status"]
        date = request.form["date"]

        cur.execute(
            "INSERT INTO billing(patient_name, amount, payment_status, date) VALUES(%s,%s,%s,%s)",
            (patient_name, amount, payment_status, date)
        )

        mysql.connection.commit()

        cur.close()

        return redirect(url_for("billing"))


    cur.execute("SELECT * FROM billing ORDER BY id DESC")

    bills = cur.fetchall()

    cur.close()

    return render_template("billing.html", bills=bills)


# ---------------- RECORDS ----------------

@app.route("/records", methods=["GET", "POST"])
def records():

    cur = mysql.connection.cursor()

    if request.method == "POST":

        patient_name = request.form["patient_name"]
        diagnosis = request.form["diagnosis"]
        treatment = request.form["treatment"]
        date = request.form["date"]

        cur.execute(
            "INSERT INTO medical_records(patient_name, diagnosis, treatment, date) VALUES(%s,%s,%s,%s)",
            (patient_name, diagnosis, treatment, date)
        )

        mysql.connection.commit()

        cur.close()

        return redirect(url_for("records"))


    cur.execute("SELECT * FROM medical_records ORDER BY id DESC")

    records = cur.fetchall()

    cur.close()

    return render_template("records.html", records=records)

# ---------------- DATABASE TEST ----------------

@app.route("/testdb")
def testdb():

    cur = mysql.connection.cursor()

    cur.execute("SELECT DATABASE();")

    data = cur.fetchone()

    cur.close()

    return f"Connected to Database : {data[0]}"


# ---------------- RUN APP ----------------
# ---------------- DELETE DOCTOR ----------------

@app.route("/delete_doctor/<int:id>")
def delete_doctor(id):
    cur = mysql.connection.cursor()

    cur.execute(
        "DELETE FROM doctors WHERE id=%s",
        (id,)
    )

    mysql.connection.commit()
    cur.close()

    return redirect(url_for("doctors"))


# ---------------- EDIT DOCTOR ----------------

@app.route("/edit_doctor/<int:id>", methods=["GET", "POST"])
def edit_doctor(id):

    cur = mysql.connection.cursor()

    if request.method == "POST":

        name = request.form["name"]
        specialization = request.form["specialization"]
        email = request.form["email"]
        phone = request.form["phone"]

        cur.execute(
            "UPDATE doctors SET name=%s, specialization=%s, email=%s, phone=%s WHERE id=%s",
            (name, specialization, email, phone, id)
        )

        mysql.connection.commit()
        cur.close()

        return redirect(url_for("doctors"))

    cur.execute(
        "SELECT * FROM doctors WHERE id=%s",
        (id,)
    )

    doctor = cur.fetchone()

    cur.close()

    return render_template("edit_doctor.html", doctor=doctor)


# ---------------- RUN APP ----------------

if __name__ == "__main__":
    app.run(debug=True)