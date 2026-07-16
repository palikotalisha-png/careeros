"""SQLAlchemy ORM models — the complete LaunchPath schema."""
from __future__ import annotations
import uuid
from datetime import datetime, date
from sqlalchemy import (
    String, Integer, Float, Boolean, Text, Date, DateTime, ForeignKey, JSON, func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


def _uuid() -> str:
    return str(uuid.uuid4())


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )


# ─────────────────────────────── Users & profile ───────────────────────────────
class User(Base, TimestampMixin):
    __tablename__ = "users"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    email: Mapped[str] = mapped_column(String, unique=True, index=True)
    name: Mapped[str] = mapped_column(String, default="")
    hashed_password: Mapped[str | None] = mapped_column(String, nullable=True)
    auth_provider: Mapped[str] = mapped_column(String, default="credentials")

    profile: Mapped["Profile"] = relationship(back_populates="user", uselist=False)
    applications: Mapped[list["Application"]] = relationship(back_populates="user")
    events: Mapped[list["UserEvent"]] = relationship(back_populates="user")
    notifications: Mapped[list["Notification"]] = relationship(back_populates="user")


class Profile(Base, TimestampMixin):
    __tablename__ = "profiles"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), unique=True)

    degree: Mapped[str] = mapped_column(String, default="")
    major: Mapped[str] = mapped_column(String, default="")
    minor: Mapped[str] = mapped_column(String, default="")
    graduation_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    gpa: Mapped[float | None] = mapped_column(Float, nullable=True)
    skills: Mapped[list] = mapped_column(JSON, default=list)
    resume_text: Mapped[str] = mapped_column(Text, default="")
    resume_filename: Mapped[str] = mapped_column(String, default="")
    linkedin_url: Mapped[str] = mapped_column(String, default="")

    preferred_locations: Mapped[list] = mapped_column(JSON, default=list)
    desired_industries: Mapped[list] = mapped_column(JSON, default=list)
    career_goals: Mapped[str] = mapped_column(Text, default="")

    # Visa / work authorization
    visa_status: Mapped[str] = mapped_column(String, default="")          # F-1, J-1, ...
    opt_eligible: Mapped[bool] = mapped_column(Boolean, default=False)
    stem_opt_eligible: Mapped[bool] = mapped_column(Boolean, default=False)
    requires_sponsorship: Mapped[bool] = mapped_column(Boolean, default=True)

    salary_min: Mapped[int | None] = mapped_column(Integer, nullable=True)
    salary_max: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Learned preference vector (updated from UserEvent stream)
    preference_vector: Mapped[dict] = mapped_column(JSON, default=dict)

    user: Mapped[User] = relationship(back_populates="profile")


# ─────────────────────────────── Companies ───────────────────────────────
class Company(Base, TimestampMixin):
    __tablename__ = "companies"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    name: Mapped[str] = mapped_column(String, index=True)
    normalized_name: Mapped[str] = mapped_column(String, index=True)
    website: Mapped[str] = mapped_column(String, default="")
    industry: Mapped[str] = mapped_column(String, default="")
    headquarters: Mapped[str] = mapped_column(String, default="")
    size: Mapped[str] = mapped_column(String, default="")
    revenue: Mapped[str] = mapped_column(String, default="")
    description: Mapped[str] = mapped_column(Text, default="")

    research: Mapped[dict] = mapped_column(JSON, default=dict)        # cached research blob
    e_verify: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    sponsorship_score: Mapped[int | None] = mapped_column(Integer, nullable=True)

    jobs: Mapped[list["Job"]] = relationship(back_populates="company")
    sponsorship_records: Mapped[list["SponsorshipRecord"]] = relationship(
        back_populates="company"
    )


