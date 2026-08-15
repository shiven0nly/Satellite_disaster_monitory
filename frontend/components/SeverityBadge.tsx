import React from "react";
import { SeverityLevel } from "@/types";

interface SeverityBadgeProps {
  severity: SeverityLevel | string;
}

const severityConfig: Record<string, { bg: string; text: string; border: string; dot: string }> = {
  LOW: {
    bg: "bg-blue-500/15",
    text: "text-blue-300",
    border: "border-blue-500/30",
    dot: "bg-blue-400",
  },
  MEDIUM: {
    bg: "bg-amber-500/15",
    text: "text-amber-300",
    border: "border-amber-500/30",
    dot: "bg-amber-400",
  },
  HIGH: {
    bg: "bg-orange-500/15",
    text: "text-orange-300",
    border: "border-orange-500/30",
    dot: "bg-orange-400",
  },
  CRITICAL: {
    bg: "bg-rose-500/15",
    text: "text-rose-300",
    border: "border-rose-500/30",
    dot: "bg-rose-400",
  },
};

export default function SeverityBadge({ severity }: SeverityBadgeProps) {
  const normalizedKey = (severity || "MEDIUM").toUpperCase();
  const config = severityConfig[normalizedKey] || severityConfig.MEDIUM;

  return (
    <span className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold uppercase tracking-wide border ${config.bg} ${config.text} ${config.border}`}>
      <span className={`w-2 h-2 rounded-full ${config.dot} animate-pulse`}></span>
      {normalizedKey} SEVERITY
    </span>
  );
}
