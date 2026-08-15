import { SeverityLevel } from "@/types";

export interface SeverityTheme {
  name: string;
  hex: string;
  bg: string;
  text: string;
  border: string;
  dot: string;
  shadow: string;
}

export const severityColors: Record<string, SeverityTheme> = {
  LOW: {
    name: "Low",
    hex: "#3b82f6",
    bg: "bg-blue-500/15",
    text: "text-blue-300",
    border: "border-blue-500/30",
    dot: "bg-blue-400",
    shadow: "rgba(59, 130, 246, 0.5)",
  },
  MEDIUM: {
    name: "Medium",
    hex: "#f59e0b",
    bg: "bg-amber-500/15",
    text: "text-amber-300",
    border: "border-amber-500/30",
    dot: "bg-amber-400",
    shadow: "rgba(245, 158, 11, 0.5)",
  },
  HIGH: {
    name: "High",
    hex: "#f97316",
    bg: "bg-orange-500/15",
    text: "text-orange-300",
    border: "border-orange-500/30",
    dot: "bg-orange-400",
    shadow: "rgba(249, 115, 22, 0.5)",
  },
  CRITICAL: {
    name: "Critical",
    hex: "#f43f5e",
    bg: "bg-rose-500/15",
    text: "text-rose-300",
    border: "border-rose-500/30",
    dot: "bg-rose-400",
    shadow: "rgba(244, 63, 94, 0.6)",
  },
};

export function getSeverityTheme(severity?: SeverityLevel | string): SeverityTheme {
  const norm = (severity || "MEDIUM").toUpperCase();
  return severityColors[norm] || severityColors.MEDIUM;
}
