"use client";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useEffect } from "react";
import { useAuth } from "@/lib/auth";
const NAV: [string, [string, string][]][] = [
  ["", [["Dashboard", "dashboard"], ["Hosted zones", "hosted-zones"], ["Health checks", "health-checks"], ["Profiles", "profiles"]]],
  ["IP-based routing", [["CIDR collections", "cidr-collections"]]],
  ["Traffic flow", [["Traffic policies", "traffic-policies"], ["Policy records", "policy-records"]]],
  ["Domains", [["Registered domains", "registered-domains"], ["Requests", "requests"]]],
  ["Resolver", [["VPCs", "vpcs"], ["Inbound endpoints", "inbound-endpoints"], ["Outbound endpoints", "outbound-endpoints"], ["Rules", "rules"], ["Query logging", "query-logging"]]],
];
export default function Shell({ crumbs, children }: { crumbs: [string, string?][]; children: React.ReactNode }) {
  const { user, ready, logout } = useAuth(); const p = usePathname(); const r = useRouter();
  useEffect(() => { if (ready && !user) r.replace("/login"); }, [ready, user, r]);
  useEffect(() => {
    const h = (e: KeyboardEvent) => { const t = e.target as HTMLElement; if (/INPUT|TEXTAREA|SELECT/.test(t.tagName)) return;
      if (e.key === "/") { e.preventDefault(); document.querySelector<HTMLInputElement>("[data-search]")?.focus(); }
      if (e.key === "n") document.querySelector<HTMLButtonElement>("[data-new]")?.click();
      if (e.key === "g") r.push("/route53/hosted-zones"); };
    window.addEventListener("keydown", h); return () => window.removeEventListener("keydown", h);
  }, [r]);
  if (!user) return null;
  const toggle = () => { const t = document.documentElement.dataset.theme === "dark" ? "light" : "dark"; document.documentElement.dataset.theme = t; localStorage.setItem("r53_theme", t); };
  return <>
    <header className="top"><span className="logo">aws</span><input placeholder="Search   [Alt+S]" /><span className="sp" />
      <button onClick={toggle} title="Toggle dark mode">◐</button><span>Global ▾</span>
      <span>{user.account} ▾</span><button onClick={() => { logout(); r.push("/login"); }}>Sign out</button></header>
    <div className="crumb">{crumbs.map(([t, h], i) => <span key={i}>{i > 0 && <span style={{ marginRight: 10 }}>›</span>}{h ? <Link href={h}>{t}</Link> : <b style={{ fontWeight: 400 }}>{t}</b>}</span>)}</div>
    <div className="layout"><nav className="side"><h2>Route 53</h2>
      {NAV.map(([g, items]) => <div key={g}>{g && <div className="grp">▾ {g}</div>}{items.map(([l, s]) => <Link key={s} href={`/route53/${s}`} className={p.startsWith(`/route53/${s}`) ? "act" : ""}>{l}</Link>)}</div>)}
    </nav><main>{children}</main></div></>;
}
