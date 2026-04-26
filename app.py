from flask import Flask, request, render_template, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
import numpy as np
from sklearn.ensemble import IsolationForest
import datetime
import random

app = Flask(__name__)
app.secret_key = "super-secret-key-2026"
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

# ====================== Helper to get real IP ======================
def get_client_ip():
    """Get real client IP even if behind proxy"""
    if request.headers.get('X-Forwarded-For'):
        return request.headers.get('X-Forwarded-For').split(',')[0].strip()
    elif request.headers.get('X-Real-IP'):
        return request.headers.get('X-Real-IP')
    else:
        return request.remote_addr

# Dummy Users
users = {
    "admin": generate_password_hash("1234"),
    "user": generate_password_hash("abcd")
}

login_history = []          # Now will store IP too
pending_otps = {}

# Isolation Forest Model
data = np.array([
    [9, 1, 1], [10, 1, 1], [11, 1, 1],
    [14, 1, 2], [15, 2, 2],
    [18, 1, 4], [19, 1, 4], [20, 1, 4],
    [2, 5, 6], [3, 6, 6], [23, 4, 5]
])

model = IsolationForest(contamination=0.25, random_state=42)
model.fit(data)

def is_suspicious(hour, attempts, day_of_week):
    test_data = np.array([[hour, attempts, day_of_week]])
    prediction = model.predict(test_data)
    score = model.decision_function(test_data)[0]
    return prediction[0] == -1, round(score, 3)

# ====================== ROUTES ======================

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        confirm = request.form.get("confirm_password", "")

        if password != confirm:
            flash("Passwords do not match!", "error")
            return redirect(url_for('register'))

        if username in users:
            flash("Username already taken!", "error")
            return redirect(url_for('register'))

        users[username] = generate_password_hash(password)
        flash("Account created successfully!", "success")
        return redirect(url_for('login'))

    return render_template("register.html")


@app.route("/", methods=["GET", "POST"])
@app.route("/login", methods=["GET", "POST"])
def login():
    message = ""
    show_otp = False

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        attempts = int(request.form.get("attempts", 1))
        entered_otp = request.form.get("otp")

        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        current_hour = datetime.datetime.now().hour
        current_day = datetime.datetime.now().weekday()
        client_ip = get_client_ip()

        # OTP Verification
        if entered_otp and username in pending_otps:
            if entered_otp == pending_otps[username]:
                session['username'] = username
                flash("✅ Login Successful!", "success")
                del pending_otps[username]
                login_history.append({
                    "username": username,
                    "time": current_time,
                    "attempts": attempts,
                    "status": "Success",
                    "ip": client_ip
                })
                return redirect(url_for('dashboard'))
            else:
                message = "❌ Invalid OTP!"
                show_otp = True

        # Normal Login
        elif username in users and check_password_hash(users[username], password):
            is_susp, score = is_suspicious(current_hour, attempts, current_day)

            if is_susp:
                otp = str(random.randint(100000, 999999))
                pending_otps[username] = otp
                message = f"⚠️ Suspicious Login (Score: {score}) - OTP Sent!"
                show_otp = True
                status = "Suspicious"
            else:
                session['username'] = username
                flash("✅ Login Successful!", "success")
                status = "Success"

            login_history.append({
                "username": username,
                "time": current_time,
                "attempts": attempts,
                "status": status,
                "ip": client_ip
            })

            if not show_otp:
                return redirect(url_for('dashboard'))
        else:
            message = "❌ Invalid Credentials!"
            login_history.append({
                "username": username,
                "time": current_time,
                "attempts": attempts,
                "status": "Error",
                "ip": client_ip
            })

    return render_template("index.html", 
                         message=message, 
                         history=login_history[-10:], 
                         show_otp=show_otp)


@app.route("/dashboard")
def dashboard():
    if 'username' not in session:
        flash("Please login first!", "error")
        return redirect(url_for("login"))
    
    return render_template("dashboard.html", history=login_history[-15:])


@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out successfully", "success")
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True)