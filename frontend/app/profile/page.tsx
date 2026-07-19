"use client";
import { useEffect, useRef, useState } from "react";
import { api } from "@/lib/api";
import { Section, Spinner } from "@/components/ui";

export default function Profile() {
  const [p, setP] = useState<any>(null);
  const [saved, setSaved] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [uploadWarning, setUploadWarning] = useState("");
  const [uploadError, setUploadError] = useState("");
  const fileRef = useRef<HTMLInputElement>(null);

  useEffect(() => { api.getProfile().then(setP); }, []);
  if (!p) return <Spinner label="Loading profile…" />;

  const set = (k: string, v: any) => setP({ ...p, [k]: v });
  const csv = (arr: string[]) => (arr || []).join(", ");
  const fromCsv = (s: string) => s.split(",").map((x) => x.trim()).filter(Boolean);

  async function save() {
    const body = { ...p };
    await api.updateProfile(body); setSaved(true); setTimeout(() => setSaved(false), 1500);
  }
  async function upload(f?: File) {
    if (!f) return;
    setUploading(true); setUploadWarning(""); setUploadError("");
    try {
      const r = await api.uploadResume(f);
      setP(r.profile);
      if (r.warning) setUploadWarning(r.warning);
    } catch (e: any) {
      setUploadError(e.message || "Upload failed. Please try again.");
    } finally {
      setUploading(false);
      if (fileRef.current) fileRef.current.value = "";
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Profile</h1>
        <button className="btn-primary" onClick={save}>{saved ? "Saved ✓" : "Save"}</button>
      </div>

      <Section title="Resume">
        <input ref={fileRef} type="file" accept=".pdf,.docx" hidden
          onChange={(e) => upload(e.target.files?.[0])} />
        <div className="flex flex-wrap items-center gap-3">
          <button className="btn-ghost" onClick={() => fileRef.current?.click()}>
            {uploading ? "Parsing…" : "Upload PDF / DOCX"}</button>
          <span className="text-sm text-slate-500">
            {p.resume_filename || "No resume uploaded"}</span>
        </div>
        {uploadError && (
          <div className="mt-3 rounded-lg bg-red-50 p-3 text-sm text-red-700 dark:bg-red-900/30 dark:text-red-300">
            {uploadError}
          </div>
        )}
        {uploadWarning && (
          <div className="mt-3 rounded-lg bg-amber-50 p-3 text-sm text-amber-700 dark:bg-amber-900/30 dark:text-amber-300">
            {uploadWarning}
          </div>
        )}
        <textarea className="input mt-3 h-40 font-mono text-xs" value={p.resume_text || ""}
          onChange={(e) => set("resume_text", e.target.value)}
          placeholder="Parsed resume text appears here and can be edited…" />
      </Section>

      <div className="grid gap-6 md:grid-cols-2">
        <Section title="Education">
          <div className="grid grid-cols-2 gap-3">
            <div><label className="label">Degree</label><input className="input" value={p.degree || ""} onChange={(e) => set("degree", e.target.value)} /></div>
            <div><label className="label">GPA</label><input className="input" value={p.gpa ?? ""} onChange={(e) => set("gpa", parseFloat(e.target.value) || null)} /></div>
            <div><label className="label">Major</label><input className="input" value={p.major || ""} onChange={(e) => set("major", e.target.value)} /></div>
            <div><label className="label">Minor</label><input className="input" value={p.minor || ""} onChange={(e) => set("minor", e.target.value)} /></div>
            <div className="col-span-2"><label className="label">Graduation date</label><input type="date" className="input" value={p.graduation_date || ""} onChange={(e) => set("graduation_date", e.target.value)} /></div>
          </div>
        </Section>

        <Section title="Preferences">
          <div className="space-y-3">
            <div><label className="label">Skills (comma-separated)</label><input className="input" value={csv(p.skills)} onChange={(e) => set("skills", fromCsv(e.target.value))} /></div>
            <div><label className="label">Preferred locations</label><input className="input" value={csv(p.preferred_locations)} onChange={(e) => set("preferred_locations", fromCsv(e.target.value))} /></div>
            <div><label className="label">Desired industries</label><input className="input" value={csv(p.desired_industries)} onChange={(e) => set("desired_industries", fromCsv(e.target.value))} /></div>
            <div><label className="label">LinkedIn URL</label><input className="input" value={p.linkedin_url || ""} onChange={(e) => set("linkedin_url", e.target.value)} /></div>
            <div className="grid grid-cols-2 gap-3">
              <div><label className="label">Salary min</label><input className="input" value={p.salary_min ?? ""} onChange={(e) => set("salary_min", parseInt(e.target.value) || null)} /></div>
              <div><label className="label">Salary max</label><input className="input" value={p.salary_max ?? ""} onChange={(e) => set("salary_max", parseInt(e.target.value) || null)} /></div>
            </div>
          </div>
        </Section>

        <Section title="Work authorization">
          <div className="space-y-3">
            <div><label className="label">Visa status</label><input className="input" value={p.visa_status || ""} onChange={(e) => set("visa_status", e.target.value)} placeholder="F-1, J-1, ..." /></div>
            {[["opt_eligible", "OPT eligible"], ["stem_opt_eligible", "STEM OPT eligible"], ["requires_sponsorship", "Requires sponsorship"]].map(([k, lab]) => (
              <label key={k} className="flex items-center gap-2 text-sm">
                <input type="checkbox" checked={!!p[k]} onChange={(e) => set(k, e.target.checked)} /> {lab}
              </label>
            ))}
          </div>
        </Section>

        <Section title="Career goals">
          <textarea className="input h-32" value={p.career_goals || ""} onChange={(e) => set("career_goals", e.target.value)} placeholder="What roles and companies are you targeting?" />
        </Section>
      </div>
    </div>
  );
}
