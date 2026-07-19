"use client";
import { useEffect, useState } from "react";
import { MapPin, DollarSign, ExternalLink, ShieldCheck, Building2 } from "lucide-react";
import { api } from "@/lib/api";
import { Badge, Spinner } from "@/components/ui";

export default function Jobs() {
  const [rows, setRows] = useState<any[] | null>(null);
  const [favorites, setFavorites] = useState<string[]>([]);
  const [minMatch, setMinMatch] = useState(0);
  const [sponsorshipOnly, setSponsorshipOnly] = useState(false);
  const [location, setLocation] = useState("");
  const [saved, setSaved] = useState<Record<string, boolean>>({});
  const [newFavorite, setNewFavorite] = useState("");
  const [expanded, setExpanded] = useState<string | null>(null);

  function load() {
    setRows(null);
    api.jobs({ min_match: minMatch, sponsorship_only: sponsorshipOnly, location }).then(setRows);
  }
  useEffect(() => { load(); api.favorites().then(setFavorites); }, []); // eslint-disable-line
  useEffect(() => { load(); }, [minMatch, sponsorshipOnly, location]); // eslint-disable-line

  async function save(jobId: string) {
    await api.saveJob(jobId);
    setSaved((s) => ({ ...s, [jobId]: true }));
  }

  async function addFavorite() {
    if (!newFavorite.trim()) return;
    await api.addFavorite(newFavorite.trim());
    setFavorites(await api.favorites());
    setNewFavorite("");
  }
  async function removeFavorite(name: string) {
    await api.removeFavorite(name);
    setFavorites(await api.favorites());
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Job Feed</h1>
          <p className="text-sm text-slate-500">
            New openings found today, scored against your profile.
          </p>
        </div>
      </div>

      <div className="card space-y-3">
        <div className="flex flex-wrap items-end gap-4">
          <div>
            <label className="label">Min match score</label>
            <input type="range" min={0} max={100} step={5} value={minMatch}
              onChange={(e) => setMinMatch(Number(e.target.value))} className="w-40" />
            <div className="text-xs text-slate-500">{minMatch}+</div>
          </div>
          <div>
            <label className="label">Location contains</label>
            <input className="input w-48" value={location} placeholder="e.g. Remote, NY"
              onChange={(e) => setLocation(e.target.value)} />
          </div>
          <label className="flex items-center gap-2 pb-2 text-sm">
            <input type="checkbox" checked={sponsorshipOnly}
              onChange={(e) => setSponsorshipOnly(e.target.checked)} />
            Sponsorship-friendly only
          </label>
        </div>

        <div className="border-t border-slate-100 pt-3 dark:border-slate-700">
          <label className="label">Favorite companies (monitored for new openings)</label>
          <div className="flex flex-wrap items-center gap-2">
            {favorites.map((f) => (
              <span key={f} className="chip bg-slate-100 text-slate-600 dark:bg-slate-700 dark:text-slate-300">
                {f}
                <button className="ml-1.5 text-slate-400 hover:text-red-500" onClick={() => removeFavorite(f)}>×</button>
              </span>
            ))}
            <input className="input w-40" placeholder="Add a company…" value={newFavorite}
              onChange={(e) => setNewFavorite(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && addFavorite()} />
            <button className="btn-ghost px-3 py-1.5 text-xs" onClick={addFavorite}>Add</button>
          </div>
        </div>
      </div>

      {!rows && <Spinner label="Loading jobs…" />}
      {rows && rows.length === 0 && (
        <div className="card text-center text-slate-400">
          No jobs match your filters yet. New openings are pulled in automatically once a day —
          try lowering the match filter, or add a favorite company above.
        </div>
      )}

      <div className="space-y-3">
        {rows?.map(({ job, match }) => (
          <div key={job.id} className="card">
            <div className="flex flex-wrap items-start justify-between gap-3">
              <div className="min-w-0">
                <div className="flex items-center gap-2">
                  <h3 className="font-display font-semibold">{job.title}</h3>
                  <span className="chip bg-slate-100 text-slate-500 dark:bg-slate-700">{job.source}</span>
                </div>
                <div className="mt-1 flex flex-wrap items-center gap-x-3 gap-y-1 text-sm text-slate-500">
                  <span className="flex items-center gap-1"><Building2 size={13} /> {job.company_name}</span>
                  <span className="flex items-center gap-1"><MapPin size={13} /> {job.location || "Location not listed"}</span>
                  {job.salary && <span className="flex items-center gap-1"><DollarSign size={13} /> {job.salary}</span>}
                </div>
                {job.date_posted && (
                  <div className="mt-0.5 text-xs text-slate-400">Posted {job.date_posted}</div>
                )}
              </div>
              <div className="flex items-center gap-4">
                <div className="text-center">
                  <div className="font-display text-2xl font-bold text-brand-600 dark:text-brand-400">{match?.match_score ?? "—"}</div>
                  <div className="text-[10px] uppercase tracking-wide text-slate-400">Match</div>
                </div>
                {match && <Badge level={match.sponsorship_probability}>{match.sponsorship_probability} sponsorship</Badge>}
                {job.e_verify && (
                  <span className="chip flex items-center gap-1 bg-green-100 text-green-700 dark:bg-green-900/40 dark:text-green-300">
                    <ShieldCheck size={12} /> E-Verify
                  </span>
                )}
              </div>
            </div>

            {match?.risk_flags?.length > 0 && (
              <div className="mt-2 text-xs text-red-600">⚠ {match.risk_flags.join(", ")}</div>
            )}

            <div className="mt-3 flex items-center gap-3 text-sm">
              <button className="text-brand-600 hover:underline"
                onClick={() => setExpanded(expanded === job.id ? null : job.id)}>
                {expanded === job.id ? "Hide details" : "Why this score?"}
              </button>
              <a href={job.apply_url} target="_blank" rel="noreferrer"
                className="flex items-center gap-1 text-brand-600 hover:underline dark:text-brand-400">
                View posting <ExternalLink size={13} />
              </a>
              <button className="btn-primary ml-auto px-3 py-1.5 text-xs"
                disabled={!!saved[job.id]} onClick={() => save(job.id)}>
                {saved[job.id] ? "Saved to tracker" : "Save to tracker"}
              </button>
            </div>

            {expanded === job.id && match && (
              <div className="mt-3 grid gap-3 border-t border-slate-100 pt-3 text-sm dark:border-slate-700 md:grid-cols-2">
                <div>
                  <div className="mb-1 text-xs font-semibold uppercase text-slate-500">Strengths</div>
                  <ul className="list-inside list-disc text-slate-600 dark:text-slate-300">
                    {(match.strengths || []).map((s: string, i: number) => <li key={i}>{s}</li>)}
                  </ul>
                </div>
                <div>
                  <div className="mb-1 text-xs font-semibold uppercase text-slate-500">Missing skills</div>
                  <ul className="list-inside list-disc text-slate-600 dark:text-slate-300">
                    {(match.missing_skills || []).map((s: string, i: number) => <li key={i}>{s}</li>)}
                  </ul>
                </div>
                <div className="md:col-span-2">
                  <div className="mb-1 text-xs font-semibold uppercase text-slate-500">Recommended actions</div>
                  <ul className="list-inside list-disc text-slate-600 dark:text-slate-300">
                    {(match.recommended_actions || []).map((s: string, i: number) => <li key={i}>{s}</li>)}
                  </ul>
                </div>
                <div className="md:col-span-2 text-slate-500">{match.explanation}</div>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
