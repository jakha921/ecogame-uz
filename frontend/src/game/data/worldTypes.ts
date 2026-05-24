// Ground tile types (index matches tileset order)
export type GroundType = "dirt" | "grass" | "water" | "concrete" | "polluted";
export type ObjectStage = 0 | 1 | 2 | 3; // placed → growing → mature → spreading

export interface TileState {
  col: number;
  row: number;
  groundType: GroundType;
  placedObject: string | null; // action key, e.g. "plant_tree"
  objectStage: ObjectStage;
  pollution: number; // 0-100
  health: number; // 0-100
  moisture: number; // 0-100
  placedAt?: number; // timestamp when object was placed
}

export interface WorldState {
  tiles: TileState[][];
  resources: number;
}

export interface PlacedObject {
  actionKey: string;
  col: number;
  row: number;
  stage: ObjectStage;
  placedAt: number;
}

// The new isometric map_config structure stored in Level.map_config
export interface IsoMapConfig {
  iso_width: number;
  iso_height: number;
  initial_resources: number;
  regen_rate: number; // eco-coins per second
  // Optional pre-defined grid data (populated in Phase 4):
  ground?: number[]; // flat array, index = row*width + col
  pollution?: number[]; // flat array, initial pollution per tile
  blocked?: number[]; // tile indices that cannot be modified
}
