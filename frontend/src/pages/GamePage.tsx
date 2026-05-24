import { useCallback, useEffect, useRef, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
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
        <div className="text-6xl">🎉</div>
        <h1 className="text-3xl font-bold text-green-700">{t("game.level_complete")}</h1>
        <p className="text-gray-600">{level.name_uz} muvaffaqiyatli tugallandi!</p>
        <p className="text-2xl font-bold text-green-600">Ball: {score}</p>
        <button
          onClick={() => navigate("/")}
          className="bg-green-600 hover:bg-green-500 text-white font-semibold px-8 py-3 rounded-xl transition-colors"
        >
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
          className="text-sm text-gray-500 hover:text-gray-700"
        >
          ← Chiqish
        </button>
      </div>

      {/* React HUD overlay */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        {indicators.map(({ key, label, value, bg }) => (
          <div key={key} className="bg-white rounded-xl p-3 shadow-sm">
            <p className="text-xs text-gray-400 mb-1">{label}</p>
            <div className="w-full bg-gray-100 rounded-full h-2.5">
              <div
                className={`${bg} h-2.5 rounded-full transition-all duration-500`}
                style={{ width: `${Math.min(100, Math.max(0, value))}%` }}
              />
            </div>
            <p className="text-xs text-right text-gray-500 mt-1">{value.toFixed(1)}%</p>
          </div>
        ))}
      </div>

      <div className="text-right text-sm text-gray-600">
        {t("game.score")}: <span className="font-bold text-green-700">{score}</span>
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
        <div className="fixed bottom-6 right-6 bg-yellow-400 text-gray-900 rounded-xl px-5 py-3 shadow-lg font-semibold animate-bounce">
          🏆 Yutuq: {unlockedAchievement}
        </div>
      )}
    </div>
  );
}
