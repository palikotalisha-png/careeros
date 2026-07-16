# API reference

Base URL: `/api`. All routes except `/auth/*` and `/health` require `Authorization: Bearer <token>`
(Clerk session token in production, or a dev token from `/auth/login`).

## Auth
| Method | Path | Body | Returns |
|--------|------|------|---------|
| POST | `/auth/signup` | email, password, name | access_token |
| POST | `/auth/login` | email, password | access_token |
| GET  | `/auth/me` | — | current user |

## Profile
| GET | `/profile` | — | profile |
| PUT | `/profile` | ProfileIn | profile |
| POST | `/profile/resume` | multipart file (PDF/DOCX) | profile (with parsed resume_text) |

## Analyze (primary flow)
| POST | `/analyze` | resume_text?, job_description?, job_url?, company?, job_title?, save? | full bundle: resume_analysis, match, sponsorship, company_research, interview |

## Resume
| POST | `/resume/optimize` | job_description, company, resume_text? | ResumeVersion (ats/recruiter scores, keywords, validation) |
| GET  | `/resume/versions` | — | list |
| GET  | `/resume/{id}/export.pdf` · `.docx` | — | file download |

## Cover letter
| POST | `/cover-letter` | company, job_description, tone | CoverLetter |
| PUT  | `/cover-letter/{id}` | content | CoverLetter |
| GET  | `/cover-letter/{id}/export.pdf` · `.docx` | — | file download |

## Company / Interview / Sponsorship / Networking
| POST | `/company/research` | company, context | research blob |
| POST | `/interview/prep` | company, role, job_description | questions[] |
| POST | `/interview/feedback` | question, answer | score, strengths, improvements, improved_answer |
| POST | `/sponsorship` | company, job_description | score, probability, compat, e_verify, h1b_history, risk_flags |
| POST | `/networking` | kind, company, recruiter_name, recruiter_role, job_title, job_description | message |

## Tracker / Dashboard / Events
| GET·POST | `/applications` | ApplicationIn | application(s) |
| PUT·DELETE | `/applications/{id}` | ApplicationIn | application / ok |
| GET | `/dashboard` | — | metrics + funnel + upcoming |
| POST | `/events` | event_type, job_id, payload | ok (updates learned prefs) |

Interactive docs at `/docs` (Swagger) when the server is running.
