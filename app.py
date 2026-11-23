from flask import Flask, render_template
from database import get_db

app = Flask(__name__)

@app.route("/")
def dashboard():
    return render_template("dashboard.html")

@app.route("/companies")
def companies():
    conn = get_db()
    cursor = conn.cursor(dictionary = True)

    try:
        cursor.execute("SELECT * FROM companies")
        results = cursor.fetchall()
    finally:
        cursor.close()
        conn.close()
    return render_template("companies.html",companies=results)

if __name__ == "__main__":
    app.run(debug=True)