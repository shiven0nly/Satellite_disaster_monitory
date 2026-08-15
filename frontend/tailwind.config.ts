import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        "space-bg": "#080c14",
        "space-sidebar": "#0e1424",
        "space-card": "#131b2e",
        "space-card-hover": "#1c263f",
        "space-border": "#1e293b",
        "space-accent": "#06b6d4",
        "space-accent-hover": "#0891b2",
        "space-violet": "#8b5cf6",
        "space-violet-hover": "#7c3aed",
        "space-emerald": "#10b981",
        "space-rose": "#f43f5e",
        "space-amber": "#f59e0b",
        "space-text": "#f8fafc",
        "space-text-muted": "#94a3b8",
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "-apple-system", "sans-serif"],
      },
    },
  },
  plugins: [],
};

export default config;
