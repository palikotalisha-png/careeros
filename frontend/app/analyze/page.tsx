"use client";
import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { ScoreRing, Badge, Section, Spinner } from "@/components/ui";

type Tab = "input" | "resume" | "sponsorship" | "company" | "interview" | "hirevue" | "tools";

export default function Analyze() {
  const [profile, setProfile] = useState<any>(null);
  const [jd, setJd] = useState("");
  const [url, setUrl] = useState("");
  const [company, setCompany] = useState("");
  const [title, setTitle] = useState("");
  const [resumeText, setResumeText] = useState("");
  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState("");
  const [res, setRes] = useState<any>(null);
  const [tab, setTab] = useState<Tab>("input");
  const [saved, setSaved] = useState(false);
  const [pkgBusy, setPkgBusy] = useState(false);
  const [resumeVersionId, setResumeVersionId] = useState<string | null>(null);
  const [coverLetterId, setCoverLetterId] = useState<string | null>(null);

  useEffect(() => {
    api.getProfile().then((p) => { setProfile(p); setResumeText(p.resume_text || ""); }).catch(() => {});
  }, []);

  async function run() {
    setErr(""); setLoading(true); setRes(null);
    try {
      const r = await api.analyze({
        resume_text: resumeText, job_description: jd, job_url: url,
        company, job_title: title, save: false,
      });
      setRes(r); setTab("resume");
    } catch (e: any) { setErr(e.message); } finally { setLoading(false); }
  }

  async function saveToTracker() {
    await api.createApp({
      company: res.job.company, job_title: res.job.title, source: "paste",
      status: "Saved", date_found: new Date().toISOString().slice(0, 10),
      resume_version_id: resumeVersionId, cover_letter_id: coverLetterId,
    });
    setSaved(true);
  }

  async function downloadPackage() {
    setPkgBusy(true);
    try {
      await api.downloadPackage(
        { job_id: res.job.id, company: res.job.company, job_title: res.job.title, job_description: jd },
        `application_package_${(res.job.company || "role").replace(/\s+/g, "_")}.zip`
      );
    } finally { setPkgBusy(false); }
  }

  const tabs: [Tab, string][] = [
    ["input", "Job & Resume"], ["resume", "Resume & ATS"], ["sponsorship", "Sponsorship"],
    ["company", "Company"], ["interview", "Interview"], ["hirevue", "HireVue"],
    ["tools", "Cover Letter & Outreach"],
  ];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Analyze a Job</h1>
        <p className="text-sm text-slate-500">Paste a description or URL, then get your full application kit.</p>
      </div>

      <div className="flex flex-wrap gap-1 border-b border-slate-200 dark:border-slate-800">
        {tabs.map(([t, lab]) => (
          <button key={t} onClick={() => setTab(t)} disabled={t !== "input" && !res}
            className={`rounded-t-lg px-3 py-2 text-sm font-medium disabled:opacity-40 ${
              tab === t ? "border-b-2 border-brand-600 text-brand-700 dark:text-brand-300"
              : "text-slate-500 hover:text-slate-700"}`}>{lab}</button>
        ))}
      </div>

      {tab === "input" && (
        <div className="grid gap-6 md:grid-cols-2">
          <Section title="Job posting">
            <label className="label">Paste job URL (optional)</label>
            <input className="input" value={url} onChange={(e) => setUrl(e.target.value)}
              placeholder="https://… (we fetch the text)" />
            <label className="label mt-3">Or paste the description</label>
            <textarea className="input h-44" value={jd} onChange={(e) => setJd(e.target.value)}
              placeholder="Paste the full job description here…" />
            <div className="mt-3 grid grid-cols-2 gap-3">
              <div><label className="label">Company</label><input className="input" value={company} onChange={(e) => setCompany(e.target.value)} /></div>
              <div><label className="label">Job title</label><input className="input" value={title} onChange={(e) => setTitle(e.target.value)} /></div>
            </div>
          </Section>
          <Section title="Your resume">
            <p className="mb-2 text-xs text-slate-500">Pulled from your profile — edit here or upload on the Profile page.</p>
            <textarea className="input h-56 font-mono text-xs" value={resumeText}
              onChange={(e) => setResumeText(e.target.value)} placeholder="Your resume text…" />
          </Section>
          <div className="md:col-span-2">
            {err && <p className="mb-3 text-sm text-red-600">{err}</p>}
            <button className="btn-primary" onClick={run} disabled={loading || (!jd && !url)}>
              {loading ? "Analyzing…" : "Analyze Job →"}
            </button>
            {loading && <div className="mt-3"><Spinner label="Running recruiter analysis, ATS scan, sponsorship & company research…" /></div>}
          </div>
        </div>
      )}

      {res && tab === "resume" && <ResumeTab res={res} jd={jd} company={res.job.company} onVersionSaved={setResumeVersionId} />}
      {res && tab === "sponsorship" && <SponsorshipTab s={res.sponsorship} />}
      {res && tab === "company" && <CompanyTab c={res.company_research} />}
      {res && tab === "interview" && <InterviewTab questions={res.interview.questions} />}
      {res && tab === "hirevue" && <HireVueTab job={res.job} jd={jd} />}
      {res && tab === "tools" && <ToolsTab job={res.job} jd={jd} onCoverLetterSaved={setCoverLetterId} />}

      {res && (
        <div className="flex flex-wrap items-center gap-3">
          <button className="btn-primary" onClick={saveToTracker} disabled={saved}>
            {saved ? "Saved to tracker ✓" : "Save to Application Tracker"}</button>
          <button className="btn-ghost" onClick={downloadPackage} disabled={pkgBusy}>
            {pkgBusy ? "Packaging…" : "Download full application package"}</button>
          <span className="text-sm text-slate-500">{res.job.title} · {res.job.company}</span>
        </div>
      )}
    </div>
  );
}

