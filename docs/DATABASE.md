# Database schema

PostgreSQL via SQLAlchemy 2 (`backend/app/models.py`). A SQLite fallback is built in for
zero-infra local runs. Tables are auto-created on startup; for production use Alembic migrations.

| Table | Purpose | Key columns |
|-------|---------|-------------|
| `users` | accounts | id, email, name, hashed_password, auth_provider |
| `profiles` | 1:1 user profile | degree, major, minor, graduation_date, gpa, skills[], resume_text, linkedin_url, preferred_locations[], desired_industries[], career_goals, visa_status, opt_eligible, stem_opt_eligible, requires_sponsorship, salary_min/max, preference_vector |
| `companies` | researched companies | name, normalized_name, industry, headquarters, size, revenue, research(json), e_verify, sponsorship_score |
| `sponsorship_records` | public H-1B/E-Verify/PERM rows | company_id, record_type, fiscal_year, count, job_title, detail |
| `jobs` | analyzed postings | title, company_name, location, description, salary, source, apply_url, date_posted, deadline, e_verify, dedup_hash |
| `job_matches` | per-user AI scoring | match_score, sponsorship_score, intl_compat_score, sponsorship_probability, strengths[], risks[], missing_skills[], missing_qualifications[], recommended_actions[], risk_flags[], explanation |
| `applications` | tracker | company, job_title, source, status, date_found/applied, interview_date, follow_up_date, recruiter, notes, resume_version_id, cover_letter_id |
| `resume_versions` | optimized resumes | label, content, ats_score, recruiter_score, ats_score_before, missing_keywords[], weak_bullets[], improvements[], validation(json), keyword_report(json) |
| `cover_letters` | generated letters | company, content |
| `interview_preps` | question sets | company, role, questions(json) |
| `user_events` | learning-loop signals | event_type, job_id, payload |
| `notifications` | in-app/email alerts | kind, title, body, link, read, emailed |
| `favorite_companies` | watchlist | company_name |

### Relationships
- `User 1—1 Profile`, `User 1—* Application / ResumeVersion / CoverLetter / InterviewPrep / UserEvent / Notification`
- `Company 1—* Job`, `Company 1—* SponsorshipRecord`
- `Job 1—* JobMatch`, `Application *—1 Job` (optional)

Statuses: `Saved · Applying · Applied · Interview · Follow-up · Rejected · Offer · Accepted`.
