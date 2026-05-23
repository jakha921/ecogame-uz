interface HealthBarProps {
  label: string;
  value: number;
  icon?: string;
}

function getColor(value: number): string {
  if (value < 30) return "bg-red-500";
  if (value < 60) return "bg-yellow-400";
  return "bg-green-500";
}

export function HealthBar({ label, value, icon }: HealthBarProps) {
  const clamped = Math.min(100, Math.max(0, value));
  return (
    <div className="flex flex-col gap-1">
      <div className="flex items-center justify-between text-xs text-gray-500">
        <span>
          {icon} {label}
        </span>
        <span className="font-medium">{clamped.toFixed(0)}%</span>
      </div>
      <div className="w-full bg-gray-100 rounded-full h-3 overflow-hidden">
        <div
          className={`${getColor(clamped)} h-3 rounded-full transition-all duration-700`}
          style={{ width: `${clamped}%` }}
        />
      </div>
    </div>
  );
}
