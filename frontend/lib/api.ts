const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export function getToken(): string | null {
  if (typeof window === "undefined") return null;
  return window.localStorage.getItem("careeros_token");
}
export function setToken(t: string) { window.localStorage.setItem("careeros_token", t); }
export function clearToken() { window.localStorage.removeItem("careeros_token"); }

async function req(path: string, opts: RequestInit = {}) {
  const token = getToken();
  const headers: Record<string, string> = { ...(opts.headers as any) };
  if (token) headers["Authorization"] = `Bearer ${token}`;
  if (opts.body && !(opts.body instanceof FormData)) headers["Content-Type"] = "application/json";
  const res = await fetch(`${API}${path}`, { ...opts, headers });
  if (!res.ok) throw new Error((await res.json().catch(() => ({}))).detail || res.statusText);
  const ct = res.headers.get("content-type") || "";
  return ct.includes("application/json") ? res.json() : res.blob();
}

export const api = {
  login: (email: string, password: string) =>
    req("/api/auth/login", { method: "POST", body: JSON.stringify({ email, password }) }),
  signup: (email: string, password: string, name: string) =>
    req("/api/auth/signup", { method: "POST", body: JSON.stringify({ email, password, name }) }),
  me: () => req("/api/auth/me"),

  getProfile: () => req("/api/profile"),
  updateProfile: (p: any) => req("/api/profile", { method: "PUT", body: JSON.stringify(p) }),
  uploadResume: (file: File) => {
    const fd = new FormData(); fd.append("file", file);
    return req("/api/profile/resume", { method: "POST", body: fd });
  },

  analyze: (b: any) => req("/api/analyze", { method: "POST", body: JSON.stringify(b) }),
  optimizeResume: (b: any) => req("/api/resume/optimize", { method: "POST", body: JSON.stringify(b) }),
  applyFix: (rid: string, fixId: string) =>
    req(`/api/resume/${rid}/apply-fix`, { method: "POST", body: JSON.stringify({ fix_id: fixId }) }),
  coverLetter: (b: any) => req("/api/cover-letter", { method: "POST", body: JSON.stringify(b) }),
  research: (b: any) => req("/api/company/research", { method: "POST", body: JSON.stringify(b) }),
  interviewPrep: (b: any) => req("/api/interview/prep", { method: "POST", body: JSON.stringify(b) }),
  interviewFeedback: (b: any) => req("/api/interview/feedback", { method: "POST", body: JSON.stringify(b) }),
  hirevuePrep: (b: any) => req("/api/interview/hirevue", { method: "POST", body: JSON.stringify(b) }),
  sponsorship: (b: any) => req("/api/sponsorship", { method: "POST", body: JSON.stringify(b) }),
  networking: (b: any) => req("/api/networking", { method: "POST", body: JSON.stringify(b) }),
  strategy: () => req("/api/strategy"),

  apps: () => req("/api/applications"),
  createApp: (b: any) => req("/api/applications", { method: "POST", body: JSON.stringify(b) }),
  updateApp: (id: string, b: any) => req(`/api/applications/${id}`, { method: "PUT", body: JSON.stringify(b) }),
  deleteApp: (id: string) => req(`/api/applications/${id}`, { method: "DELETE" }),
  dashboard: () => req("/api/dashboard"),

  exportUrl: (kind: "resume" | "cover-letter", id: string, fmt: "pdf" | "docx") =>
    `${API}/api/${kind}/${id}/export.${fmt}`,

  downloadPackage: async (b: any, filename = "application_package.zip") => {
    const blob: Blob = await req("/api/analyze/package", { method: "POST", body: JSON.stringify(b) });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url; a.download = filename; document.body.appendChild(a); a.click();
    a.remove(); URL.revokeObjectURL(url);
  },
};
