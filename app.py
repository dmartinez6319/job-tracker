from flask import Flask, render_template, request, redirect, url_for
from database import get_db
from mysql.connector import IntegrityError
import json

app = Flask(__name__)


@app.route("/")
def dashboard():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("SELECT COUNT(*) AS total FROM jobs")
        total_jobs = cursor.fetchone()["total"]

        cursor.execute("SELECT COUNT(*) AS total FROM companies")
        total_companies = cursor.fetchone()["total"]

        cursor.execute("SELECT COUNT(*) AS total FROM applications")
        total_applications = cursor.fetchone()["total"]

        cursor.execute("SELECT COUNT(*) AS total FROM contacts")
        total_contacts = cursor.fetchone()["total"]

        cursor.execute("SELECT COUNT(*) AS total FROM applications WHERE status = 'Applied'")
        total_applied = cursor.fetchone()["total"]

        cursor.execute("SELECT COUNT(*) AS total FROM applications WHERE status = 'Interview'")
        total_interviews = cursor.fetchone()["total"]

        cursor.execute("SELECT COUNT(*) AS total FROM applications WHERE status = 'Offer'")
        total_offers = cursor.fetchone()["total"]

        cursor.execute("SELECT COUNT(*) AS total FROM applications WHERE status = 'Rejected'")
        total_rejected = cursor.fetchone()["total"]

    finally:
        cursor.close()
        conn.close()

    return render_template(
        "dashboard.html",
        total_jobs=total_jobs,
        total_companies=total_companies,
        total_applications=total_applications,
        total_contacts=total_contacts,
        total_applied=total_applied,
        total_interviews=total_interviews,
        total_offers=total_offers,
        total_rejected=total_rejected
    )


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



@app.route("/jobs/<int:id>/delete")
def delete_job(id):
    conn = get_db()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "DELETE FROM jobs WHERE job_id = %s",
            (id,)
        )
        conn.commit()
    except IntegrityError:
        conn.rollback()
        return "Cannot delete a job with related applications.", 409
    except Exception:
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()

    return redirect(url_for("jobs"))


def get_job_types():
    conn = get_db()
    cursor = conn.cursor()

    try:
        cursor.execute("SHOW COLUMNS FROM jobs LIKE 'job_type'")
        column = cursor.fetchone()

        if not column:
            raise ValueError("jobs.job_type column not found")

        enum_values = column[1]
        return [
            value.strip("'")
            for value in enum_values[5:-1].split(",")
        ]
    finally:
        cursor.close()
        conn.close()


def get_job_form():
    company_id = request.form.get("company_id", type=int)
    job_title = request.form.get("job_title", "").strip()
    job_type = request.form.get("job_type", "").strip()
    salary_min = request.form.get("salary_min", "").strip()
    salary_max = request.form.get("salary_max", "").strip()
    job_url = request.form.get("job_url", "").strip()
    date_posted = request.form.get("date_posted", "").strip()
    requirements = request.form.get("requirements", "")

    if not company_id:
        raise ValueError("Please select a company")

    if not job_title:
        raise ValueError("Job title is required")

    skills = [
        skill.strip()
        for skill in requirements.split(",")
        if skill.strip()
    ]

    return (
        company_id,
        job_title,
        job_type or None,
        salary_min or None,
        salary_max or None,
        job_url or None,
        date_posted or None,
        json.dumps(skills)
    )

@app.route("/jobs")
def jobs():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("SELECT company_id, company_name FROM companies ORDER BY company_name")
        companies = cursor.fetchall()

        cursor.execute("SELECT * FROM jobs ORDER BY job_id DESC")
        results = cursor.fetchall()
    finally:
        cursor.close()
        conn.close()

    for job in results:
        requirements = job["requirements"]

        if isinstance(requirements, str):
            requirements = json.loads(requirements)

        if isinstance(requirements, list):
            job["requirements_text"] = ", ".join(requirements)
        else:
            job["requirements_text"] = ""

    return render_template(
        "jobs.html",
        jobs=results,
        companies=companies,
        job_types=get_job_types()
    )