function List({ items, tone }: { items: string[]; tone?: "good" | "bad" }) {
  const dot = tone === "good" ? "text-green-500" : tone === "bad" ? "text-red-500" : "text-brand-500";
  return <ul className="space-y-1.5 text-sm">{(items || []).map((x, i) =>
    <li key={i} className="flex gap-2"><span className={dot}>•</span><span>{x}</span></li>)}</ul>;
}

function ResumeTab({ res, jd, company, onVersionSaved }: any) {
  const a = res.resume_analysis;
  const [vid, setVid] = useState<string | null>(null);
  const [fixes, setFixes] = useState<any[]>(a.fixes || []);
  const [applied, setApplied] = useState<string[]>([]);
  const [content, setContent] = useState(a.optimized_resume);
  const [atsScore, setAtsScore] = useState(a.ats_score);
  const [fixBusy, setFixBusy] = useState<string | null>(null);

  async function makeVersion() {
    const r = await api.optimizeResume({ job_description: jd, company });
    setVid(r.id); setFixes(r.fixes || []); setApplied(r.applied_fix_ids || []);
    setContent(r.content); setAtsScore(r.ats_score);
    onVersionSaved?.(r.id);
  }
  async function applyFix(fixId: string) {
    if (!vid) return;
    setFixBusy(fixId);
    try {
      const r = await api.applyFix(vid, fixId);
      setApplied(r.applied_fix_ids || []); setContent(r.content); setAtsScore(r.ats_score);
    } finally { setFixBusy(null); }
  }
  return (
    <div className="space-y-6">
      <div className="grid gap-4 sm:grid-cols-3">
        <div className="card flex items-center justify-around">
          <ScoreRing value={a.match_score} label="Recruiter match" />
          <ScoreRing value={atsScore} label="ATS score" />
        </div>
        <Section title="ATS improvement">
          <div className="flex items-end gap-2">
            <span className="text-4xl font-bold text-green-600">+{atsScore - a.ats_score_before}</span>
            <span className="pb-1 text-sm text-slate-500">{a.ats_score_before} → {atsScore}</span>
          </div>
          <div className="mt-2 flex h-3 overflow-hidden rounded bg-slate-100 dark:bg-slate-800">
            <div className="bg-slate-400" style={{ width: `${a.ats_score_before}%` }} />
            <div className="bg-green-500" style={{ width: `${atsScore - a.ats_score_before}%` }} />
          </div>
          <p className="mt-2 text-xs text-slate-500">Validation: {a.validation.passed ? "ATS-safe ✓" : "Review formatting"}</p>
        </Section>
        <Section title="Missing keywords">
          <div className="flex flex-wrap gap-2">
            {a.missing_keywords.map((k: string, i: number) =>
              <span key={i} className="chip bg-amber-100 text-amber-700 dark:bg-amber-900/40 dark:text-amber-300">{k}</span>)}
          </div>
        </Section>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        <Section title="Strongest qualifications"><List items={a.strengths} tone="good" /></Section>
        <Section title="Biggest experience gaps"><List items={a.experience_gaps} tone="bad" /></Section>
        <Section title="Weak bullets to fix"><List items={a.weak_bullets} tone="bad" /></Section>
        <Section title="Recommendations"><List items={a.recommendations} /></Section>
      </div>

      {vid && (
        <Section title="One-click fixes">
          {fixes.length === 0 ? <p className="text-sm text-slate-400">No itemized fixes returned.</p> : (
            <div className="space-y-2">
              {fixes.map((f) => {
                const done = applied.includes(f.id);
                return (
                  <div key={f.id} className={`rounded-xl border p-3 text-sm ${done ? "border-green-300 bg-green-50 dark:border-green-800 dark:bg-green-900/20" : "border-slate-200 dark:border-slate-800"}`}>
                    <div className="flex items-start justify-between gap-3">
                      <div>
                        <span className="chip mr-2 bg-slate-100 text-slate-500 dark:bg-slate-800">{f.category}</span>
                        <span className="text-slate-600 dark:text-slate-300">{f.issue}</span>
                      </div>
                      <button className="btn-ghost shrink-0 py-1 text-xs" disabled={done || fixBusy === f.id}
                        onClick={() => applyFix(f.id)}>
                        {done ? "Applied ✓" : fixBusy === f.id ? "Applying…" : "Apply fix"}
                      </button>
                    </div>
                    {f.before && <p className="mt-2 text-xs text-slate-400 line-through">{f.before}</p>}
                    {f.after && <p className="text-xs text-green-700 dark:text-green-400">{f.after}</p>}
                  </div>
                );
              })}
            </div>
          )}
        </Section>
      )}

      <Section title="Optimized resume (XYZ formula, ATS-safe)"
        right={vid && (
          <span className="flex gap-2">
            <a className="btn-ghost py-1.5 text-xs" href={api.exportUrl("resume", vid, "pdf")} target="_blank">PDF</a>
            <a className="btn-ghost py-1.5 text-xs" href={api.exportUrl("resume", vid, "docx")} target="_blank">DOCX</a>
          </span>)}>
        <pre className="max-h-72 overflow-auto whitespace-pre-wrap rounded-lg bg-slate-50 p-3 text-xs dark:bg-slate-800/50">{content}</pre>
        {!vid && <button className="btn-primary mt-3" onClick={makeVersion}>Save version & enable export</button>}
      </Section>
    </div>
  );
}

