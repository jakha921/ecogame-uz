import { useEffect, useRef } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { useGameStore } from "@/stores/gameStore";
import { t } from "@/i18n";

// Placeholder: Phaser game will be integrated in Phase 6
export function GamePage() {
  const { levelId } = useParams<{ levelId: string }>();
  const { startGame, endGame, loadLevels, levels, ecosystem, score, isLoading } = useGameStore();
  const navigate = useNavigate();
  const started = useRef(false);

  useEffect(() => {
    if (!levelId) return;
    loadLevels().then(() => {
      if (!started.current) {
        started.current = true;
        startGame(Number(levelId)).catch(() => navigate("/"));
      }
    });

    return () => {
      if (started.current) endGame();
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [levelId]);

  const level = levels.find((l) => l.id === Number(levelId));

  if (isLoading) return <p className="text-gray-400 text-center py-20">O'yin yuklanmoqda...</p>;

  return (
    <div className="flex flex-col gap-4">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-bold text-green-700">
          {level?.name_uz ?? `Daraja ${levelId}`}
        </h1>
        <button
          onClick={() => navigate("/")}
          className="text-sm text-gray-500 hover:text-gray-700"
        >
          ← Chiqish
        </button>
      </div>

      {/* HUD */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        {[
          { key: "air_quality", label: t("game.air_quality"), value: ecosystem.air, color: "blue" },
          { key: "water", label: t("game.water_purity"), value: ecosystem.water, color: "cyan" },
          { key: "soil", label: t("game.soil_health"), value: ecosystem.soil, color: "yellow" },
          {
            key: "biodiversity",
            label: t("game.biodiversity"),
            value: ecosystem.biodiversity,
            color: "green",
          },
        ].map(({ key, label, value, color }) => (
          <div key={key} className="bg-white rounded-xl p-3 shadow-sm">
            <p className="text-xs text-gray-400 mb-1">{label}</p>
            <div className="w-full bg-gray-100 rounded-full h-2">
              <div
                className={`bg-${color}-500 h-2 rounded-full transition-all`}
                style={{ width: `${Math.min(100, value)}%` }}
              />
            </div>
            <p className="text-xs text-right text-gray-500 mt-1">{value.toFixed(1)}%</p>
          </div>
        ))}
      </div>

      <div className="text-right text-sm text-gray-600">
        {t("game.score")}: <span className="font-bold text-green-700">{score}</span>
      </div>

      {/* Game canvas placeholder */}
      <div className="bg-gradient-to-b from-sky-200 to-green-300 rounded-2xl flex items-center justify-center min-h-[400px] text-center">
        <div>
          <p className="text-white text-2xl font-bold mb-2">🎮 O'yin sahifasi</p>
          <p className="text-white/80 text-sm">Phaser.js o'yin motori Phase 6 da qo'shiladi</p>
          <p className="text-white/60 text-xs mt-2">
            {level?.description_uz}
          </p>
        </div>
      </div>
    </div>
  );
}
