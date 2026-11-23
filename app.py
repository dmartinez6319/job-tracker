from flask import Flask, render_template, request, redirect, url_for
from database import get_db
from mysql.connector import IntegrityError

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

@app.route("/companies/new", methods=["POST"])
def add_company():
    name = request.form.get("company_name")
    industry = request.form.get("industry")
    website = request.form.get("website")
    city = request.form.get("city")
    state = request.form.get("state")
    notes = request.form.get("notes")

    if not name or not name.strip():
        return "Company name is required", 400

    conn = get_db()
    cursor = conn.cursor()

    try:
        cursor.execute("""

            INSERT INTO companies
            (company_name, industry, website, city, state, notes)
            VALUES (%s, %s, %s, %s, %s, %s)

        """, (name.strip(), industry, website, city, state, notes))

        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()

    return redirect(url_for("companies"))

    name = request.form.get("company_name")
    industry = request.form.get("industry")
    website = request.form.get("website")
    city = request.form.get("city")
    state = request.form.get("state")
    notes = request.form.get("notes")

    if not name or not name.strip():
        return "Company name is required", 400

    conn = get_db()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO companies
            (company_name, industry, website, city, state, notes)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (name.strip(), industry, website, city, state, notes))

        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()

    return redirect(url_for("companies"))

@app.route("/companies/<int:id>/edit", methods=["POST"])
def edit_company(id):
    name = request.form.get("company_name")
    industry = request.form.get("industry")
    website = request.form.get("website")
    city = request.form.get("city")
    state = request.form.get("state")
    notes = request.form.get("notes")

    if not name or not name.strip():
        return "Company name is required", 400

    conn = get_db()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            UPDATE companies
            SET company_name = %s,
                industry = %s,
                website = %s,
                city = %s,
                state = %s,
                notes = %s
            WHERE company_id = %s
        """, (name.strip(), industry, website, city, state, notes, id))

        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()

    return redirect(url_for("companies"))


@app.route("/companies/<int:id>/delete")
def delete_company(id):
    conn = get_db()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "DELETE FROM companies WHERE company_id = %s",
            (id,)
        )

        conn.commit()
    except IntegrityError:
        conn.rollback()
        return "Cannot delete a company that has related jobs or contacts.", 409
    except Exception:
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()

    return redirect(url_for("companies"))


if __name__ == "__main__":
    app.run(debug=True)