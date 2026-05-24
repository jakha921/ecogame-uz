export const GAME_WIDTH = 960;
export const GAME_HEIGHT = 560;

// Isometric tile dimensions (standard 2:1 ratio)
export const ISO_TILE_W = 64;
export const ISO_TILE_H = 32;
// 3D side depth (pixels below the diamond)
export const ISO_SIDE_DEPTH = 12;

// Legacy — keep for HUDScene compat
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

export const INDICATOR_LOW = 30;
export const INDICATOR_MID = 60;

// Ecosystem simulation timings (seconds)
export const OBJECT_STAGE_1_S = 10; // placed → growing
export const OBJECT_STAGE_2_S = 30; // growing → mature
export const OBJECT_STAGE_3_S = 60; // mature → spreading

// Spread radii per object type (tiles)
export const SPREAD_RADIUS: Record<string, number> = {
  plant_tree: 3,
  plant_flowers: 2,
  care_garden: 2,
  clean_water: 4,
  save_water: 2,
  sort_waste: 2,
  recycle: 2,
  install_solar: 2,
  save_energy: 1,
  protect_animal: 3,
  bird_house: 3,
  save_fish: 3,
};

// Eco-coin cost per action (fallback if not in backend EcoAction.cost)
export const ACTION_COST: Record<string, number> = {
  plant_tree: 20,
  plant_flowers: 10,
  care_garden: 15,
  clean_water: 25,
  save_water: 10,
  sort_waste: 20,
  recycle: 15,
  install_solar: 30,
  save_energy: 10,
  protect_animal: 30,
  bird_house: 20,
  save_fish: 25,
};
