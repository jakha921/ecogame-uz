import Phaser from "phaser";

// Singleton EventEmitter bridging Phaser scenes ↔ React components
export const EventBus = new Phaser.Events.EventEmitter();

// Typed event constants to avoid magic strings
export const EVENTS = {
  SCORE_UPDATED: "score-updated",
  ECOSYSTEM_CHANGED: "ecosystem-changed",
  ACTION_PERFORMED: "action-performed",
  ACHIEVEMENT_UNLOCKED: "achievement-unlocked",
  LEVEL_COMPLETED: "level-completed",
  GAME_PAUSED: "game-paused",
  GAME_RESUMED: "game-resumed",
  // Isometric sandbox — new events
  TOOL_SELECTED: "tool-selected",       // React → Phaser: player picked a tool
  RESOURCES_CHANGED: "resources-changed", // Phaser → React: eco-coin balance update
  WORLD_SYNC: "world-sync",             // Phaser → React: batch of placements to persist
} as const;

export type GameEvent = (typeof EVENTS)[keyof typeof EVENTS];

export interface ScoreUpdatedPayload {
  score: number;
}

export interface EcosystemChangedPayload {
  air: number;
  water: number;
  soil: number;
  biodiversity: number;
}

export interface ActionPerformedPayload {
  actionKey: string;
  positionX: number;
  positionY: number;
}

export interface AchievementUnlockedPayload {
  achievementKey: string;
  nameUz: string;
  icon: string;
}

export interface LevelCompletedPayload {
  levelNumber: number;
}

export interface ToolSelectedPayload {
  actionKey: string;
}

export interface ResourcesChangedPayload {
  resources: number;
  maxResources: number;
}

export interface WorldSyncPayload {
  placements: Array<{ actionKey: string; col: number; row: number }>;
  removals: Array<{ col: number; row: number }>;
}
