"""Seed a demo user, profile, companies + public sponsorship records, and applications.

Run:  python -m app.seed
Login: demo@careeros.app / demo1234
"""
from datetime import date, timedelta
from passlib.context import CryptContext
from app.database import SessionLocal, init_db
from app import models

pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")


def run():
    init_db()
    db = SessionLocal()
    if db.query(models.User).filter_by(email="demo@careeros.app").first():
        print("Already seeded."); return

    user = models.User(email="demo@careeros.app", name="Aisha Rahman",
                       hashed_password=pwd.hash("demo1234"))
    db.add(user); db.commit(); db.refresh(user)

    db.add(models.Profile(
        user_id=user.id, degree="M.S.", major="Computer Science", minor="Statistics",
        graduation_date=date(2026, 5, 15), gpa=3.8,
        skills=["Python", "SQL", "Machine Learning", "React", "AWS", "Tableau"],
        resume_text=("Aisha Rahman — M.S. Computer Science.\nEXPERIENCE\n"
                     "Data Science Intern, Acme Analytics: built churn model improving "
                     "retention 12%; automated ETL with Python and Airflow.\n"
                     "Research Assistant: published NLP paper; led 3-person team.\n"
                     "SKILLS: Python, SQL, ML, React, AWS, Tableau."),
        resume_filename="aisha_resume.pdf", linkedin_url="https://linkedin.com/in/aisha",
        preferred_locations=["New York, NY", "Remote"],
        desired_industries=["Technology", "Finance"],
        career_goals="Data Scientist / ML Engineer at a sponsorship-friendly company.",
        visa_status="F-1", opt_eligible=True, stem_opt_eligible=True,
        requires_sponsorship=True, salary_min=95000, salary_max=140000))

    companies = [
        ("Google", "Technology", "Mountain View, CA", "10,000+", True, 90, 1200),
        ("Stripe", "Fintech", "San Francisco, CA", "5,000-10,000", True, 75, 180),
        ("Acme Defense", "Defense", "Arlington, VA", "1,000-5,000", True, 10, 0),
    ]
    import re
    for name, ind, hq, size, ev, score, h1b in companies:
        c = models.Company(name=name, normalized_name=re.sub(r"[^a-z0-9]", "", name.lower()),
                           industry=ind, headquarters=hq, size=size, e_verify=ev,
                           sponsorship_score=score)
        db.add(c); db.commit(); db.refresh(c)
        if h1b:
            db.add(models.SponsorshipRecord(company_id=c.id, record_type="h1b",
                   fiscal_year=2025, count=h1b, job_title="Software Engineer"))
    db.commit()

    today = date.today()
    for comp, title, status, days in [
        ("Google", "Data Scientist", "Applied", -10),
        ("Stripe", "ML Engineer", "Interview", -20),
        ("Notion", "Software Engineer", "Saved", -2),
    ]:
        db.add(models.Application(
            user_id=user.id, company=comp, job_title=title, source="paste", status=status,
            date_found=today + timedelta(days=days),
            date_applied=today + timedelta(days=days + 1) if status != "Saved" else None,
            interview_date=today + timedelta(days=5) if status == "Interview" else None))
    db.add(models.ResumeVersion(user_id=user.id, label="Tailored — Google",
           content="Optimized resume...", ats_score=88, recruiter_score=84,
           ats_score_before=70))
    db.commit()
    print("Seeded demo@careeros.app / demo1234")


if __name__ == "__main__":
    run()
