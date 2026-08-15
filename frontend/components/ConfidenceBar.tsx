import React from "react";

interface ConfidenceBarProps {
  score?: number | null;
}

export default function ConfidenceBar({ score }: ConfidenceBarProps) {
  if (score === undefined || score === null) {
    return (
      <div className="text-xs text-slate-400 font-mono">
        Confidence Score: <span className="text-slate-400 italic">Not available</span>
      </div>
    );
  }

  // Handle score provided as 0.0-1.0 or 0-100
  const normalizedPercent = Math.min(
    Math.max(score > 1 ? score : score * 100, 0),
    100
  ).toFixed(1);

  const numericVal = parseFloat(normalizedPercent);

  let barColor = "from-cyan-500 to-emerald-400";
  let textColor = "text-emerald-400";

  if (numericVal < 70) {
    barColor = "from-amber-500 to-orange-400";
    textColor = "text-amber-400";
  } else if (numericVal < 50) {
    barColor = "from-rose-500 to-red-400";
    textColor = "text-rose-400";
  }

  return (
    <div className="space-y-1.5 w-full">
      <div className="flex justify-between items-center text-xs">
        <span className="text-slate-400 font-medium">Model Confidence</span>
        <span className={`font-mono font-bold ${textColor}`}>
          {normalizedPercent}%
        </span>
      </div>

      <div className="w-full h-2.5 rounded-full bg-[#080c14] border border-[#1e293b] overflow-hidden">
        <div
          className={`h-full bg-gradient-to-r ${barColor} transition-all duration-500 rounded-full shadow-[0_0_10px_rgba(6,182,212,0.4)]`}
          style={{ width: `${normalizedPercent}%` }}
        ></div>
      </div>
    </div>
  );
}
