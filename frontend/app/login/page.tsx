"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import { api, setToken } from "@/lib/api";

export default function Login() {
  const router = useRouter();
  const [mode, setMode] = useState<"login" | "signup">("login");
  const [email, setEmail] = useState("demo@careeros.app");
  const [password, setPassword] = useState("demo1234");
  const [name, setName] = useState("");
  const [err, setErr] = useState("");
  const [loading, setLoading] = useState(false);

  async function submit(e: React.FormEvent) {
    e.preventDefault(); setErr(""); setLoading(true);
    try {
      const r = mode === "login"
        ? await api.login(email, password)
        : await api.signup(email, password, name);
      setToken(r.access_token);
      router.push("/dashboard");
    } catch (e: any) { setErr(e.message); } finally { setLoading(false); }
  }

  return (
    <div className="mx-auto mt-10 max-w-md">
      <div className="mb-6 text-center">
        <div className="mx-auto mb-3 grid h-12 w-12 place-items-center rounded-xl bg-brand-600 text-xl font-bold text-white">C</div>
        <h1 className="text-2xl font-bold">Welcome to CareerOS</h1>
        <p className="text-sm text-slate-500">Your AI job-application copilot.</p>
      </div>
      <form onSubmit={submit} className="card space-y-4">
        {mode === "signup" && (
          <div><label className="label">Name</label>
            <input className="input" value={name} onChange={(e) => setName(e.target.value)} /></div>
        )}
        <div><label className="label">Email</label>
          <input className="input" value={email} onChange={(e) => setEmail(e.target.value)} /></div>
        <div><label className="label">Password</label>
          <input type="password" className="input" value={password}
            onChange={(e) => setPassword(e.target.value)} /></div>
        {err && <p className="text-sm text-red-600">{err}</p>}
        <button className="btn-primary w-full" disabled={loading}>
          {loading ? "…" : mode === "login" ? "Sign in" : "Create account"}
        </button>
        <p className="text-center text-sm text-slate-500">
          {mode === "login" ? "No account?" : "Have an account?"}{" "}
          <button type="button" className="font-medium text-brand-600"
            onClick={() => setMode(mode === "login" ? "signup" : "login")}>
            {mode === "login" ? "Sign up" : "Sign in"}
          </button>
        </p>
        <p className="text-center text-xs text-slate-400">Demo: demo@careeros.app / demo1234</p>
      </form>
      <p className="mt-4 text-center text-xs text-slate-400">
        Production uses Clerk; this credential form is the dev fallback.
      </p>
    </div>
  );
}
