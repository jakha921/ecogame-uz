import type { BinType } from "@/data/sortingItems";

interface WasteBinProps {
  binType: BinType;
  label: string;
  color: string;
  icon: string;
  onDrop: (binType: BinType) => void;
  isHighlighted: boolean;
  onTapSelect?: () => void;
}

export function WasteBin({ binType, label, color, icon, onDrop, isHighlighted, onTapSelect }: WasteBinProps) {
  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    onDrop(binType);
  };

  return (
    <div
      onDragOver={handleDragOver}
      onDrop={handleDrop}
      onClick={onTapSelect}
      className={[
        "flex flex-col items-center justify-center rounded-2xl border-4 p-4 gap-2 transition-all cursor-pointer min-h-[120px]",
        color,
        isHighlighted ? "scale-105 shadow-xl" : "hover:scale-102",
      ].join(" ")}
    >
      <span className="text-4xl">{icon}</span>
      <p className="text-sm font-bold text-center leading-tight">{label}</p>
    </div>
  );
}
