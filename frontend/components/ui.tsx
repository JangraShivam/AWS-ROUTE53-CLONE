"use client";
import { useEffect } from "react";
export function Modal({ title, children, onClose }: { title: string; children: React.ReactNode; onClose: () => void }) {
  useEffect(() => { const h = (e: KeyboardEvent) => e.key === "Escape" && onClose(); window.addEventListener("keydown", h); return () => window.removeEventListener("keydown", h); }, [onClose]);
  return <div className="ov" onMouseDown={onClose}><div className="modal" role="dialog" onMouseDown={e => e.stopPropagation()}><h2>{title}</h2>{children}</div></div>;
}
export type Msg = { ok: boolean; text: string } | null;
export function Flash({ msg, clear }: { msg: Msg; clear: () => void }) {
  useEffect(() => { if (msg) { const t = setTimeout(clear, 6000); return () => clearTimeout(t); } }, [msg, clear]);
  if (!msg) return null;
  return <div className={"flash" + (msg.ok ? "" : " err")} role="alert"><span>{msg.ok ? "✔" : "✖"}</span><span>{msg.text}</span><button className="x" onClick={clear}>✕</button></div>;
}
export function Pager({ page, pages, set }: { page: number; pages: number; set: (n: number) => void }) {
  return <div className="pg"><button disabled={page <= 1} onClick={() => set(page - 1)}>‹</button><b>{page}</b>{pages > 1 && <span>of {pages}</span>}<button disabled={page >= pages} onClick={() => set(page + 1)}>›</button></div>;
}
