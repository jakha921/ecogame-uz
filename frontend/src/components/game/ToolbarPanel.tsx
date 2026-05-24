import { useEffect, useState } from "react";
import {
  Bird,
  Coins,
  Droplets,
  Fish,
  Flower2,
  Leaf,
  Recycle,
  ShieldCheck,
  Shovel,
  SunMedium,
  Trash2,
  TreeDeciduous,
  Waves,
  Zap,
} from "lucide-react";
import { EVENTS, EventBus } from "@/game/events/EventBus";
import type { ResourcesChangedPayload } from "@/game/events/EventBus";
import { ACTION_COST } from "@/game/data/constants";
import { useGameStore } from "@/stores/gameStore";
import { ToolButton } from "./ToolButton";

// ─── Icon mapping (action_key → lucide icon) ─────────────────────────────────

const ACTION_ICONS: Record<string, React.ReactNode> = {
  plant_tree: <TreeDeciduous size={20} />,
  plant_flowers: <Flower2 size={20} />,
  care_garden: <Shovel size={20} />,
  clean_water: <Waves size={20} />,
  save_water: <Droplets size={20} />,
  sort_waste: <Trash2 size={20} />,
  recycle: <Recycle size={20} />,
  install_solar: <SunMedium size={20} />,
  save_energy: <Zap size={20} />,
  protect_animal: <ShieldCheck size={20} />,
  bird_house: <Bird size={20} />,
  save_fish: <Fish size={20} />,
};

// Fallback if action not in icon map
const DEFAULT_ICON = <Leaf size={20} />;

// Category tab ordering
const CATEGORY_ORDER = ["FLORA", "WATER", "WASTE", "ENERGY", "FAUNA"] as const;
type Category = (typeof CATEGORY_ORDER)[number];

const CATEGORY_LABELS: Record<Category, string> = {
  FLORA: "O'simliklar",
  WATER: "Suv",
  WASTE: "Chiqindi",
  ENERGY: "Energiya",
  FAUNA: "Hayvonlar",
};

// ─── Component ────────────────────────────────────────────────────────────────

interface ToolbarPanelProps {
  levelNumber: number;
}

export function ToolbarPanel({ levelNumber }: ToolbarPanelProps) {
  const { actions, loadActions } = useGameStore();
  const [selectedTool, setSelectedTool] = useState<string | null>(null);
  const [activeCategory, setActiveCategory] = useState<Category>("FLORA");
  const [resources, setResources] = useState(100);
  const [maxResources, setMaxResources] = useState(200);

  useEffect(() => {
    loadActions(levelNumber);
  }, [levelNumber, loadActions]);

  // Listen for resource updates from Phaser
  useEffect(() => {
    const handler = (payload: ResourcesChangedPayload) => {
      setResources(payload.resources);
      setMaxResources(payload.maxResources);
    };
    EventBus.on(EVENTS.RESOURCES_CHANGED, handler);
    return () => {
      EventBus.off(EVENTS.RESOURCES_CHANGED, handler);
    };
  }, []);

  const selectTool = (actionKey: string) => {
    const next = selectedTool === actionKey ? null : actionKey;
    setSelectedTool(next);
    EventBus.emit(EVENTS.TOOL_SELECTED, { actionKey: next ?? "" });
  };

  const visibleActions = actions.filter((a) => a.category === activeCategory);

  const getCost = (actionKey: string) => ACTION_COST[actionKey] ?? 10;

  return (
    <div className="flex flex-col gap-2 bg-gray-900/95 border border-gray-700 rounded-2xl p-3 shadow-2xl">
      {/* Resources bar */}
      <div className="flex items-center gap-3">
        <span className="text-yellow-400 font-semibold text-sm flex items-center gap-1">
          <Coins size={14} /> {resources}
        </span>
        <div className="flex-1 bg-gray-700 rounded-full h-2">
          <div
            className="bg-yellow-400 h-2 rounded-full transition-all duration-300"
            style={{ width: `${(resources / maxResources) * 100}%` }}
          />
        </div>
        <span className="text-gray-500 text-xs">{maxResources}</span>
      </div>

      {/* Category tabs */}
      <div className="flex gap-1 overflow-x-auto pb-1 scrollbar-none">
        {CATEGORY_ORDER.map((cat) => (
          <button
            key={cat}
            onClick={() => setActiveCategory(cat)}
            className={[
              "text-xs font-medium px-3 py-1.5 rounded-lg whitespace-nowrap transition-colors",
              activeCategory === cat
                ? "bg-green-600 text-white"
                : "bg-gray-700 text-gray-400 hover:bg-gray-600",
            ].join(" ")}
          >
            {CATEGORY_LABELS[cat]}
          </button>
        ))}
      </div>

      {/* Action buttons */}
      <div className="flex gap-2 overflow-x-auto pb-1 scrollbar-none">
        {visibleActions.length === 0 ? (
          <p className="text-gray-500 text-xs py-2 px-1">Amallar yo'q</p>
        ) : (
          visibleActions.map((action) => {
            const cost = getCost(action.key);
            return (
              <ToolButton
                key={action.key}
                icon={ACTION_ICONS[action.key] ?? DEFAULT_ICON}
                label={action.name_uz}
                cost={cost}
                isSelected={selectedTool === action.key}
                disabled={resources < cost}
                onClick={() => selectTool(action.key)}
              />
            );
          })
        )}
      </div>

      {selectedTool && (
        <p className="text-center text-xs text-green-400">
          Joylashtirish uchun xaritaga bosing
        </p>
      )}
    </div>
  );
}