function SponsorshipTab({ s }: any) {
  return (
    <div className="space-y-6">
      {s.risk_flags?.length > 0 && (
        <div className="rounded-2xl border border-red-300 bg-red-50 p-4 dark:border-red-800 dark:bg-red-900/20">
          <p className="font-semibold text-red-700 dark:text-red-300">⚠ Risk phrases detected</p>
          <ul className="mt-2 text-sm text-red-700 dark:text-red-300">
            {s.risk_flags.map((f: string, i: number) => <li key={i}>• {f}</li>)}</ul>
        </div>
      )}
      <div className="grid gap-4 sm:grid-cols-3">
        <div className="card flex flex-col items-center">
          <ScoreRing value={s.sponsorship_score} label="Sponsorship score" />
          <Badge level={s.sponsorship_probability}>{s.sponsorship_probability} probability</Badge>
        </div>
        <div className="card flex items-center justify-center"><ScoreRing value={s.intl_compat_score} label="Intl. compatibility" /></div>
        <Section title="Signals">
          <ul className="space-y-2 text-sm">
            <li className="flex justify-between"><span>E-Verify</span><span className="font-medium">{s.e_verify === true ? "Yes" : s.e_verify === false ? "No" : "Unknown"}</span></li>
            <li className="flex justify-between"><span>H-1B records</span><span className="font-medium">{(s.h1b_history || []).reduce((n: number, h: any) => n + (h.count || 0), 0)}</span></li>
          </ul>
        </Section>
      </div>
      <Section title="Summary"><p className="text-sm">{s.summary}</p></Section>
    </div>
  );
}

