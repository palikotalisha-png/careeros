"use client";
import { useEffect, useState } from "react";
import Link from "next/link";
import { api } from "@/lib/api";
import { Section, Spinner } from "@/components/ui";

function Stat({ label, value, sub }: { label: string; value: any; sub?: string }) {
  return (
    <div className="card">
      <div className="text-3xl font-bold">{value}</div>
      <div className="mt-1 text-sm font-medium text-slate-500">{label}</div>
      {sub && <div className="text-xs text-slate-400">{sub}</div>}
    </div>
  );
}

function List({ items }: { items?: string[] }) {
  return <ul className="space-y-1.5 text-sm">{(items || []).map((x, i) =>
    <li key={i} className="flex gap-2"><span className="text-brand-500">•</span><span>{x}</span></li>)}</ul>;
}

function CareerCoach() {
  const [s, setS] = useState<any>(null);
  useEffect(() => { api.strategy().then(setS).catch(() => {}); }, []);
  if (!s) return null;
  const range = s.estimated_salary_range || {};
  return (
    <Section title="AI Career Coach">
      <div className="grid gap-4 sm:grid-cols-2">
        <div className="rounded-xl bg-slate-50 p-3 dark:bg-slate-800/50">
          <div className="text-xs text-slate-500">Estimated salary range</div>
          <div className="text-xl font-bold">
            {range.low ? `$${Math.round(range.low / 1000)}k – $${Math.round(range.high / 1000)}k` : "—"}
          </div>
        </div>
        <div className="rounded-xl bg-slate-50 p-3 dark:bg-slate-800/50">
          <div className="text-xs text-slate-500">Estimated interview chance</div>
          <div className="text-xl font-bold">{s.interview_chance_pct != null ? `${s.interview_chance_pct}%` : "—"}</div>
        </div>
      </div>
      <div className="mt-4 grid gap-6 md:grid-cols-2">
        <div><h4 className="mb-1 text-xs font-semibold uppercase text-slate-500">This week's plan</h4><List items={s.weekly_plan} /></div>
        <div><h4 className="mb-1 text-xs font-semibold uppercase text-slate-500">Top companies to target</h4><List items={s.top_companies} /></div>
        <div><h4 className="mb-1 text-xs font-semibold uppercase text-slate-500">Skills to learn</h4><List items={s.skills_to_learn} /></div>
        <div><h4 className="mb-1 text-xs font-semibold uppercase text-slate-500">Certifications to pursue</h4><List items={s.certifications} /></div>
        <div><h4 className="mb-1 text-xs font-semibold uppercase text-slate-500">Networking recommendations</h4><List items={s.networking_recommendations} /></div>
        <div><h4 className="mb-1 text-xs font-semibold uppercase text-slate-500">Alumni to contact</h4><List items={s.alumni_to_contact} /></div>
      </div>
    </Section>
  );
}

export default function Dashboard() {
  const [d, setD] = useState<any>(null);
  const [err, setErr] = useState("");
  useEffect(() => { api.dashboard().then(setD).catch((e) => setErr(e.message)); }, []);

  if (err) return <p className="text-red-600">{err}</p>;
  if (!d) return <Spinner label="Loading dashboard…" />;

  const funnelOrder = ["Saved", "Applying", "Applied", "Assessment", "Recruiter Screen",
    "Interview", "Final Round", "Follow-up", "Offer", "Accepted", "Rejected"];
  const maxF = Math.max(1, ...Object.values(d.funnel as Record<string, number>));

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Dashboard</h1>
          <p className="text-sm text-slate-500">Your job search at a glance.</p>
        </div>
        <Link href="/analyze" className="btn-primary">+ Analyze a Job</Link>
      </div>

      <div className="grid grid-cols-2 gap-4 md:grid-cols-5">
        <Link href="/jobs"><Stat label="New jobs today" value={d.new_jobs_today} sub="View feed →" /></Link>
        <Stat label="Active applications" value={d.active_applications} />
        <Stat label="Applied this month" value={d.applications_this_month} />
        <Stat label="Interviews" value={d.interview_count} />
        <Stat label="Offers" value={d.offer_count} />
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        <Section title="Application funnel">
          <div className="space-y-2">
            {funnelOrder.map((s) => (
              <div key={s} className="flex items-center gap-3">
                <div className="w-20 text-xs text-slate-500">{s}</div>
                <div className="h-5 flex-1 overflow-hidden rounded bg-slate-100 dark:bg-slate-800">
                  <div className="h-full rounded bg-brand-500"
                    style={{ width: `${(d.funnel[s] / maxF) * 100}%` }} />
                </div>
                <div className="w-6 text-right text-xs font-semibold">{d.funnel[s]}</div>
              </div>
            ))}
          </div>
          <p className="mt-3 text-xs text-slate-400">Response rate: {d.response_rate}%</p>
        </Section>

        <Section title="ATS score improvements">
          {d.ats_score_trend.length === 0 ? (
            <p className="text-sm text-slate-400">Optimize a resume to see trends.</p>
          ) : (
            <div className="space-y-3">
              {d.ats_score_trend.map((t: any, i: number) => (
                <div key={i}>
                  <div className="mb-1 flex justify-between text-xs">
                    <span className="text-slate-500">{t.label}</span>
                    <span className="font-semibold text-green-600">+{t.after - t.before}</span>
                  </div>
                  <div className="flex h-3 overflow-hidden rounded bg-slate-100 dark:bg-slate-800">
                    <div className="bg-slate-400" style={{ width: `${t.before}%` }} />
                    <div className="bg-green-500" style={{ width: `${t.after - t.before}%` }} />
                  </div>
                </div>
              ))}
            </div>
          )}
        </Section>

        <Section title="Upcoming interviews">
          {d.upcoming_interviews.length === 0 ? <p className="text-sm text-slate-400">None scheduled.</p> :
            <ul className="space-y-2 text-sm">{d.upcoming_interviews.map((x: any, i: number) =>
              <li key={i} className="flex justify-between"><span>{x.job_title} · {x.company}</span>
                <span className="text-slate-400">{x.date}</span></li>)}</ul>}
        </Section>

        <Section title="Upcoming follow-ups">
          {d.upcoming_followups.length === 0 ? <p className="text-sm text-slate-400">Nothing due.</p> :
            <ul className="space-y-2 text-sm">{d.upcoming_followups.map((x: any, i: number) =>
              <li key={i} className="flex justify-between"><span>{x.job_title} · {x.company}</span>
                <span className="text-slate-400">{x.date}</span></li>)}</ul>}
        </Section>
      </div>

      <CareerCoach />
    </div>
  );
}
