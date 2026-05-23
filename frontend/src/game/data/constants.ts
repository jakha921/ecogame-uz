export const GAME_WIDTH = 800;
export const GAME_HEIGHT = 500;
export const TILE_SIZE = 32;
export const INDICATOR_MAX = 100;
export const INDICATOR_MIN = 0;
export const SYNC_INTERVAL_MS = 15_000;
export const LEVEL_COMPLETION_THRESHOLD = 80;

export const INDICATOR_COLORS = {
  air: 0x87ceeb,
  water: 0x00bcd4,
  soil: 0x8d6e63,
  biodiversity: 0x4caf50,
} as const;

// Visual thresholds for color feedback
export const INDICATOR_LOW = 30;
export const INDICATOR_MID = 60;
