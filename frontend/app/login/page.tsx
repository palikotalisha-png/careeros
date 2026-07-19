"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import { Sparkles, ShieldCheck, TrendingUp, Radar } from "lucide-react";
import { api, setToken } from "@/lib/api";

const FEATURES = [
  { icon: Radar, text: "Daily job discovery, scored and matched to your visa status" },
  { icon: TrendingUp, text: "ATS resume optimization tailored to every posting" },
  { icon: ShieldCheck, text: "Sponsorship intelligence — know before you apply" },
];

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
    <div className="mx-auto -mt-6 grid min-h-[calc(100vh-8rem)] max-w-5xl overflow-hidden rounded-3xl border border-slate-200/80 bg-white shadow-soft md:grid-cols-2 dark:border-slate-800 dark:bg-slate-900">
      {/* Left: brand panel */}
      <div className="relative hidden flex-col justify-between overflow-hidden bg-brand-gradient p-10 text-white md:flex">
        <div className="pointer-events-none absolute -right-24 -top-24 h-72 w-72 rounded-full bg-white/10 blur-3xl" />
        <div className="pointer-events-none absolute -bottom-32 -left-16 h-72 w-72 rounded-full bg-black/10 blur-3xl" />

        <div className="relative">
          <div className="mb-8 flex items-center gap-2 font-display text-lg font-bold">
            <span className="grid h-9 w-9 place-items-center rounded-xl bg-white/20 backdrop-blur">C</span>
            CareerOS
          </div>
          <h1 className="font-display text-3xl font-bold leading-tight">
            Your AI career copilot for the international job search.
          </h1>
          <p className="mt-3 text-sm text-white/80">
            One place to find sponsorship-friendly jobs, sharpen your resume, and land the offer —
            built specifically for F-1/OPT students.
          </p>
        </div>

        <ul className="relative space-y-4">
          {FEATURES.map(({ icon: Icon, text }, i) => (
            <li key={i} className="flex items-start gap-3 text-sm">
              <span className="mt-0.5 grid h-7 w-7 shrink-0 place-items-center rounded-lg bg-white/15">
                <Icon size={15} />
              </span>
              <span className="text-white/90">{text}</span>
            </li>
          ))}
        </ul>
      </div>

      {/* Right: form */}
      <div className="flex flex-col justify-center p-8 sm:p-12">
        <div className="mb-8 md:hidden">
          <div className="mb-3 flex items-center gap-2 font-display text-lg font-bold">
            <span className="grid h-9 w-9 place-items-center rounded-xl bg-brand-gradient text-white">C</span>
            CareerOS
          </div>
        </div>

        <div className="mb-6 flex items-center gap-2 text-xs font-semibold uppercase tracking-wide text-brand-600 dark:text-brand-400">
          <Sparkles size={14} />
          {mode === "login" ? "Welcome back" : "Get started free"}
        </div>
        <h2 className="mb-6 font-display text-2xl font-bold">
          {mode === "login" ? "Sign in to your account" : "Create your account"}
        </h2>

        <form onSubmit={submit} className="space-y-4">
          {mode === "signup" && (
            <div>
              <label className="label">Name</label>
              <input className="input" value={name} onChange={(e) => setName(e.target.value)} />
            </div>
          )}
          <div>
            <label className="label">Email</label>
            <input className="input" value={email} onChange={(e) => setEmail(e.target.value)} />
          </div>
          <div>
            <label className="label">Password</label>
            <input type="password" className="input" value={password}
              onChange={(e) => setPassword(e.target.value)} />
          </div>
          {err && (
            <p className="rounded-lg bg-red-50 px-3 py-2 text-sm text-red-700 dark:bg-red-900/30 dark:text-red-300">
              {err}
            </p>
          )}
          <button className="btn-primary w-full" disabled={loading}>
            {loading ? "…" : mode === "login" ? "Sign in" : "Create account"}
          </button>
          <p className="text-center text-sm text-slate-500">
            {mode === "login" ? "No account?" : "Have an account?"}{" "}
            <button type="button" className="font-semibold text-brand-600 hover:underline dark:text-brand-400"
              onClick={() => setMode(mode === "login" ? "signup" : "login")}>
              {mode === "login" ? "Sign up" : "Sign in"}
            </button>
          </p>
          <p className="text-center text-xs text-slate-400">Demo: demo@careeros.app / demo1234</p>
        </form>
      </div>
    </div>
  );
}
