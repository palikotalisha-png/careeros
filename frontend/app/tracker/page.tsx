"use client";
import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { Badge, Spinner } from "@/components/ui";

const STATUSES = ["Saved", "Applying", "Applied", "Assessment", "Recruiter Screen",
  "Interview", "Final Round", "Follow-up", "Rejected", "Offer", "Accepted"];
const COLOR: Record<string, string> = {
  Saved: "bg-slate-100 text-slate-600 dark:bg-slate-700 dark:text-slate-300",
  Applying: "bg-blue-100 text-blue-700 dark:bg-blue-900/40 dark:text-blue-300",
  Applied: "bg-indigo-100 text-indigo-700 dark:bg-indigo-900/40 dark:text-indigo-300",
  Assessment: "bg-cyan-100 text-cyan-700 dark:bg-cyan-900/40 dark:text-cyan-300",
  "Recruiter Screen": "bg-teal-100 text-teal-700 dark:bg-teal-900/40 dark:text-teal-300",
  Interview: "bg-amber-100 text-amber-700 dark:bg-amber-900/40 dark:text-amber-300",
  "Final Round": "bg-orange-100 text-orange-700 dark:bg-orange-900/40 dark:text-orange-300",
  "Follow-up": "bg-purple-100 text-purple-700 dark:bg-purple-900/40 dark:text-purple-300",
  Rejected: "bg-red-100 text-red-700 dark:bg-red-900/40 dark:text-red-300",
  Offer: "bg-green-100 text-green-700 dark:bg-green-900/40 dark:text-green-300",
  Accepted: "bg-emerald-100 text-emerald-700 dark:bg-emerald-900/40 dark:text-emerald-300",
};
const REFERRAL_STATUSES = ["None", "Requested", "Received", "Declined"];

