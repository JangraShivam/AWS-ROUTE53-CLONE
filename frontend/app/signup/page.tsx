"use client";
import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth";
export default function Signup() {
  const { signup } = useAuth(); const r = useRouter();
  const [f, setF] = useState({ email: "", account: "", pw: "", pw2: "" }); const [err, setErr] = useState("");
  const set = (k: string) => (x: React.ChangeEvent<HTMLInputElement>) => setF({ ...f, [k]: x.target.value });
  const go = async (ev: React.FormEvent) => { ev.preventDefault();
    if (!f.email.includes("@")) return setErr("Enter a valid email address.");
    if (!f.account) return setErr("Enter an AWS account name.");
    if (f.pw.length < 8) return setErr("Password must be at least 8 characters.");
    if (f.pw !== f.pw2) return setErr("Passwords don't match.");
    try { await signup(f.email, f.account, f.pw); r.push("/route53/hosted-zones"); } catch (error: any) { setErr(error.message || "Unable to create account."); } };
  return <div className="auth"><div className="logo">aws</div><form className="box" onSubmit={go}>
    <h1>Sign up for AWS</h1>
    <label>Root user email address<input className="f" value={f.email} onChange={set("email")} /></label>
    <label>AWS account name<input className="f" value={f.account} onChange={set("account")} /></label>
    <label>Password<input className="f" type="password" value={f.pw} onChange={set("pw")} /></label>
    <label>Confirm password<input className="f" type="password" value={f.pw2} onChange={set("pw2")} /></label>
    {err && <div className="flash err" style={{ marginTop: 12 }}>{err}</div>}
    <button className="btn pri">Verify email address</button>
    <p className="hint" style={{ textAlign: "center" }}>Already have an account? <Link href="/login">Sign in</Link></p>
  </form></div>;
}