class SponsorshipRecord(Base):
    """Public H-1B / E-Verify / PERM disclosure rows, keyed to a company."""
    __tablename__ = "sponsorship_records"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    company_id: Mapped[str] = mapped_column(ForeignKey("companies.id"))
    record_type: Mapped[str] = mapped_column(String)   # h1b | perm | e_verify
    fiscal_year: Mapped[int | None] = mapped_column(Integer, nullable=True)
    count: Mapped[int] = mapped_column(Integer, default=0)
    job_title: Mapped[str] = mapped_column(String, default="")
    detail: Mapped[dict] = mapped_column(JSON, default=dict)

    company: Mapped[Company] = relationship(back_populates="sponsorship_records")


# ─────────────────────────────── Jobs & matches ───────────────────────────────
class Job(Base, TimestampMixin):
    __tablename__ = "jobs"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    company_id: Mapped[str | None] = mapped_column(ForeignKey("companies.id"), nullable=True)

    title: Mapped[str] = mapped_column(String, index=True)
    company_name: Mapped[str] = mapped_column(String, index=True)
    location: Mapped[str] = mapped_column(String, default="")
    description: Mapped[str] = mapped_column(Text, default="")
    salary: Mapped[str] = mapped_column(String, default="")
    source: Mapped[str] = mapped_column(String, default="")        # adapter id
    apply_url: Mapped[str] = mapped_column(String, default="")
    date_posted: Mapped[date | None] = mapped_column(Date, nullable=True)
    deadline: Mapped[date | None] = mapped_column(Date, nullable=True)
    e_verify: Mapped[bool | None] = mapped_column(Boolean, nullable=True)

    dedup_hash: Mapped[str] = mapped_column(String, unique=True, index=True)

    company: Mapped[Company | None] = relationship(back_populates="jobs")
    matches: Mapped[list["JobMatch"]] = relationship(back_populates="job")


class JobMatch(Base, TimestampMixin):
    """AI match scoring of a job for a specific user."""
    __tablename__ = "job_matches"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"))
    job_id: Mapped[str] = mapped_column(ForeignKey("jobs.id"))

    match_score: Mapped[int] = mapped_column(Integer, default=0)        # 0-100
    sponsorship_score: Mapped[int] = mapped_column(Integer, default=0)  # 0-100
    intl_compat_score: Mapped[int] = mapped_column(Integer, default=0)  # 0-100
    sponsorship_probability: Mapped[str] = mapped_column(String, default="Low")

    strengths: Mapped[list] = mapped_column(JSON, default=list)
    risks: Mapped[list] = mapped_column(JSON, default=list)
    missing_skills: Mapped[list] = mapped_column(JSON, default=list)
    missing_qualifications: Mapped[list] = mapped_column(JSON, default=list)
    recommended_actions: Mapped[list] = mapped_column(JSON, default=list)
    risk_flags: Mapped[list] = mapped_column(JSON, default=list)
    explanation: Mapped[str] = mapped_column(Text, default="")

    job: Mapped[Job] = relationship(back_populates="matches")


# ─────────────────────────────── Application tracker ───────────────────────────────
class Application(Base, TimestampMixin):
    __tablename__ = "applications"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"))
    job_id: Mapped[str | None] = mapped_column(ForeignKey("jobs.id"), nullable=True)

    company: Mapped[str] = mapped_column(String, default="")
    job_title: Mapped[str] = mapped_column(String, default="")
    location: Mapped[str] = mapped_column(String, default="")
    source: Mapped[str] = mapped_column(String, default="")
    status: Mapped[str] = mapped_column(String, default="Saved")
    # Saved | Applying | Applied | Interview | Follow-up | Rejected | Offer | Accepted

    date_found: Mapped[date | None] = mapped_column(Date, nullable=True)
    date_applied: Mapped[date | None] = mapped_column(Date, nullable=True)
    interview_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    follow_up_date: Mapped[date | None] = mapped_column(Date, nullable=True)

    recruiter: Mapped[str] = mapped_column(String, default="")
    recruiter_linkedin: Mapped[str] = mapped_column(String, default="")
    referral_status: Mapped[str] = mapped_column(String, default="None")
    # None | Requested | Received | Declined
    deadline: Mapped[date | None] = mapped_column(Date, nullable=True)
    salary: Mapped[str] = mapped_column(String, default="")
    work_auth_notes: Mapped[str] = mapped_column(String, default="")
    sponsorship_available: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    e_verify: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    notes: Mapped[str] = mapped_column(Text, default="")
    resume_version_id: Mapped[str | None] = mapped_column(
        ForeignKey("resume_versions.id"), nullable=True
    )
    cover_letter_id: Mapped[str | None] = mapped_column(
        ForeignKey("cover_letters.id"), nullable=True
    )

    user: Mapped[User] = relationship(back_populates="applications")


