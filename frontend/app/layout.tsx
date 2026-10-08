import "./globals.css";
import { AuthProvider } from "@/lib/auth";
export const metadata = { title: "Route 53 Management Console" };
export default function Root({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" data-theme="light">
      <body>
        <AuthProvider>{children}</AuthProvider>
      </body>
    </html>
  );
}
