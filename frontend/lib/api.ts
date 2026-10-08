export const BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
export const EP = {
  login: "/auth/login",
  signup: "/auth/signup",
  logout: "/auth/logout",
  zones: "/hosted-zones/",
  zone: (id: string) => `/hosted-zones/${id}`,
  records: (z: string) => `/hosted-zones/${z}/records/`,
  record: (z: string, r: string) => `/hosted-zones/${z}/records/${r}`, // PUT, DELETE
};
export type Zone = { id: string; name: string; type: "Public" | "Private"; description?: string; record_count: number; created_by?: string };
export type Rec = { id: string; name: string; type: string; value: string; ttl: number; routing_policy?: string };
export const RECORD_TYPES = ["A","AAAA","CNAME","MX","TXT","PTR","SRV","NAPTR","CAA","NS","DS","SOA"];

type BackendZone = {
  id: number;
  domain_name: string;
  type: "Public" | "Private";
  description?: string | null;
  record_count: number;
};

type BackendRecord = {
  id: number;
  name: string;
  type: string;
  value: string;
  ttl: number;
  routing_policy: string;
};

const toZone = (zone: BackendZone): Zone => ({
  id: String(zone.id),
  name: zone.domain_name,
  type: zone.type,
  description: zone.description || "",
  record_count: zone.record_count,
  created_by: "Route 53",
});

const toRecord = (record: BackendRecord): Rec => ({
  id: String(record.id),
  name: record.name,
  type: record.type,
  value: record.value,
  ttl: record.ttl,
  routing_policy: record.routing_policy,
});

const zoneBody = (body: Partial<Zone>) => ({
  domain_name: body.name,
  type: body.type,
  description: body.description || null,
});

const recordBody = (body: Partial<Rec>) => ({
  name: body.name ?? "",
  type: body.type,
  value: body.value,
  ttl: body.ttl,
  routing_policy: body.routing_policy,
});

async function req<T>(path: string, method = "GET", body?: unknown): Promise<T> {
  const token = typeof window !== "undefined" ? localStorage.getItem("r53_token") : null;
  const r = await fetch(BASE + path, {
    method,
    credentials: "include",
    headers: { "Content-Type": "application/json", ...(token ? { Authorization: `Bearer ${token}` } : {}) },
    body: body ? JSON.stringify(body) : undefined,
  });
  if (!r.ok) {
    const text = await r.text();
    let detail = "";
    try {
      const data = JSON.parse(text);
      detail = data.detail;
    } catch {
      detail = "";
    }
    throw new Error(detail || text || r.statusText);
  }
  return r.status === 204 ? (undefined as T) : r.json();
}
export const api = {
  login: (b: object) => req<{ token: string }>(EP.login, "POST", b),
  signup: (b: object) => req<{ id: number; email: string; name: string }>(EP.signup, "POST", b),
  logout: () => req<void>(EP.logout, "POST"),
  zones: async () => (await req<BackendZone[]>(EP.zones)).map(toZone),
  zone: async (id: string) => toZone(await req<BackendZone>(EP.zone(id))),
  createZone: async (b: Partial<Zone>) => toZone(await req<BackendZone>(EP.zones, "POST", zoneBody(b))),
  updateZone: async (id: string, b: Partial<Zone>) => toZone(await req<BackendZone>(EP.zone(id), "PUT", zoneBody(b))),
  deleteZone: (id: string) => req<void>(EP.zone(id), "DELETE"),
  records: async (z: string) => (await req<BackendRecord[]>(EP.records(z))).map(toRecord),
  createRecord: async (z: string, b: Partial<Rec>) => toRecord(await req<BackendRecord>(EP.records(z), "POST", recordBody(b))),
  updateRecord: async (z: string, r: string, b: Partial<Rec>) => toRecord(await req<BackendRecord>(EP.record(z, r), "PUT", recordBody(b))),
  deleteRecord: (z: string, r: string) => req<void>(EP.record(z, r), "DELETE"),
};
