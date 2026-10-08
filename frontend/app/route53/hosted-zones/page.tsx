"use client";
import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import Shell from "@/components/Shell";
import { Flash, Modal, Msg, Pager } from "@/components/ui";
import { api, Zone } from "@/lib/api";
const PER = 10;
export default function Zones() {
  const r = useRouter();
  const [zones, setZones] = useState<Zone[]>([]);
  const [q, setQ] = useState("");
  const [page, setPage] = useState(1);
  const [sel, setSel] = useState<string | null>(null);
  const [msg, setMsg] = useState<Msg>(null);
  const [edit, setEdit] = useState<Zone | null>(null);
  const [del, setDel] = useState<Zone | null>(null);
  const [confirm, setConfirm] = useState("");
  const load = () =>
    api
      .zones()
      .then(setZones)
      .catch((e) =>
        setMsg({
          ok: false,
          text: "Failed to load hosted zones: " + e.message,
        }),
      );
  useEffect(() => {
    load();
  }, []);
  const rows = zones.filter((z) =>
    (z.name + z.type + (z.description || ""))
      .toLowerCase()
      .includes(q.toLowerCase()),
  );
  const pages = Math.max(1, Math.ceil(rows.length / PER));
  const cur = zones.find((z) => z.id === sel);
  const clear = useCallback(() => setMsg(null), []);
  const save = async () => {
    if (!edit) return;
    try {
      await api.updateZone(edit.id, edit);
      setMsg({ ok: true, text: `Hosted zone ${edit.name} was updated.` });
      setEdit(null);
      load();
    } catch (e: any) {
      setMsg({ ok: false, text: e.message });
    }
  };
  const remove = async () => {
    if (!del) return;
    try {
      await api.deleteZone(del.id);
      setMsg({
        ok: true,
        text: `Successfully deleted hosted zone ${del.name}.`,
      });
      setDel(null);
      setConfirm("");
      setSel(null);
      load();
    } catch (e: any) {
      setMsg({ ok: false, text: e.message });
    }
  };
  return (
    <Shell crumbs={[["Route 53", "/route53/hosted-zones"], ["Hosted zones"]]}>
      <Flash msg={msg} clear={clear} />
      <div className="bar">
        <div className="grow">
          <h1>
            Hosted zones <span className="cnt">({zones.length})</span>
          </h1>
          <div className="hint">
            Automatic mode is the current search behavior optimized for best
            filter results.
          </div>
        </div>
        <button
          className="btn nrm"
          disabled={!cur}
          onClick={() => cur && r.push(`/route53/hosted-zones/${cur.id}`)}
        >
          View details
        </button>
        <button
          className="btn nrm"
          disabled={!cur}
          onClick={() => cur && setEdit({ ...cur })}
        >
          Edit
        </button>
        <button
          className="btn nrm"
          disabled={!cur}
          onClick={() => cur && setDel(cur)}
        >
          Delete
        </button>
        <button
          data-new
          className="btn pri"
          onClick={() => r.push("/route53/hosted-zones/create")}
        >
          Create hosted zone
        </button>
      </div>
      <div className="bar">
        <input
          data-search
          className="f"
          style={{ maxWidth: 520 }}
          placeholder="Filter records by property or value  ( / )"
          value={q}
          onChange={(e) => {
            setQ(e.target.value);
            setPage(1);
          }}
        />
        <span className="grow" />
        <Pager page={page} pages={pages} set={setPage} />
      </div>
      <table>
        <thead>
          <tr>
            <th />
            <th>Hosted zone name</th>
            <th>Type</th>
            <th>Created by</th>
            <th>Record count</th>
            <th>Description</th>
            <th>Hosted zone ID</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {rows.slice((page - 1) * PER, page * PER).map((z) => (
            <tr
              key={z.id}
              className={sel === z.id ? "sel" : ""}
              onClick={() => setSel(z.id)}
              style={{ cursor: "pointer" }}
            >
              <td>
                <input
                  type="radio"
                  checked={sel === z.id}
                  onClick={(e) => e.stopPropagation()}
                  onChange={() => setSel(z.id)}
                />
              </td>
              <td>
                <Link
                  href={`/route53/hosted-zones/${z.id}`}
                  onClick={(e) => e.stopPropagation()}
                >
                  {z.name}
                </Link>
              </td>
              <td>{z.type}</td>
              <td>{z.created_by || "Route 53"}</td>
              <td>{z.record_count}</td>
              <td>{z.description || "-"}</td>
              <td>{z.id}</td>
              <td>
                <div className="tbl-actions">
                  <button
                    className="linkbtn"
                    onClick={(e) => {
                      e.stopPropagation();
                      r.push(`/route53/hosted-zones/${z.id}`);
                    }}
                  >
                    View details
                  </button>
                  <button
                    className="linkbtn"
                    onClick={(e) => {
                      e.stopPropagation();
                      setEdit({ ...z });
                    }}
                  >
                    Edit
                  </button>
                  <button
                    className="linkbtn danger"
                    onClick={(e) => {
                      e.stopPropagation();
                      setDel(z);
                    }}
                  >
                    Delete
                  </button>
                </div>
              </td>
            </tr>
          ))}
          {!rows.length && (
            <tr>
              <td colSpan={8} style={{ textAlign: "center", padding: 40 }}>
                {zones.length
                  ? "No matches. Try a different filter."
                  : "No hosted zones. Choose Create hosted zone to add one."}
              </td>
            </tr>
          )}
        </tbody>
      </table>
      {edit && (
        <Modal title="Edit hosted zone" onClose={() => setEdit(null)}>
          <div className="lab">Hosted zone name</div>
          <input
            className="f"
            value={edit.name}
            onChange={(e) => setEdit({ ...edit, name: e.target.value })}
          />
          <div className="lab">Type</div>
          <select
            className="f"
            value={edit.type}
            onChange={(e) =>
              setEdit({ ...edit, type: e.target.value as "Public" | "Private" })
            }
          >
            <option>Public</option>
            <option>Private</option>
          </select>
          <div className="lab">Description - optional</div>
          <textarea
            className="f"
            rows={3}
            maxLength={256}
            value={edit.description || ""}
            onChange={(e) => setEdit({ ...edit, description: e.target.value })}
          />
          <div className="ft">
            <button className="btn nrm" onClick={() => setEdit(null)}>
              Cancel
            </button>
            <button className="btn pri" onClick={save}>
              Save
            </button>
          </div>
        </Modal>
      )}
      {del && (
        <Modal
          title={`Delete ${del.name}`}
          onClose={() => {
            setDel(null);
            setConfirm("");
          }}
        >
          <p>
            This permanently deletes the hosted zone and all of its records.
          </p>
          <div className="lab">
            Type <i>delete</i> to confirm
          </div>
          <input
            className="f"
            value={confirm}
            onChange={(e) => setConfirm(e.target.value)}
            placeholder="delete"
          />
          <div className="ft">
            <button
              className="btn nrm"
              onClick={() => {
                setDel(null);
                setConfirm("");
              }}
            >
              Cancel
            </button>
            <button
              className="btn pri"
              disabled={confirm !== "delete"}
              onClick={remove}
            >
              Delete
            </button>
          </div>
        </Modal>
      )}
    </Shell>
  );
}
