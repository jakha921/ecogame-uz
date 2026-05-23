import Phaser from "phaser";
import { useEffect, useRef } from "react";
import type { Level } from "@/api/types";
import { useGameStore } from "@/stores/gameStore";
import { GAME_HEIGHT, GAME_WIDTH } from "./data/constants";
import {
  EVENTS,
  EventBus,
  type AchievementUnlockedPayload,
  type ActionPerformedPayload,
  type EcosystemChangedPayload,
  type LevelCompletedPayload,
  type ScoreUpdatedPayload,
} from "./events/EventBus";
import { BootScene } from "./scenes/BootScene";
import { HUDScene } from "./scenes/HUDScene";
import { MainScene } from "./scenes/MainScene";
import { PreloadScene } from "./scenes/PreloadScene";

interface PhaserGameProps {
  levelConfig: Level;
  onActionPerformed: (payload: ActionPerformedPayload) => void;
  onLevelCompleted: (payload: LevelCompletedPayload) => void;
  onAchievementUnlocked: (payload: AchievementUnlockedPayload) => void;
}

export function PhaserGame({
  levelConfig,
  onActionPerformed,
  onLevelCompleted,
  onAchievementUnlocked,
}: PhaserGameProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const gameRef = useRef<Phaser.Game | null>(null);
  const { updateEcosystem, addScore } = useGameStore();

  useEffect(() => {
    if (!containerRef.current || gameRef.current) return;

    const config: Phaser.Types.Core.GameConfig = {
      type: Phaser.AUTO,
      width: GAME_WIDTH,
      height: GAME_HEIGHT,
      parent: containerRef.current,
      backgroundColor: "#87ceeb",
      scene: [BootScene, PreloadScene, MainScene, HUDScene],
      physics: {
        default: "arcade",
        arcade: { gravity: { x: 0, y: 0 }, debug: false },
      },
      scale: {
        mode: Phaser.Scale.FIT,
        autoCenter: Phaser.Scale.CENTER_BOTH,
      },
    };

    const game = new Phaser.Game(config);
    gameRef.current = game;

    // Pass level config to scenes via registry
    game.registry.set("levelConfig", levelConfig);

    // Bridge EventBus events → React
    EventBus.on(EVENTS.ECOSYSTEM_CHANGED, (payload: EcosystemChangedPayload) => {
      updateEcosystem({
        air: payload.air,
        water: payload.water,
        soil: payload.soil,
        biodiversity: payload.biodiversity,
      });
    });

    EventBus.on(EVENTS.SCORE_UPDATED, (payload: ScoreUpdatedPayload) => {
      addScore(payload.score);
    });

    EventBus.on(EVENTS.ACTION_PERFORMED, (payload: ActionPerformedPayload) => {
      onActionPerformed(payload);
    });

    EventBus.on(EVENTS.LEVEL_COMPLETED, (payload: LevelCompletedPayload) => {
      onLevelCompleted(payload);
    });

    EventBus.on(EVENTS.ACHIEVEMENT_UNLOCKED, (payload: AchievementUnlockedPayload) => {
      onAchievementUnlocked(payload);
    });

    return () => {
      EventBus.removeAllListeners();
      game.destroy(true);
      gameRef.current = null;
    };
  }, [
    levelConfig,
    updateEcosystem,
    addScore,
    onActionPerformed,
    onLevelCompleted,
    onAchievementUnlocked,
  ]);

  return (
    <div
      ref={containerRef}
      className="w-full rounded-2xl overflow-hidden shadow-lg"
      style={{ aspectRatio: `${GAME_WIDTH}/${GAME_HEIGHT}` }}
    />
  );
}
