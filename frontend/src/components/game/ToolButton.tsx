import type { ReactNode } from "react";

interface ToolButtonProps {
  icon: ReactNode;
  label: string;
  cost: number;
  isSelected: boolean;
  disabled: boolean;
  onClick: () => void;
}

export function ToolButton({ icon, label, cost, isSelected, disabled, onClick }: ToolButtonProps) {
  return (
    <button
      onClick={onClick}
      disabled={disabled}
      title={`${label} — ${cost} eco-coin`}
      className={[
        "flex flex-col items-center gap-1 px-3 py-2 rounded-xl border-2 transition-all select-none min-w-[72px]",
        isSelected
          ? "border-green-400 bg-green-900/80 text-green-300 shadow-lg shadow-green-900/50"
          : disabled
            ? "border-gray-700 bg-gray-800/60 text-gray-600 cursor-not-allowed opacity-60"
            : "border-gray-600 bg-gray-800/80 text-gray-300 hover:border-green-500 hover:text-green-300 hover:bg-gray-700/80",
      ].join(" ")}
    >
      <span className="text-xl">{icon}</span>
      <span className="text-[10px] font-medium leading-tight text-center">{label}</span>
      <span className="text-[9px] text-yellow-400 font-semibold">{cost}🪙</span>
    </button>
  );
}