@app.route("/jobs/new", methods=["POST"])
def add_job():
    try:
        values = get_job_form()
    except (ValueError, TypeError) as e:
        print(e)
        return "Invalid job information", 400


    conn = get_db()
    cursor = conn.cursor()

    try:
        cursor.execute("""


            INSERT INTO jobs
            (company_id, job_title, job_type, salary_min,

             salary_max, job_url, date_posted, requirements)

            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)


        """, values)

        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()

    return redirect(url_for("jobs"))


@app.route("/jobs/<int:id>/edit", methods=["POST"])
def edit_job(id):
    try:
        values = get_job_form()
    except (ValueError, TypeError):
        return "Invalid job information", 400

    conn = get_db()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            UPDATE jobs
            SET company_id = %s,
                job_title = %s,
                job_type = %s,
                salary_min = %s,
                salary_max = %s,
                job_url = %s,
                date_posted = %s,
                requirements = %s
            WHERE job_id = %s
        """, values + (id,))

        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()

    return redirect(url_for("jobs"))


def get_contact_form():
    company_id = request.form.get("company_id", type=int)
    contact_name = request.form.get("contact_name", "").strip()
    title = request.form.get("title", "").strip()
    email = request.form.get("email", "").strip()
    phone = request.form.get("phone", "").strip()
    linkedin_url = request.form.get("linkedin_url", "").strip()
    notes = request.form.get("notes", "").strip()

    if not contact_name:
        raise ValueError("Contact name is required")

    return (
        company_id,
        contact_name,
        title or None,
        email or None,
        phone or None,
        linkedin_url or None,
        notes or None
    )


@app.route("/contacts")
def contacts():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute(
            "SELECT company_id, company_name FROM companies ORDER BY company_name"
        )
        companies = cursor.fetchall()

        cursor.execute("SELECT * FROM contacts ORDER BY contact_id DESC")
        results = cursor.fetchall()
    finally:
        cursor.close()
        conn.close()

    return render_template(
        "contacts.html",
        contacts=results,
        companies=companies
    )


@app.route("/contacts/new", methods=["POST"])
def add_contact():
    try:
        values = get_contact_form()
    except (ValueError, TypeError) as e:
        return str(e), 400

    conn = get_db()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO contacts
            (company_id, contact_name, title, email,
             phone, linkedin_url, notes)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, values)

        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()

    return redirect(url_for("contacts"))


@app.route("/contacts/<int:id>/edit", methods=["POST"])
def edit_contact(id):
    try:
        values = get_contact_form()
    except (ValueError, TypeError) as e:
        return str(e), 400

    conn = get_db()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            UPDATE contacts
            SET company_id = %s,
                contact_name = %s,
                title = %s,
                email = %s,
                phone = %s,
                linkedin_url = %s,
                notes = %s
            WHERE contact_id = %s
        """, values + (id,))

        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()

    return redirect(url_for("contacts"))


@app.route("/contacts/<int:id>/delete", methods=["GET"])
def delete_contact(id):
    conn = get_db()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "DELETE FROM contacts WHERE contact_id = %s",
            (id,)
        )
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()

    return redirect(url_for("contacts"))


