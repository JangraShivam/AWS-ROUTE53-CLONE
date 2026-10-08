"use client";
import { useParams } from "next/navigation";
import Shell from "@/components/Shell";
export default function Soon() {
  const s = String(useParams().section).replace(/-/g, " ");
  const t = s.charAt(0).toUpperCase() + s.slice(1);
  return <Shell crumbs={[["Route 53", "/route53/hosted-zones"], [t]]}><div className="soon"><h1>{t}</h1><p>Coming soon. This section isn&apos;t available yet.</p></div></Shell>;
}
