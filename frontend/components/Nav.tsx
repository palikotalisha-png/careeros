"use client";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { LayoutDashboard, Radar, FileSearch, ClipboardList, UserCircle, Sun, Moon, LogOut, Menu } from "lucide-react";
import { clearToken, getToken } from "@/lib/api";

const links = [
  { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { href: "/jobs", label: "Jobs", icon: Radar },
  { href: "/analyze", label: "Analyze a Job", icon: FileSearch },
  { href: "/tracker", label: "Tracker", icon: ClipboardList },
  { href: "/profile", label: "Profile", icon: UserCircle },
];

export default function Nav() {
  const path = usePathname();
  const router = useRouter();
  const [dark, setDark] = useState(false);
  const [open, setOpen] = useState(false);

  useEffect(() => {
    const stored = window.localStorage.getItem("careeros_dark");
    const d = stored === null ? true : stored === "1";   // dark by default
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
    <header className="sticky top-0 z-20 border-b border-slate-200/80 bg-white/80 backdrop-blur-md dark:border-slate-700 dark:bg-slate-800/80">
      <div className="mx-auto flex max-w-6xl items-center justify-between px-4 py-3">
        <Link href="/dashboard" className="flex items-center gap-2 font-display font-bold">
          <span className="grid h-8 w-8 place-items-center rounded-lg bg-brand-gradient text-sm text-white shadow-glow">C</span>
          CareerOS
        </Link>
        <nav className="hidden gap-1 md:flex">
          {links.map((l) => {
            const Icon = l.icon;
            const active = path === l.href;
            return (
              <Link key={l.href} href={l.href}
                className={`flex items-center gap-1.5 rounded-lg px-3 py-2 text-sm font-medium transition ${
                  active ? "bg-brand-50 text-brand-700 dark:bg-brand-500/10 dark:text-brand-300"
                  : "text-slate-600 hover:bg-slate-100 dark:text-slate-300 dark:hover:bg-slate-700"}`}>
                <Icon size={15} strokeWidth={2.25} />
                {l.label}
              </Link>
            );
          })}
        </nav>
        <div className="flex items-center gap-2">
          <button onClick={toggleDark} className="btn-ghost px-2.5 py-2" aria-label="theme">
            {dark ? <Sun size={16} /> : <Moon size={16} />}
          </button>
          <button onClick={() => { clearToken(); router.push("/login"); }}
            className="hidden items-center gap-1.5 btn-ghost md:inline-flex">
            <LogOut size={15} /> Sign out
          </button>
          <button onClick={() => setOpen(!open)} className="btn-ghost px-2.5 py-2 md:hidden" aria-label="menu">
            <Menu size={16} />
          </button>
        </div>
      </div>
      {open && (
        <nav className="flex flex-col gap-1 border-t border-slate-200 px-4 py-2 md:hidden dark:border-slate-700">
          {links.map((l) => {
            const Icon = l.icon;
            return (
              <Link key={l.href} href={l.href} onClick={() => setOpen(false)}
                className="flex items-center gap-2 rounded-lg px-3 py-2 text-sm font-medium text-slate-600 hover:bg-slate-100 dark:text-slate-300 dark:hover:bg-slate-700">
                <Icon size={15} /> {l.label}
              </Link>
            );
          })}
          <button onClick={() => { clearToken(); router.push("/login"); }}
            className="flex items-center gap-2 rounded-lg px-3 py-2 text-left text-sm text-slate-600 dark:text-slate-300">
            <LogOut size={15} /> Sign out
          </button>
        </nav>
      )}
    </header>
  );
}
