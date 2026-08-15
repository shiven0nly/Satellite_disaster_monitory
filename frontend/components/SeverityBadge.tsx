import React from "react";
import { SeverityLevel } from "@/types";
import { getSeverityTheme } from "@/lib/severity";

interface SeverityBadgeProps {
  severity: SeverityLevel | string;
}

export default function SeverityBadge({ severity }: SeverityBadgeProps) {
  const normalizedKey = (severity || "MEDIUM").toUpperCase();
  const config = getSeverityTheme(severity);

  return (
    <span className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold uppercase tracking-wide border ${config.bg} ${config.text} ${config.border}`}>
      <span className={`w-2 h-2 rounded-full ${config.dot} animate-pulse`}></span>
      {normalizedKey} SEVERITY
    </span>
  );
}

