"use client";
import React from "react";

export function ScoreRing({ value, label, size = 88 }:
  { value: number; label?: string; size?: number }) {
  const r = (size - 12) / 2, c = 2 * Math.PI * r;
  const pct = Math.max(0, Math.min(100, value));
  const color = pct >= 75 ? "#16a34a" : pct >= 50 ? "#d97706" : "#dc2626";
  return (
    <div className="flex flex-col items-center">
      <svg width={size} height={size} className="-rotate-90">
        <circle cx={size / 2} cy={size / 2} r={r} strokeWidth="8" fill="none"
          className="stroke-slate-200 dark:stroke-slate-800" />
        <circle cx={size / 2} cy={size / 2} r={r} strokeWidth="8" fill="none"
          stroke={color} strokeLinecap="round"
          strokeDasharray={c} strokeDashoffset={c - (pct / 100) * c} />
      </svg>
      <div className="-mt-[60px] text-center">
        <div className="text-2xl font-bold">{pct}</div>
      </div>
      {label && <div className="mt-9 text-xs font-medium text-slate-500">{label}</div>}
    </div>
  );
}

export function Badge({ level, children }:
  { level: "High" | "Medium" | "Low" | string; children: React.ReactNode }) {
  const map: Record<string, string> = {
    High: "bg-green-100 text-green-700 dark:bg-green-900/40 dark:text-green-300",
    Medium: "bg-amber-100 text-amber-700 dark:bg-amber-900/40 dark:text-amber-300",
    Low: "bg-red-100 text-red-700 dark:bg-red-900/40 dark:text-red-300",
  };
  return <span className={`chip ${map[level] || "bg-slate-100 text-slate-600 dark:bg-slate-700 dark:text-slate-300"}`}>{children}</span>;
}

export function Section({ title, children, right }:
  { title: string; children: React.ReactNode; right?: React.ReactNode }) {
  return (
    <div className="card">
      <div className="mb-3 flex items-center justify-between">
        <h3 className="text-sm font-semibold uppercase tracking-wide text-slate-500">{title}</h3>
        {right}
      </div>
      {children}
    </div>
  );
}

export function Spinner({ label }: { label?: string }) {
  return (
    <div className="flex items-center gap-3 text-sm text-slate-500">
      <span className="h-4 w-4 animate-spin rounded-full border-2 border-brand-500 border-t-transparent" />
      {label || "Working…"}
    </div>
  );
}