function CompanyTab({ c }: any) {
  const ov = c.overview || {}, bi = c.business_intelligence || {}, ci = c.career_intelligence || {};
  const Row = ({ k, v }: any) => <div className="flex justify-between gap-4 border-b border-slate-100 py-1.5 text-sm last:border-0 dark:border-slate-800"><span className="text-slate-500">{k}</span><span className="text-right font-medium">{Array.isArray(v) ? v.join(", ") : v}</span></div>;
  return (
    <div className="space-y-6">
      <Section title="Overview">
        <Row k="What they do" v={ov.what_they_do} /><Row k="Industry" v={ov.industry} />
        <Row k="Products" v={ov.products} /><Row k="HQ" v={ov.headquarters} />
        <Row k="Size" v={ov.size} /><Row k="Revenue" v={ov.revenue} />
      </Section>
      <div className="grid gap-6 md:grid-cols-2">
        <Section title="Business intelligence">
          <p className="mb-2 text-sm"><b>Recent news:</b> {(bi.recent_news || []).join("; ")}</p>
          <p className="mb-2 text-sm"><b>Initiatives:</b> {(bi.strategic_initiatives || []).join("; ")}</p>
          <p className="text-sm"><b>Market position:</b> {bi.market_position}</p>
        </Section>
        <Section title="Career intelligence">
          <p className="mb-2 text-sm"><b>Culture:</b> {ci.culture}</p>
          <p className="mb-2 text-sm"><b>Values:</b> {(ci.values || []).join(", ")}</p>
          <p className="mb-2 text-sm"><b>Hiring trends:</b> {ci.hiring_trends}</p>
          <p className="text-sm"><b>Sponsorship history:</b> {ci.sponsorship_history}</p>
        </Section>
      </div>
      <Section title="Why this company may fit you">
        <p className="text-sm">{c.personalized_insight}</p>
      </Section>
    </div>
  );
}

function InterviewTab({ questions }: any) {
  const [open, setOpen] = useState<number | null>(0);
  const [mock, setMock] = useState<{ q: string; a: string } | null>(null);
  const [fb, setFb] = useState<any>(null);
  const [busy, setBusy] = useState(false);
  async function getFeedback() {
    setBusy(true); const r = await api.interviewFeedback({ question: mock!.q, answer: mock!.a });
    setFb(r); setBusy(false);
  }
  return (
    <div className="space-y-6">
      <Section title="Questions with STAR frameworks">
        <div className="space-y-2">
          {questions.map((q: any, i: number) => (
            <div key={i} className="rounded-xl border border-slate-200 dark:border-slate-800">
              <button className="flex w-full items-center justify-between px-4 py-3 text-left"
                onClick={() => setOpen(open === i ? null : i)}>
                <span className="text-sm font-medium">{q.question}</span>
                <span className="chip bg-slate-100 text-slate-500 dark:bg-slate-800">{q.category}</span>
              </button>
              {open === i && (
                <div className="space-y-2 border-t border-slate-100 px-4 py-3 text-sm dark:border-slate-800">
                  <p><b>Why they ask:</b> {q.why_they_ask}</p>
                  <p><b>Strong answer includes:</b> {(q.strong_answer_includes || []).join("; ")}</p>
                  <p><b>Framework:</b> {q.framework}</p>
                  <p className="rounded-lg bg-slate-50 p-2 dark:bg-slate-800/50"><b>Sample (STAR):</b> {q.personalized_star}</p>
                  <button className="btn-ghost py-1.5 text-xs" onClick={() => { setMock({ q: q.question, a: "" }); setFb(null); }}>Practice this →</button>
                </div>
              )}
            </div>
          ))}
        </div>
      </Section>

      {mock && (
        <Section title="Mock interview">
          <p className="mb-2 text-sm font-medium">{mock.q}</p>
          <textarea className="input h-28" value={mock.a} onChange={(e) => setMock({ ...mock, a: e.target.value })} placeholder="Type your answer…" />
          <button className="btn-primary mt-3" onClick={getFeedback} disabled={busy || !mock.a}>{busy ? "Scoring…" : "Get feedback"}</button>
          {fb && (
            <div className="mt-4 space-y-2 text-sm">
              <div className="flex items-center gap-3"><ScoreRing value={fb.score} size={64} /><span className="font-medium">Answer score</span></div>
              <p><b>Strengths:</b> {(fb.strengths || []).join("; ")}</p>
              <p><b>Improve:</b> {(fb.improvements || []).join("; ")}</p>
              <p className="rounded-lg bg-slate-50 p-2 dark:bg-slate-800/50"><b>Improved answer:</b> {fb.improved_answer}</p>
            </div>
          )}
        </Section>
      )}
    </div>
  );
}

