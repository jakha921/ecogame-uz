import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { CheckCircle, XCircle } from "lucide-react";
import type { BinType, SortingItem } from "@/data/sortingItems";
import { SORTING_ITEMS } from "@/data/sortingItems";
import { WasteBin } from "./WasteBin";
import { WasteItem } from "./WasteItem";

const MAX_ERRORS = 5;

const BINS: { type: BinType; label: string; color: string; icon: string }[] = [
  {
    type: "recyclable",
    label: "Qayta ishlanadigan",
    color: "border-blue-400 bg-blue-50 text-blue-700",
    icon: "♻️",
  },
  {
    type: "organic",
    label: "Organik",
    color: "border-green-400 bg-green-50 text-green-700",
    icon: "🌱",
  },
  {
    type: "landfill",
    label: "Poligon",
    color: "border-gray-400 bg-gray-50 text-gray-700",
    icon: "🗑️",
  },
];

function shuffle<T>(arr: T[]): T[] {
  const a = [...arr];
  for (let i = a.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [a[i], a[j]] = [a[j], a[i]];
  }
  return a;
}

type Phase = "playing" | "feedback" | "done";
type FeedbackType = "correct" | "incorrect";

interface SortingGameProps {
  onComplete: (score: number, correctCount: number, totalItems: number) => void;
}

export function SortingGame({ onComplete }: SortingGameProps) {
  const items = useMemo(() => shuffle(SORTING_ITEMS), []);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [score, setScore] = useState(0);
  const [errors, setErrors] = useState(0);
  const [correctCount, setCorrectCount] = useState(0);
  const [phase, setPhase] = useState<Phase>("playing");
  const [feedback, setFeedback] = useState<FeedbackType | null>(null);
  const [highlightedBin, setHighlightedBin] = useState<BinType | null>(null);
  const [selectedItem, setSelectedItem] = useState<SortingItem | null>(null);
  const timeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  const currentItem = items[currentIndex];
  const isLastItem = currentIndex >= items.length - 1;
  const tooManyErrors = errors >= MAX_ERRORS;

  const handleDrop = useCallback(
    (binType: BinType) => {
      if (phase !== "playing" || !currentItem) return;

      const isCorrect = currentItem.correct_bin === binType;
      setHighlightedBin(binType);
      setFeedback(isCorrect ? "correct" : "incorrect");
      setPhase("feedback");
      setSelectedItem(null);

      if (isCorrect) {
        setScore((s) => s + currentItem.points);
        setCorrectCount((c) => c + 1);
      } else {
        setErrors((e) => e + 1);
      }

      timeoutRef.current = setTimeout(() => {
        setHighlightedBin(null);
        setFeedback(null);

        if (isLastItem || (!isCorrect && errors + 1 >= MAX_ERRORS)) {
          setPhase("done");
          onComplete(
            isCorrect ? score + currentItem.points : score,
            isCorrect ? correctCount + 1 : correctCount,
            items.length,
          );
        } else {
          setCurrentIndex((i) => i + 1);
          setPhase("playing");
        }
      }, 1200);
    },
    [phase, currentItem, isLastItem, errors, score, correctCount, items.length, onComplete],
  );

  // Touch-friendly: tap item, then tap bin
  const handleItemTap = () => {
    if (phase !== "playing") return;
    setSelectedItem(selectedItem ? null : currentItem);
  };

  const handleBinTap = (binType: BinType) => {
    if (selectedItem) {
      handleDrop(binType);
    }
  };

  useEffect(() => {
    return () => {
      if (timeoutRef.current) clearTimeout(timeoutRef.current);
    };
  }, []);

  if (phase === "done") return null;

  return (
    <div className="flex flex-col gap-6">
      {/* Progress */}
      <div className="flex items-center justify-between text-sm">
        <span className="text-gray-500">
          {currentIndex + 1} / {items.length}
        </span>
        <span className="font-bold text-green-700">{score} ball</span>
        <span className="text-red-500 text-xs">
          Xatolar: {errors}/{MAX_ERRORS}
        </span>
      </div>

      {/* Current item */}
      <div
        className={["flex justify-center transition-all", selectedItem ? "scale-105" : ""].join(" ")}
        onClick={handleItemTap}
      >
        <div className="w-48">
          <WasteItem item={currentItem} draggable={phase === "playing"} />
        </div>
        {selectedItem && (
          <p className="absolute mt-2 text-xs text-green-600 font-medium text-center">
            Idishni bosing
          </p>
        )}
      </div>

      {/* Feedback flash */}
      {feedback && (
        <div
          className={[
            "flex items-center justify-center gap-2 rounded-xl py-3 text-sm font-bold",
            feedback === "correct"
              ? "bg-green-50 text-green-700"
              : "bg-red-50 text-red-700",
          ].join(" ")}
        >
          {feedback === "correct" ? (
            <>
              <CheckCircle size={18} />
              To'g'ri!
            </>
          ) : (
            <>
              <XCircle size={18} />
              Noto'g'ri idish!
            </>
          )}
        </div>
      )}

      {/* Bins */}
      <div className="grid grid-cols-3 gap-3">
        {BINS.map((bin) => (
          <WasteBin
            key={bin.type}
            binType={bin.type}
            label={bin.label}
            color={bin.color}
            icon={bin.icon}
            onDrop={handleDrop}
            isHighlighted={highlightedBin === bin.type}
            onTapSelect={() => handleBinTap(bin.type)}
          />
        ))}
      </div>

      {tooManyErrors && (
        <p className="text-center text-sm text-red-500">Juda ko'p xato!</p>
      )}
    </div>
  );
}
