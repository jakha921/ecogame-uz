import type { SortingItem } from "@/data/sortingItems";

interface WasteItemProps {
  item: SortingItem;
  draggable: boolean;
}

export function WasteItem({ item, draggable }: WasteItemProps) {
  const handleDragStart = (e: React.DragEvent) => {
    e.dataTransfer.setData("itemId", item.id);
  };

  return (
    <div
      draggable={draggable}
      onDragStart={handleDragStart}
      className={[
        "flex flex-col items-center gap-2 bg-white rounded-2xl border-2 border-gray-200 p-6 shadow-sm",
        "select-none",
        draggable ? "cursor-grab active:cursor-grabbing hover:shadow-md hover:border-green-300 transition-all" : "opacity-50",
      ].join(" ")}
    >
      <span className="text-6xl">{item.emoji}</span>
      <p className="text-base font-semibold text-gray-700 text-center">{item.name_uz}</p>
      <p className="text-xs text-gray-400">Sudrab, idishga tashlang</p>
    </div>
  );
}
