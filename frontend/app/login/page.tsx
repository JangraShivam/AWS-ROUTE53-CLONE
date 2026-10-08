"use client";
import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth";
export default function Login() {
  const { login } = useAuth(); const r = useRouter();
  const [e, setE] = useState(""); const [p, setP] = useState(""); const [err, setErr] = useState("");
  const go = async (ev: React.FormEvent) => { ev.preventDefault(); if (!e.includes("@") || !p) return setErr("Enter a valid email address and password."); try { await login(e, p); r.push("/route53/hosted-zones"); } catch (error: any) { setErr(error.message || "Unable to sign in."); } };
  return <div className="auth"><div className="logo">aws</div><form className="box" onSubmit={go}>
    <h1>Sign in</h1>
    <label><input type="radio" defaultChecked name="t" /> Root user <div className="hint" style={{ fontWeight: 400, marginLeft: 20 }}>Account owner that performs tasks requiring unrestricted access.</div></label>
    <label><input type="radio" name="t" /> IAM user <div className="hint" style={{ fontWeight: 400, marginLeft: 20 }}>User within an account that performs daily tasks.</div></label>
    <label>Email address<input className="f" value={e} onChange={x => setE(x.target.value)} placeholder="username@example.com" /></label>
    <label>Password<input className="f" type="password" value={p} onChange={x => setP(x.target.value)} /></label>
    {err && <div className="flash err" style={{ marginTop: 12 }}>{err}</div>}
    <button className="btn pri">Sign in</button>
    <p className="hint">New to AWS?</p><Link className="btn nrm" style={{ display: "block", textAlign: "center", width: "100%", padding: 7, borderRadius: 20 }} href="/signup">Create a new AWS account</Link>
  </form></div>;
}