export default function Tracker() {
  const [apps, setApps] = useState<any[] | null>(null);
  const [edit, setEdit] = useState<any | null>(null);
  const load = () => api.apps().then(setApps);
  useEffect(() => { load(); }, []);

  async function save() {
    if (edit.id) await api.updateApp(edit.id, edit);
    else await api.createApp(edit);
    setEdit(null); load();
  }
  async function quickStatus(a: any, status: string) { await api.updateApp(a.id, { ...a, status }); load(); }
  async function del(id: string) { await api.deleteApp(id); load(); }

  if (!apps) return <Spinner label="Loading tracker…" />;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Application Tracker</h1>
        <button className="btn-primary" onClick={() => setEdit({ company: "", job_title: "", status: "Saved" })}>+ Add</button>
      </div>

      <div className="card overflow-x-auto p-0">
        <table className="w-full text-sm">
          <thead className="border-b border-slate-200 text-left text-xs uppercase text-slate-500 dark:border-slate-700">
            <tr>{["Company", "Role", "Status", "Deadline", "Salary", "Sponsorship", "Referral", "Documents", ""].map((h) =>
              <th key={h} className="px-4 py-3">{h}</th>)}</tr>
          </thead>
          <tbody>
            {apps.length === 0 && <tr><td colSpan={9} className="px-4 py-8 text-center text-slate-400">No applications yet. Analyze a job to add one.</td></tr>}
            {apps.map((a) => (
              <tr key={a.id} className="border-b border-slate-100 dark:border-slate-700/60">
                <td className="px-4 py-3 font-medium">{a.company}</td>
                <td className="px-4 py-3">{a.job_title}</td>
                <td className="px-4 py-3">
                  <select value={a.status} onChange={(e) => quickStatus(a, e.target.value)}
                    className={`chip cursor-pointer border-0 ${COLOR[a.status]}`}>
                    {STATUSES.map((s) => <option key={s}>{s}</option>)}
                  </select>
                </td>
                <td className="px-4 py-3 text-slate-500">{a.deadline || "—"}</td>
                <td className="px-4 py-3 text-slate-500">{a.salary || "—"}</td>
                <td className="px-4 py-3 text-slate-500">
                  {a.sponsorship_available === true ? "Yes" : a.sponsorship_available === false ? "No" : "—"}
                </td>
                <td className="px-4 py-3 text-slate-500">{a.referral_status || "None"}</td>
                <td className="px-4 py-3">
                  <div className="flex flex-col gap-1 text-xs">
                    {a.resume_version_id ? (
                      <span className="flex gap-1.5">
                        Resume:
                        <a className="text-brand-600 hover:underline" href={api.exportUrl("resume", a.resume_version_id, "pdf")} target="_blank">PDF</a>
                        <a className="text-brand-600 hover:underline" href={api.exportUrl("resume", a.resume_version_id, "docx")} target="_blank">DOCX</a>
                      </span>
                    ) : <span className="text-slate-400">No resume saved</span>}
                    {a.cover_letter_id ? (
                      <span className="flex gap-1.5">
                        Cover letter:
                        <a className="text-brand-600 hover:underline" href={api.exportUrl("cover-letter", a.cover_letter_id, "pdf")} target="_blank">PDF</a>
                        <a className="text-brand-600 hover:underline" href={api.exportUrl("cover-letter", a.cover_letter_id, "docx")} target="_blank">DOCX</a>
                      </span>
                    ) : <span className="text-slate-400">No cover letter saved</span>}
                  </div>
                </td>
                <td className="px-4 py-3 text-right">
                  <button className="text-xs text-brand-600" onClick={() => setEdit(a)}>Edit</button>
                  <button className="ml-3 text-xs text-red-500" onClick={() => del(a.id)}>Delete</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {edit && (
        <div className="fixed inset-0 z-30 grid place-items-center bg-black/40 p-4" onClick={() => setEdit(null)}>
          <div className="card w-full max-w-lg" onClick={(e) => e.stopPropagation()}>
            <h3 className="mb-4 text-lg font-bold">{edit.id ? "Edit" : "Add"} application</h3>
            <div className="max-h-[70vh] overflow-y-auto pr-1">
            <div className="grid grid-cols-2 gap-3">
              <div className="col-span-2"><label className="label">Company</label><input className="input" value={edit.company || ""} onChange={(e) => setEdit({ ...edit, company: e.target.value })} /></div>
              <div className="col-span-2"><label className="label">Job title</label><input className="input" value={edit.job_title || ""} onChange={(e) => setEdit({ ...edit, job_title: e.target.value })} /></div>
              <div><label className="label">Location</label><input className="input" value={edit.location || ""} onChange={(e) => setEdit({ ...edit, location: e.target.value })} /></div>
              <div><label className="label">Salary</label><input className="input" value={edit.salary || ""} onChange={(e) => setEdit({ ...edit, salary: e.target.value })} placeholder="$120k–$140k" /></div>
              <div><label className="label">Status</label><select className="input" value={edit.status} onChange={(e) => setEdit({ ...edit, status: e.target.value })}>{STATUSES.map((s) => <option key={s}>{s}</option>)}</select></div>
              <div><label className="label">Deadline</label><input type="date" className="input" value={edit.deadline || ""} onChange={(e) => setEdit({ ...edit, deadline: e.target.value })} /></div>
              <div><label className="label">Date applied</label><input type="date" className="input" value={edit.date_applied || ""} onChange={(e) => setEdit({ ...edit, date_applied: e.target.value })} /></div>
              <div><label className="label">Interview date</label><input type="date" className="input" value={edit.interview_date || ""} onChange={(e) => setEdit({ ...edit, interview_date: e.target.value })} /></div>
              <div><label className="label">Follow-up date</label><input type="date" className="input" value={edit.follow_up_date || ""} onChange={(e) => setEdit({ ...edit, follow_up_date: e.target.value })} /></div>
              <div><label className="label">Recruiter name</label><input className="input" value={edit.recruiter || ""} onChange={(e) => setEdit({ ...edit, recruiter: e.target.value })} /></div>
              <div className="col-span-2"><label className="label">Recruiter LinkedIn</label><input className="input" value={edit.recruiter_linkedin || ""} onChange={(e) => setEdit({ ...edit, recruiter_linkedin: e.target.value })} placeholder="https://linkedin.com/in/…" /></div>
              <div><label className="label">Referral status</label><select className="input" value={edit.referral_status || "None"} onChange={(e) => setEdit({ ...edit, referral_status: e.target.value })}>{REFERRAL_STATUSES.map((s) => <option key={s}>{s}</option>)}</select></div>
              <div><label className="label">Sponsorship available</label>
                <select className="input" value={edit.sponsorship_available === true ? "yes" : edit.sponsorship_available === false ? "no" : ""}
                  onChange={(e) => setEdit({ ...edit, sponsorship_available: e.target.value === "" ? null : e.target.value === "yes" })}>
                  <option value="">Unknown</option><option value="yes">Yes</option><option value="no">No</option>
                </select>
              </div>
              <div><label className="label">E-Verify</label>
                <select className="input" value={edit.e_verify === true ? "yes" : edit.e_verify === false ? "no" : ""}
                  onChange={(e) => setEdit({ ...edit, e_verify: e.target.value === "" ? null : e.target.value === "yes" })}>
                  <option value="">Unknown</option><option value="yes">Yes</option><option value="no">No</option>
                </select>
              </div>
              <div><label className="label">Work auth notes</label><input className="input" value={edit.work_auth_notes || ""} onChange={(e) => setEdit({ ...edit, work_auth_notes: e.target.value })} placeholder="e.g. requires GC/citizen" /></div>
              <div className="col-span-2"><label className="label">Notes</label><textarea className="input h-20" value={edit.notes || ""} onChange={(e) => setEdit({ ...edit, notes: e.target.value })} /></div>
            </div>
            </div>
            <div className="mt-4 flex justify-end gap-2">
              <button className="btn-ghost" onClick={() => setEdit(null)}>Cancel</button>
              <button className="btn-primary" onClick={save}>Save</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
