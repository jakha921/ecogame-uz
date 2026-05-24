import { useCallback, useEffect, useRef, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { ArrowLeft, CheckCircle, Info, Star, Target, Trophy } from "lucide-react";
import { ToolbarPanel } from "@/components/game/ToolbarPanel";
import type { AchievementUnlockedPayload, ActionPerformedPayload, LevelCompletedPayload } from "@/game/events/EventBus";
import { PhaserGame } from "@/game/PhaserGame";
import { useGameSync } from "@/hooks/useGameSync";
import { t } from "@/i18n";
import { useGameStore } from "@/stores/gameStore";

export function GamePage() {
  const { levelId } = useParams<{ levelId: string }>();
  const { startGame, endGame, loadLevels, levels, currentSession, ecosystem, score, isLoading } =
    useGameStore();
  const navigate = useNavigate();
  const started = useRef(false);
  const [levelComplete, setLevelComplete] = useState(false);
  const [unlockedAchievement, setUnlockedAchievement] = useState<string | null>(null);
  const [showTutorial, setShowTutorial] = useState(true);

  const { pushAction, flushBuffer } = useGameSync(currentSession?.id ?? null);

  useEffect(() => {
    if (!levelId) return;
    loadLevels().then(() => {
      if (!started.current) {
        started.current = true;
        startGame(Number(levelId)).catch(() => navigate("/"));
      }
    });

    return () => {
      if (started.current) {
        flushBuffer();
        endGame();
      }
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [levelId]);

  const handleActionPerformed = useCallback(
    (payload: ActionPerformedPayload) => {
      pushAction({
        action_key: payload.actionKey,
        position_x: payload.positionX,
        position_y: payload.positionY,
      });
    },
    [pushAction],
  );

  const handleLevelCompleted = useCallback(
    async (_payload: LevelCompletedPayload) => {
      setLevelComplete(true);
      await flushBuffer();
      await endGame();
    },
    [flushBuffer, endGame],
  );

  const handleAchievementUnlocked = useCallback((payload: AchievementUnlockedPayload) => {
    setUnlockedAchievement(payload.nameUz);
    setTimeout(() => setUnlockedAchievement(null), 3000);
  }, []);

  const level = levels.find((l) => l.id === Number(levelId));

  if (isLoading || !level) {
    return <p className="text-gray-400 text-center py-20">O'yin yuklanmoqda...</p>;
  }

  if (levelComplete) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] gap-6">
        <CheckCircle size={72} className="text-green-500" />
        <h1 className="text-3xl font-bold text-green-700">{t("game.level_complete")}</h1>
        <p className="text-gray-600">{level.name_uz} muvaffaqiyatli tugallandi!</p>
        <div className="flex items-center gap-2 text-2xl font-bold text-green-600">
          <Star size={24} className="text-yellow-500" />
          {score} ball
        </div>
        <button
          onClick={() => navigate("/")}
          className="bg-green-600 hover:bg-green-500 text-white font-semibold px-8 py-3 rounded-xl transition-colors flex items-center gap-2"
        >
          <ArrowLeft size={18} />
          Bosh sahifaga qaytish
        </button>
      </div>
    );
  }

  const indicators = [
    { key: "air", label: t("game.air_quality"), value: ecosystem.air, bg: "bg-blue-500" },
    { key: "water", label: t("game.water_purity"), value: ecosystem.water, bg: "bg-cyan-500" },
    { key: "soil", label: t("game.soil_health"), value: ecosystem.soil, bg: "bg-yellow-600" },
    {
      key: "bio",
      label: t("game.biodiversity"),
      value: ecosystem.biodiversity,
      bg: "bg-green-500",
    },
  ];

  return (
    <div className="flex flex-col gap-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-bold text-green-700">{level.name_uz}</h1>
        <button
          onClick={() => navigate("/")}
          className="text-sm text-gray-500 hover:text-gray-700 flex items-center gap-1"
        >
          <ArrowLeft size={14} /> Chiqish
        </button>
      </div>

      {/* Goal banner */}
      <div className="bg-green-50 border border-green-200 rounded-xl px-4 py-2.5 flex items-center gap-3">
        <Target size={16} className="text-green-600 shrink-0" />
        <p className="text-sm text-green-700 flex-1">
          <span className="font-semibold">Maqsad:</span> barcha ko'rsatkichlarni{" "}
          <span className="font-bold">80%</span> ga yetkazing
        </p>
        <span className="text-sm font-bold text-green-700 ml-auto">
          {t("game.score")}: {score}
        </span>
      </div>

      {/* Tutorial hint — dismissable */}
      {showTutorial && (
        <div className="bg-blue-50 border border-blue-200 rounded-xl px-4 py-3 flex items-start gap-3">
          <Info size={16} className="text-blue-500 mt-0.5 shrink-0" />
          <div className="flex-1 text-sm text-blue-700">
            <p className="font-semibold mb-1">Qanday o'ynash kerak?</p>
            <ol className="list-decimal list-inside space-y-0.5 text-xs">
              <li>Pastdagi paneldan qurol tanlang (daraxt, suv, quyosh paneli...)</li>
              <li>Xaritadagi istalgan katakchaga bosing — ob'ekt joylashadi</li>
              <li>Ob'ektlar o'sib, atrofdagi muhitni yaxshilaydi</li>
              <li>Barcha 4 ko'rsatkich 80% ga yetganda daraja tugaydi</li>
            </ol>
          </div>
          <button
            onClick={() => setShowTutorial(false)}
            className="text-blue-400 hover:text-blue-600 text-xs shrink-0"
          >
            Yopish ✕
          </button>
        </div>
      )}

      {/* React HUD overlay */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        {indicators.map(({ key, label, value, bg }) => {
          const done = value >= 80;
          return (
            <div
              key={key}
              className={`rounded-xl p-3 shadow-sm border ${done ? "bg-green-50 border-green-200" : "bg-white border-transparent"}`}
            >
              <p className="text-xs text-gray-400 mb-1">{label}</p>
              <div className="w-full bg-gray-100 rounded-full h-2.5">
                <div
                  className={`${done ? "bg-green-500" : bg} h-2.5 rounded-full transition-all duration-500`}
                  style={{ width: `${Math.min(100, Math.max(0, value))}%` }}
                />
              </div>
              <p className={`text-xs text-right mt-1 ${done ? "text-green-600 font-semibold" : "text-gray-500"}`}>
                {value.toFixed(1)}% {done && "✓"}
              </p>
            </div>
          );
        })}
      </div>

      {/* Phaser canvas */}
      <PhaserGame
        levelConfig={level}
        onActionPerformed={handleActionPerformed}
        onLevelCompleted={handleLevelCompleted}
        onAchievementUnlocked={handleAchievementUnlocked}
      />

      {/* Toolbar: tool selection panel */}
      <ToolbarPanel levelNumber={level.number} />

      {/* Achievement toast */}
      {unlockedAchievement && (
        <div className="fixed bottom-6 right-6 bg-yellow-400 text-gray-900 rounded-xl px-5 py-3 shadow-lg font-semibold animate-bounce flex items-center gap-2">
          <Trophy size={18} />
          Yutuq: {unlockedAchievement}
        </div>
      )}
    </div>
  );
}
