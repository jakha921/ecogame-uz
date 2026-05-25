import { Bird, Droplets, Leaf, Recycle, SunMedium } from "lucide-react";
import type { ActionCategory } from "@/api/types";

interface CategorySelectorProps {
  selected?: ActionCategory;
  onSelect: (category: ActionCategory) => void;
}

const CATEGORIES: {
  value: ActionCategory;
  label: string;
  icon: React.ReactNode;
  color: string;
}[] = [
  {
    value: "FLORA",
    label: "Flora",
    icon: <Leaf size={24} />,
    color: "text-green-600 bg-green-50 border-green-200 hover:border-green-500",
  },
  {
    value: "WATER",
    label: "Suv",
    icon: <Droplets size={24} />,
    color: "text-blue-600 bg-blue-50 border-blue-200 hover:border-blue-500",
  },
  {
    value: "WASTE",
    label: "Chiqindi",
    icon: <Recycle size={24} />,
    color: "text-yellow-600 bg-yellow-50 border-yellow-200 hover:border-yellow-500",
  },
  {
    value: "ENERGY",
    label: "Energiya",
    icon: <SunMedium size={24} />,
    color: "text-orange-600 bg-orange-50 border-orange-200 hover:border-orange-500",
  },
  {
    value: "FAUNA",
    label: "Fauna",
    icon: <Bird size={24} />,
    color: "text-purple-600 bg-purple-50 border-purple-200 hover:border-purple-500",
  },
];

export function CategorySelector({ selected, onSelect }: CategorySelectorProps) {
  return (
    <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
      {CATEGORIES.map((cat) => (
        <button
          key={cat.value}
          onClick={() => onSelect(cat.value)}
          className={[
            "border-2 rounded-xl p-4 flex flex-col items-center gap-2 transition-all",
            cat.color,
            selected === cat.value ? "ring-2 ring-offset-1 ring-current" : "",
          ].join(" ")}
        >
          {cat.icon}
          <span className="text-sm font-semibold">{cat.label}</span>
        </button>
      ))}
    </div>
  );
}