# ─────────────────────────────── Resume & cover letters ───────────────────────────────
class ResumeVersion(Base, TimestampMixin):
    __tablename__ = "resume_versions"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"))
    job_id: Mapped[str | None] = mapped_column(ForeignKey("jobs.id"), nullable=True)
    label: Mapped[str] = mapped_column(String, default="")
    content: Mapped[str] = mapped_column(Text, default="")

    ats_score: Mapped[int] = mapped_column(Integer, default=0)
    recruiter_score: Mapped[int] = mapped_column(Integer, default=0)
    ats_score_before: Mapped[int] = mapped_column(Integer, default=0)
    missing_keywords: Mapped[list] = mapped_column(JSON, default=list)
    weak_bullets: Mapped[list] = mapped_column(JSON, default=list)
    improvements: Mapped[list] = mapped_column(JSON, default=list)
    validation: Mapped[dict] = mapped_column(JSON, default=dict)
    keyword_report: Mapped[dict] = mapped_column(JSON, default=dict)
    fixes: Mapped[list] = mapped_column(JSON, default=list)
    applied_fix_ids: Mapped[list] = mapped_column(JSON, default=list)


class CoverLetter(Base, TimestampMixin):
    __tablename__ = "cover_letters"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"))
    job_id: Mapped[str | None] = mapped_column(ForeignKey("jobs.id"), nullable=True)
    company: Mapped[str] = mapped_column(String, default="")
    content: Mapped[str] = mapped_column(Text, default="")


# ─────────────────────────────── Interview prep ───────────────────────────────
class InterviewPrep(Base, TimestampMixin):
    __tablename__ = "interview_preps"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"))
    job_id: Mapped[str | None] = mapped_column(ForeignKey("jobs.id"), nullable=True)
    company: Mapped[str] = mapped_column(String, default="")
    role: Mapped[str] = mapped_column(String, default="")
    kind: Mapped[str] = mapped_column(String, default="general")   # general | hirevue
    questions: Mapped[list] = mapped_column(JSON, default=list)   # list of question objects
    live: Mapped[bool] = mapped_column(Boolean, default=False)     # hirevue: real web-sourced?
    note: Mapped[str] = mapped_column(Text, default="")            # hirevue: sourcing status note


# ─────────────────────────────── Learning loop & notifications ──────────────────────
class UserEvent(Base):
    __tablename__ = "user_events"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"))
    event_type: Mapped[str] = mapped_column(String)   # view|save|click|apply|dismiss
    job_id: Mapped[str | None] = mapped_column(String, nullable=True)
    payload: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    user: Mapped[User] = relationship(back_populates="events")


class Notification(Base):
    __tablename__ = "notifications"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"))
    kind: Mapped[str] = mapped_column(String)   # high_match|sponsorship|deadline|...
    title: Mapped[str] = mapped_column(String)
    body: Mapped[str] = mapped_column(Text, default="")
    link: Mapped[str] = mapped_column(String, default="")
    read: Mapped[bool] = mapped_column(Boolean, default=False)
    emailed: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    user: Mapped[User] = relationship(back_populates="notifications")


class FavoriteCompany(Base):
    __tablename__ = "favorite_companies"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"))
    company_name: Mapped[str] = mapped_column(String)
