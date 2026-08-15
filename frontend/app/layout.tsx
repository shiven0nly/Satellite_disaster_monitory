import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import Sidebar from "@/components/Sidebar";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Satellite Disaster Monitoring Dashboard",
  description: "AI-powered satellite, IR, and thermal disaster detection & analysis system",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark">
      <body className={`${inter.className} bg-[#080c14] text-slate-100 antialiased flex min-h-screen`}>
        {/* Persistent Sidebar Navigation */}
        <Sidebar />

        {/* Main Content Area */}
        <div className="flex-1 flex flex-col min-w-0 overflow-y-auto">
          {/* Header Bar */}
          <header className="h-16 border-b border-[#1e293b] bg-[#0e1424]/80 backdrop-blur-md px-8 flex items-center justify-between sticky top-0 z-10">
            <div className="flex items-center gap-3">
              <span className="w-2.5 h-2.5 rounded-full bg-cyan-400 animate-ping"></span>
              <span className="text-xs font-semibold tracking-wider uppercase text-cyan-400">
                Satellite Sensor Feed Active
              </span>
            </div>
            
            <div className="flex items-center gap-4 text-xs text-slate-400">
              <div className="px-3 py-1 rounded-md bg-[#131b2e] border border-[#1e293b] flex items-center gap-2">
                <span className="w-2 h-2 rounded-full bg-emerald-400"></span>
                <span>FastAPI Base: <code className="text-cyan-300">http://localhost:8000</code></span>
              </div>
            </div>
          </header>

          {/* Page Content Container */}
          <main className="flex-1 p-8">
            {children}
          </main>
        </div>
      </body>
    </html>
  );
}
