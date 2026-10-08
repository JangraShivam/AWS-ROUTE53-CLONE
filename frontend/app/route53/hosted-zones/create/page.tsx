"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import Shell from "@/components/Shell";
import { Flash, Msg } from "@/components/ui";
import { api } from "@/lib/api";
export default function Create() {
  const r = useRouter();
  const [name, setName] = useState("");
  const [desc, setDesc] = useState("");
  const [type, setType] = useState<"Public" | "Private">("Public");
  const [msg, setMsg] = useState<Msg>(null);
  const go = async () => {
    if (!/^[a-z0-9-]+(\.[a-z0-9-]+)+$/i.test(name))
      return setMsg({
        ok: false,
        text: "Enter a valid domain name, such as example.com.",
      });
    try {
      await api.createZone({ name, description: desc, type });
      r.push("/route53/hosted-zones");
    } catch (e: any) {
      setMsg({ ok: false, text: e.message });
    }
  };
  const opt = (t: "Public" | "Private", d: string) => (
    <label
      className="card"
      style={{
        flex: 1,
        margin: 0,
        padding: "10px 16px",
        borderColor: type === t ? "var(--link)" : undefined,
        cursor: "pointer",
      }}
    >
      <input type="radio" checked={type === t} onChange={() => setType(t)} />{" "}
      <b>{t} hosted zone</b>
      <div className="hint">{d}</div>
    </label>
  );
  return (
    <Shell
      crumbs={[
        ["Route 53", "/route53/hosted-zones"],
        ["Hosted zones", "/route53/hosted-zones"],
        ["Create hosted zone"],
      ]}
    >
      <Flash msg={msg} clear={() => setMsg(null)} />
      <h1>Create hosted zone</h1>
      <br />
      <div className="card">
        <h2>Hosted zone configuration</h2>
        <div className="hint">
          A hosted zone is a container that holds information about how you want
          to route traffic for a domain, such as example.com, and its
          subdomains.
        </div>
        <div className="lab">Domain name</div>
        <div className="hint">
          This is the name of the domain that you want to route traffic for.
        </div>
        <input
          className="f"
          placeholder="example.com"
          value={name}
          onChange={(e) => setName(e.target.value)}
        />
        <div className="lab">
          Description - <i>optional</i>
        </div>
        <div className="hint">
          This value lets you distinguish hosted zones that have the same name.
        </div>
        <textarea
          className="f"
          rows={3}
          maxLength={256}
          placeholder="The hosted zone is used for..."
          value={desc}
          onChange={(e) => setDesc(e.target.value)}
        />
        <div className="hint">
          The description can have up to 256 characters. {desc.length}/256
        </div>
        <div className="lab">Type</div>
        <div className="hint">
          The type indicates whether you want to route traffic on the internet
          or in an Amazon VPC.
        </div>
        <div style={{ display: "flex", gap: 16, marginTop: 6 }}>
          {opt(
            "Public",
            "A public hosted zone determines how traffic is routed on the internet.",
          )}
          {opt(
            "Private",
            "A private hosted zone determines how traffic is routed within an Amazon VPC.",
          )}
        </div>
      </div>
      <div className="bar" style={{ justifyContent: "flex-end" }}>
        <button
          className="btn nrm"
          onClick={() => r.push("/route53/hosted-zones")}
        >
          Cancel
        </button>
        <button className="btn pri" onClick={go}>
          Create hosted zone
        </button>
      </div>
    </Shell>
  );
}
