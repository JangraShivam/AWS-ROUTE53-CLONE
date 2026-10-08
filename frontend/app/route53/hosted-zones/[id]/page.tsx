"use client";
import { useCallback, useEffect, useRef, useState } from "react";
import { useParams } from "next/navigation";
import Shell from "@/components/Shell";
import { Flash, Modal, Msg, Pager } from "@/components/ui";
import { api, Rec, RECORD_TYPES, Zone } from "@/lib/api";
const PER = 10; const blank = { name: "", type: "A", value: "", ttl: 300, routing_policy: "Simple routing" };
const dl = (name: string, text: string) => { const a = document.createElement("a"); a.href = URL.createObjectURL(new Blob([text])); a.download = name; a.click(); };
export default function ZonePage() {
  const id = String(useParams().id); const file = useRef<HTMLInputElement>(null);
  const [zone, setZone] = useState<Zone | null>(null); const [recs, setRecs] = useState<Rec[]>([]); const [q, setQ] = useState(""); const [tf, setTf] = useState(""); const [page, setPage] = useState(1);
  const [sel, setSel] = useState<string[]>([]); const [form, setForm] = useState<Partial<Rec> | null>(null); const [del, setDel] = useState<Rec[] | null>(null); const [details, setDetails] = useState<Rec | null>(null); const [msg, setMsg] = useState<Msg>(null);
  const load = () => { api.zone(id).then(setZone).catch(() => {}); api.records(id).then(setRecs).catch(e => setMsg({ ok: false, text: e.message })); };
  useEffect(load, [id]);
  const clear = useCallback(() => setMsg(null), []); const zn = zone?.name || "";
  const full = (n: string) => (n ? `${n}.${zn}` : zn);
  const rows = recs.filter(r => (!tf || r.type === tf) && (r.name + r.type + r.value).toLowerCase().includes(q.toLowerCase()));
  const pages = Math.max(1, Math.ceil(rows.length / PER)); const one = sel.length === 1 ? recs.find(r => r.id === sel[0]) : undefined;
  const save = async () => { if (!form) return; if (!form.value?.trim()) return setMsg({ ok: false, text: "Value is required." });
    try { form.id ? await api.updateRecord(id, form.id, form) : await api.createRecord(id, form); setMsg({ ok: true, text: `Record ${form.id ? "updated" : "created"} successfully.` }); setForm(null); setSel([]); load(); } catch (e: any) { setMsg({ ok: false, text: e.message }); } };
  const remove = async () => { if (!del) return; try { await Promise.all(del.map(r => api.deleteRecord(id, r.id))); setMsg({ ok: true, text: `Successfully deleted ${del.length} record(s).` }); setDel(null); setSel([]); load(); } catch (e: any) { setMsg({ ok: false, text: e.message }); } };
  const bind = () => `$ORIGIN ${zn}.\n` + recs.map(r => `${r.name || "@"}\t${r.ttl}\tIN\t${r.type}\t${r.value.split("\n").join(" ")}`).join("\n") + "\n";
  const importBind = async (f: File) => { let n = 0;
    for (const l of (await f.text()).split("\n")) { const m = l.trim().match(/^(\S+)\s+(\d+)\s+IN\s+(\S+)\s+(.+)$/i); if (!m || m[3].toUpperCase() === "SOA") continue;
      const name = m[1] === "@" ? "" : m[1].replace(new RegExp(`\\.?${zn.replace(/\./g, "\\.")}\\.?$`), "");
      try { await api.createRecord(id, { name, ttl: +m[2], type: m[3].toUpperCase(), value: m[4], routing_policy: "Simple routing" }); n++; } catch {} }
    setMsg({ ok: n > 0, text: n ? `Imported ${n} record(s) from zone file.` : "No valid records found in the file." }); load(); };
  const tog = (i: string) => setSel(s => s.includes(i) ? s.filter(x => x !== i) : [...s, i]);
  return <Shell crumbs={[["Route 53", "/route53/hosted-zones"], ["Hosted zones", "/route53/hosted-zones"], [zn || "…"]]}>
    <Flash msg={msg} clear={clear} /><h1>{zn}</h1><div className="hint">{zone?.type} hosted zone · ID {id}</div>
    <div className="card" style={{ marginTop: 16 }}>
      <div className="bar"><div className="grow"><h2>Records <span className="cnt">({recs.length})</span></h2></div>
        <button className="btn nrm" onClick={() => dl(`${zn}.json`, JSON.stringify(recs, null, 2))}>Export JSON</button>
        <button className="btn nrm" onClick={() => dl(`${zn}.zone`, bind())}>Export BIND</button>
        <button className="btn nrm" onClick={() => file.current?.click()}>Import BIND</button><input ref={file} type="file" hidden onChange={e => e.target.files?.[0] && importBind(e.target.files[0])} />
        <button className="btn nrm" disabled={!one} onClick={() => one && setDetails(one)}>View details</button>
        <button className="btn nrm" disabled={!one} onClick={() => one && setForm({ ...one })}>Edit record</button>
        <button className="btn nrm" disabled={!sel.length} onClick={() => setDel(recs.filter(r => sel.includes(r.id)))}>Delete record{sel.length > 1 ? "s" : ""}</button>
        <button data-new className="btn pri" onClick={() => setForm({ ...blank })}>Create record</button></div>
      <div className="bar"><input data-search className="f" style={{ maxWidth: 420 }} placeholder="Filter records by property or value  ( / )" value={q} onChange={e => { setQ(e.target.value); setPage(1); }} />
        <select className="f" style={{ width: 160 }} value={tf} onChange={e => { setTf(e.target.value); setPage(1); }}><option value="">Type: all</option>{RECORD_TYPES.map(t => <option key={t}>{t}</option>)}</select><span className="grow" /><Pager page={page} pages={pages} set={setPage} /></div>
      <table><thead><tr><th><input type="checkbox" checked={!!rows.length && rows.every(r => sel.includes(r.id))} onChange={e => setSel(e.target.checked ? rows.map(r => r.id) : [])} /></th><th>Record name</th><th>Type</th><th>Routing policy</th><th>Value/Route traffic to</th><th>TTL (seconds)</th><th>Actions</th></tr></thead><tbody>
        {rows.slice((page - 1) * PER, page * PER).map(r => <tr key={r.id} className={sel.includes(r.id) ? "sel" : ""} onClick={() => tog(r.id)} style={{ cursor: "pointer" }}><td><input type="checkbox" checked={sel.includes(r.id)} onClick={e => e.stopPropagation()} onChange={() => tog(r.id)} /></td>
          <td>{full(r.name)}</td><td>{r.type}</td><td>{r.routing_policy || "Simple"}</td><td style={{ whiteSpace: "pre-line" }}>{r.value}</td><td>{r.ttl}</td><td><div className="tbl-actions">
            <button className="linkbtn" onClick={e => { e.stopPropagation(); setDetails(r); }}>View details</button>
            <button className="linkbtn" onClick={e => { e.stopPropagation(); setForm({ ...r }); }}>Edit</button>
            <button className="linkbtn danger" onClick={e => { e.stopPropagation(); setDel([r]); }}>Delete</button>
          </div></td></tr>)}
        {!rows.length && <tr><td colSpan={7} style={{ textAlign: "center", padding: 40 }}>No records found. Choose Create record to add one.</td></tr>}</tbody></table></div>
    {details && <Modal title="Record details" onClose={() => setDetails(null)}>
      <div className="lab">Record name</div><div>{full(details.name)}</div>
      <div className="lab">Type</div><div>{details.type}</div>
      <div className="lab">Routing policy</div><div>{details.routing_policy || "Simple routing"}</div>
      <div className="lab">Value/Route traffic to</div><div style={{ whiteSpace: "pre-line" }}>{details.value}</div>
      <div className="lab">TTL (seconds)</div><div>{details.ttl}</div>
      <div className="lab">Record ID</div><div>{details.id}</div>
      <div className="ft"><button className="btn nrm" onClick={() => setDetails(null)}>Close</button><button className="btn pri" onClick={() => { setForm({ ...details }); setDetails(null); }}>Edit</button></div>
    </Modal>}
    {form && <Modal title={form.id ? "Edit record" : "Quick create record"} onClose={() => setForm(null)}>
      <div className="lab">Record name</div><div style={{ display: "flex", gap: 10, alignItems: "center" }}><input className="f" placeholder="subdomain" value={form.name || ""} onChange={e => setForm({ ...form, name: e.target.value })} /><span>{zn}</span></div><div className="hint">Keep blank to create a record for the root domain.</div>
      <div className="lab">Record type</div><select className="f" value={form.type} onChange={e => setForm({ ...form, type: e.target.value })}>{RECORD_TYPES.map(t => <option key={t}>{t}</option>)}</select>
      <div className="lab">Value</div><textarea className="f" rows={4} placeholder="192.0.2.235" value={form.value || ""} onChange={e => setForm({ ...form, value: e.target.value })} /><div className="hint">Enter multiple values on separate lines.</div>
      <div className="lab">TTL (seconds)</div><div style={{ display: "flex", gap: 8 }}><input className="f" type="number" min={0} value={form.ttl} onChange={e => setForm({ ...form, ttl: +e.target.value })} />{[["1m", 60], ["1h", 3600], ["1d", 86400]].map(([l, v]) => <button key={l} className="btn" onClick={() => setForm({ ...form, ttl: +v })}>{l}</button>)}</div><div className="hint">Recommended values: 60 to 172800 (two days)</div>
      <div className="lab">Routing policy</div><select className="f" value={form.routing_policy} onChange={e => setForm({ ...form, routing_policy: e.target.value })}>{["Simple routing", "Weighted", "Latency", "Failover", "Geolocation"].map(t => <option key={t}>{t}</option>)}</select>
      <div className="ft"><button className="btn nrm" onClick={() => setForm(null)}>Cancel</button><button className="btn pri" onClick={save}>{form.id ? "Save" : "Create records"}</button></div></Modal>}
    {del && <Modal title="Delete record" onClose={() => setDel(null)}><p>Delete {del.length} record(s)? This can&apos;t be undone.</p>
      <div className="ft"><button className="btn nrm" onClick={() => setDel(null)}>Cancel</button><button className="btn pri" onClick={remove}>Delete</button></div></Modal>}
  </Shell>;
}