def get_application_form():
    job_id = request.form.get("job_id", type=int)
    application_date = request.form.get("application_date", "").strip()
    status = request.form.get("status", "").strip()
    resume_version = request.form.get("resume_version", "").strip()
    cover_letter_sent = 1 if request.form.get("cover_letter_sent") else 0

    interview_date = request.form.get("interview_date", "").strip()
    interviewer = request.form.get("interviewer", "").strip()
    interview_notes = request.form.get("interview_notes", "").strip()

    if not job_id:
        raise ValueError("Please select a job")

    if not application_date:
        raise ValueError("Application date is required")

    statuses = [
        "Applied",
        "Screening",
        "Interview",
        "Offer",
        "Rejected",
        "Withdrawn"
    ]

    if status and status not in statuses:
        raise ValueError("Invalid application status")

    interview_data = {
        "interview_date": interview_date,
        "interviewer": interviewer,
        "notes": interview_notes
    }

    return (
        job_id,
        application_date,
        status or None,
        resume_version or None,
        cover_letter_sent,
        json.dumps(interview_data)
    )


@app.route("/applications")
def applications():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT jobs.job_id, jobs.job_title, companies.company_name
            FROM jobs
            LEFT JOIN companies ON jobs.company_id = companies.company_id
            ORDER BY jobs.job_title
        """)
        jobs = cursor.fetchall()

        cursor.execute("""
            SELECT *
            FROM applications
            ORDER BY application_id DESC
        """)
        results = cursor.fetchall()
    finally:
        cursor.close()
        conn.close()

    for application in results:
        data = application["interview_data"]

        if isinstance(data, str):
            data = json.loads(data)

        if not isinstance(data, dict):
            data = {}

        application["interview_date"] = data.get("interview_date", "")
        application["interviewer"] = data.get("interviewer", "")
        application["interview_notes"] = data.get("notes", "")

    return render_template(
        "applications.html",
        applications=results,
        jobs=jobs,
        statuses=[
            "Applied",
            "Screening",
            "Interview",
            "Offer",
            "Rejected",
            "Withdrawn"
        ]
    )


@app.route("/applications/new", methods=["POST"])
def add_application():
    try:
        values = get_application_form()
    except (ValueError, TypeError) as e:
        return str(e), 400

    conn = get_db()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO applications
            (job_id, application_date, status,
             resume_version, cover_letter_sent, interview_data)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, values)

        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()

    return redirect(url_for("applications"))


@app.route("/applications/<int:id>/edit", methods=["POST"])
def edit_application(id):
    try:
        values = get_application_form()
    except (ValueError, TypeError) as e:
        return str(e), 400

    conn = get_db()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            UPDATE applications
            SET job_id = %s,
                application_date = %s,
                status = %s,
                resume_version = %s,
                cover_letter_sent = %s,
                interview_data = %s
            WHERE application_id = %s
        """, values + (id,))

        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()

    return redirect(url_for("applications"))


@app.route("/applications/<int:id>/delete", methods=["GET"])
def delete_application(id):
    conn = get_db()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "DELETE FROM applications WHERE application_id = %s",
            (id,)
        )
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()

    return redirect(url_for("applications"))

@app.route("/job-match", methods=["GET", "POST"])
def job_match():
    matches = []
    skills = ""

    if request.method == "POST":
        skills = request.form.get("skills", "")
        user_skills = [skill.strip().lower() for skill in skills.split(",")]

        conn = get_db()
        cursor = conn.cursor(dictionary=True)

        try:
            cursor.execute("""
                SELECT jobs.*, companies.company_name
                FROM jobs
                LEFT JOIN companies ON jobs.company_id = companies.company_id
            """)
            matches = cursor.fetchall()
        finally:
            cursor.close()
            conn.close()

        for job in matches:
            required = job["requirements"] or []

            if isinstance(required, str):
                required = json.loads(required)

            if not isinstance(required, list):
                required = []

            matching = [
                skill for skill in required
                if isinstance(skill, str) and skill.strip().lower() in user_skills
            ]

            job["percentage"] = round(len(matching) / len(required) * 100) if required else 0
            job["required_skills"] = ", ".join(required)
            job["matching_skills"] = ", ".join(matching) or "None"

        matches.sort(key=lambda job: job["percentage"], reverse=True)

    return render_template("job_match.html", matches=matches, skills=skills)

if __name__ == "__main__":
    app.run(debug=True)