function HireVueTab({ job, jd }: any) {
  const [data, setData] = useState<any>(null);
  const [busy, setBusy] = useState(false);
  const [open, setOpen] = useState<number | null>(0);

  async function gen() {
    setBusy(true);
    try {
      const r = await api.hirevuePrep({ company: job.company, role: job.title, job_description: jd });
      setData(r);
    } finally { setBusy(false); }
  }

  if (!data) {
    return (
      <Section title="Real interview questions">
        <p className="mb-3 text-sm text-slate-500">
          Pulls actual candidate-reported questions for this company and role from public
          sources (Reddit, Glassdoor, Indeed reviews) — not AI-generated guesses. Each question
          links back to where it was reported.
        </p>
        <button className="btn-primary" onClick={gen} disabled={busy}>{busy ? "Searching…" : "Find real questions"}</button>
      </Section>
    );
  }

  if (!data.live || (data.questions || []).length === 0) {
    return (
      <Section title="Real interview questions">
        <p className="text-sm text-slate-500">{data.note || "No sourced questions available."}</p>
        <button className="btn-ghost mt-3" onClick={gen} disabled={busy}>{busy ? "Searching…" : "Try again"}</button>
      </Section>
    );
  }

  return (
    <Section title="Real interview questions"
      right={<span className="chip bg-green-100 text-green-700 dark:bg-green-900/40 dark:text-green-300">Sourced from the web</span>}>
      <div className="space-y-2">
        {data.questions.map((q: any, i: number) => (
          <div key={i} className="rounded-xl border border-slate-200 dark:border-slate-800">
            <button className="flex w-full items-center justify-between px-4 py-3 text-left"
              onClick={() => setOpen(open === i ? null : i)}>
              <span className="text-sm font-medium">{q.question}</span>
              <span className="chip bg-slate-100 text-slate-500 dark:bg-slate-800">{q.source_domain}</span>
            </button>
            {open === i && (
              <div className="space-y-2 border-t border-slate-100 px-4 py-3 text-sm dark:border-slate-800">
                <p><b>Why they ask:</b> {q.why_they_ask}</p>
                <p><b>Strong answer includes:</b> {(q.strong_answer_includes || []).join("; ")}</p>
                {q.personalized_star && (
                  <p className="rounded-lg bg-slate-50 p-2 dark:bg-slate-800/50"><b>Sample (STAR):</b> {q.personalized_star}</p>
                )}
                <a href={q.source_url} target="_blank" rel="noreferrer" className="block text-xs text-brand-600 hover:underline">
                  Source: {q.source_title} →
                </a>
              </div>
            )}
          </div>
        ))}
      </div>
    </Section>
  );
}

function ToolsTab({ job, jd, onCoverLetterSaved }: any) {
  const [cl, setCl] = useState<any>(null);
  const [clBusy, setClBusy] = useState(false);
  const [net, setNet] = useState("");
  const [kind, setKind] = useState("linkedin");
  const [netBusy, setNetBusy] = useState(false);

  async function genCover() {
    setClBusy(true);
    const r = await api.coverLetter({ company: job.company, job_description: jd, tone: "professional" });
    setCl(r); setClBusy(false);
    onCoverLetterSaved?.(r.id);
  }
  async function genNet() {
    setNetBusy(true);
    const r = await api.networking({ kind, company: job.company, job_title: job.title, job_description: jd });
    setNet(r.message); setNetBusy(false);
  }
  return (
    <div className="grid gap-6 md:grid-cols-2">
      <Section title="Cover letter"
        right={cl && <span className="flex gap-2">
          <a className="btn-ghost py-1.5 text-xs" href={api.exportUrl("cover-letter", cl.id, "pdf")} target="_blank">PDF</a>
          <a className="btn-ghost py-1.5 text-xs" href={api.exportUrl("cover-letter", cl.id, "docx")} target="_blank">DOCX</a></span>}>
        {!cl ? <button className="btn-primary" onClick={genCover} disabled={clBusy}>{clBusy ? "Writing…" : "Generate cover letter"}</button>
          : <textarea className="input h-72 text-sm" defaultValue={cl.content} />}
      </Section>
      <Section title="Networking message">
        <select className="input mb-3" value={kind} onChange={(e) => setKind(e.target.value)}>
          <option value="linkedin">LinkedIn connection</option>
          <option value="referral">Referral request</option>
          <option value="recruiter">Recruiter outreach</option>
          <option value="thank_you">Thank-you email</option>
          <option value="follow_up">Follow-up email</option>
        </select>
        <button className="btn-primary" onClick={genNet} disabled={netBusy}>{netBusy ? "Writing…" : "Generate"}</button>
        {net && <textarea className="input mt-3 h-52 text-sm" defaultValue={net} />}
      </Section>
    </div>
  );
}
