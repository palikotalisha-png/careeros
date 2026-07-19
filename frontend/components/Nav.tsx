"use client";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { clearToken, getToken } from "@/lib/api";

const links = [
  { href: "/dashboard", label: "Dashboard" },
  { href: "/jobs", label: "Jobs" },
  { href: "/analyze", label: "Analyze a Job" },
  { href: "/tracker", label: "Tracker" },
  { href: "/profile", label: "Profile" },
];

export default function Nav() {
  const path = usePathname();
  const router = useRouter();
  const [dark, setDark] = useState(false);
  const [open, setOpen] = useState(false);

  useEffect(() => {
    const d = window.localStorage.getItem("careeros_dark") === "1";
    setDark(d); document.documentElement.classList.toggle("dark", d);
    if (!getToken() && path !== "/login") router.push("/login");
  }, [path, router]);

  function toggleDark() {
    const d = !dark; setDark(d);
    document.documentElement.classList.toggle("dark", d);
    window.localStorage.setItem("careeros_dark", d ? "1" : "0");
  }
  if (path === "/login") return null;

  return (
    <header className="sticky top-0 z-20 border-b border-slate-200 bg-white/80 backdrop-blur dark:border-slate-800 dark:bg-slate-950/80">
      <div className="mx-auto flex max-w-6xl items-center justify-between px-4 py-3">
        <Link href="/dashboard" className="flex items-center gap-2 font-bold">
          <span className="grid h-8 w-8 place-items-center rounded-lg bg-brand-600 text-white">C</span>
          CareerOS
        </Link>
        <nav className="hidden gap-1 md:flex">
          {links.map((l) => (
            <Link key={l.href} href={l.href}
              className={`rounded-lg px-3 py-2 text-sm font-medium ${
                path === l.href ? "bg-brand-50 text-brand-700 dark:bg-slate-800 dark:text-brand-300"
                : "text-slate-600 hover:bg-slate-100 dark:text-slate-300 dark:hover:bg-slate-800"}`}>
              {l.label}
            </Link>
          ))}
        </nav>
        <div className="flex items-center gap-2">
          <button onClick={toggleDark} className="btn-ghost px-2.5 py-2" aria-label="theme">
            {dark ? "☀" : "☾"}
          </button>
          <button onClick={() => { clearToken(); router.push("/login"); }}
            className="hidden btn-ghost md:inline-flex">Sign out</button>
          <button onClick={() => setOpen(!open)} className="btn-ghost px-2.5 py-2 md:hidden">≡</button>
        </div>
      </div>
      {open && (
        <nav className="flex flex-col gap-1 border-t border-slate-200 px-4 py-2 md:hidden dark:border-slate-800">
          {links.map((l) => (
            <Link key={l.href} href={l.href} onClick={() => setOpen(false)}
              className="rounded-lg px-3 py-2 text-sm font-medium text-slate-600 hover:bg-slate-100 dark:text-slate-300 dark:hover:bg-slate-800">
              {l.label}
            </Link>
          ))}
          <button onClick={() => { clearToken(); router.push("/login"); }}
            className="rounded-lg px-3 py-2 text-left text-sm text-slate-600">Sign out</button>
        </nav>
      )}
    </header>
  );
}
