from __future__ import annotations
from datetime import date, datetime
from pydantic import BaseModel, EmailStr, ConfigDict


class ORM(BaseModel):
    model_config = ConfigDict(from_attributes=True)


# Auth
class SignUp(BaseModel):
    email: EmailStr
    password: str
    name: str = ""


class Login(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


# Profile
class ProfileIn(BaseModel):
    degree: str = ""
    major: str = ""
    minor: str = ""
    graduation_date: date | None = None
    gpa: float | None = None
    skills: list[str] = []
    resume_text: str = ""
    linkedin_url: str = ""
    preferred_locations: list[str] = []
    desired_industries: list[str] = []
    career_goals: str = ""
    visa_status: str = ""
    opt_eligible: bool = False
    stem_opt_eligible: bool = False
    requires_sponsorship: bool = True
    salary_min: int | None = None
    salary_max: int | None = None


class ProfileOut(ProfileIn, ORM):
    id: str
    resume_filename: str = ""


# Jobs
class JobOut(ORM):
    id: str
    title: str
    company_name: str
    location: str
    salary: str
    source: str
    apply_url: str
    date_posted: date | None
    deadline: date | None
    e_verify: bool | None


class MatchOut(ORM):
    id: str
    job_id: str
    match_score: int
    sponsorship_score: int
    intl_compat_score: int
    sponsorship_probability: str
    strengths: list
    risks: list
    missing_skills: list
    missing_qualifications: list
    recommended_actions: list
    risk_flags: list
    explanation: str


class JobWithMatch(BaseModel):
    job: JobOut
    match: MatchOut | None = None


# Resume
class ResumeOptimizeIn(BaseModel):
    job_id: str | None = None
    job_description: str = ""
    company: str = ""
    resume_text: str = ""   # falls back to profile resume


class ResumeOut(ORM):
    id: str
    label: str
    content: str
    ats_score: int
    recruiter_score: int
    ats_score_before: int
    missing_keywords: list
    weak_bullets: list
    improvements: list
    validation: dict
    keyword_report: dict
    fixes: list = []
    applied_fix_ids: list = []


class ApplyFixIn(BaseModel):
    fix_id: str


# Cover letter
class CoverLetterIn(BaseModel):
    job_id: str | None = None
    company: str = ""
    job_description: str = ""
    tone: str = "professional"


class CoverLetterOut(ORM):
    id: str
    company: str
    content: str


# Company
class CompanyOut(ORM):
    id: str
    name: str
    industry: str
    headquarters: str
    size: str
    revenue: str
    description: str
    research: dict
    e_verify: bool | None
    sponsorship_score: int | None


# Interview
class InterviewIn(BaseModel):
    job_id: str | None = None
    company: str = ""
    role: str = ""
    job_description: str = ""


class InterviewOut(ORM):
    id: str
    company: str
    role: str
    questions: list


class MockAnswerIn(BaseModel):
    question: str
    answer: str


# HireVue
class HireVueIn(BaseModel):
    job_id: str | None = None
    company: str = ""
    role: str = ""
    job_description: str = ""


class HireVueOut(ORM):
    id: str
    company: str
    role: str
    questions: list
    live: bool = False
    note: str = ""


# Application package
class PackageIn(BaseModel):
    job_id: str | None = None
    resume_version_id: str | None = None
    cover_letter_id: str | None = None
    company: str = ""
    job_title: str = ""
    job_description: str = ""


# Sponsorship
class SponsorshipOut(BaseModel):
    company: str
    sponsorship_score: int
    sponsorship_probability: str
    intl_compat_score: int
    e_verify: bool | None
    h1b_history: list
    risk_flags: list
    summary: str


# Tracker
class ApplicationIn(BaseModel):
    job_id: str | None = None
    company: str = ""
    job_title: str = ""
    location: str = ""
    source: str = ""
    status: str = "Saved"
    date_found: date | None = None
    date_applied: date | None = None
    interview_date: date | None = None
    follow_up_date: date | None = None
    deadline: date | None = None
    salary: str = ""
    recruiter: str = ""
    recruiter_linkedin: str = ""
    referral_status: str = "None"
    work_auth_notes: str = ""
    sponsorship_available: bool | None = None
    e_verify: bool | None = None
    notes: str = ""
    resume_version_id: str | None = None
    cover_letter_id: str | None = None


class ApplicationOut(ApplicationIn, ORM):
    id: str
    created_at: datetime


# Networking
class OutreachIn(BaseModel):
    kind: str = "linkedin"   # linkedin|referral|recruiter|thank_you|follow_up
    company: str = ""
    recruiter_name: str = ""
    recruiter_role: str = ""
    job_title: str = ""
    job_description: str = ""
    context: str = ""


class OutreachOut(BaseModel):
    kind: str
    message: str


# Events / notifications
class EventIn(BaseModel):
    event_type: str
    job_id: str | None = None
    payload: dict = {}


class NotificationOut(ORM):
    id: str
    kind: str
    title: str
    body: str
    link: str
    read: bool
    created_at: datetime


# Extension
class ExtensionAnalyzeIn(BaseModel):
    title: str
    company: str
    location: str = ""
    description: str = ""
    url: str = ""
    source: str = "extension"
