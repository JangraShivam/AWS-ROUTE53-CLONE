"use client";
import { createContext, useContext, useEffect, useState } from "react";
import { api } from "./api";
type U = { email: string; account: string } | null;
const Ctx = createContext<any>(null);
export const useAuth = () => useContext(Ctx);
export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<U>(null);
  const [ready, setReady] = useState(false);
  useEffect(() => {
    try { const s = localStorage.getItem("r53_session"); if (s) setUser(JSON.parse(s)); } catch {}
    setReady(true);
    document.documentElement.dataset.theme = localStorage.getItem("r53_theme") || "light";
  }, []);
  const start = (u: NonNullable<U>, token?: string) => { localStorage.setItem("r53_session", JSON.stringify(u)); if (token) localStorage.setItem("r53_token", token); setUser(u); };
  const login = async (email: string, password: string) => { const { token } = await api.login({ email, password }); start({ email, account: "Route53 Console" }, token); };
  const signup = async (email: string, account: string, password: string) => { await api.signup({ email, name: account, password }); const { token } = await api.login({ email, password }); start({ email, account }, token); };
  const logout = async () => { try { await api.logout(); } catch {} localStorage.removeItem("r53_session"); localStorage.removeItem("r53_token"); setUser(null); };
  return <Ctx.Provider value={{ user, ready, login, signup, logout }}>{children}</Ctx.Provider>;
}
