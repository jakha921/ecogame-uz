import type { GroundType, TileState } from "./worldTypes";

// Tile type index constants
export const GROUND_INDEX = {
  dirt: 0,
  grass: 1,
  water: 2,
  concrete: 3,
  polluted: 4,
} as const satisfies Record<GroundType, number>;

export const GROUND_TYPES: GroundType[] = ["dirt", "grass", "water", "concrete", "polluted"];

// Base colors for procedural tile rendering
export const TILE_COLORS: Record<GroundType, number> = {
  dirt: 0xc8975a,
  grass: 0x4caf50,
  water: 0x1e88e5,
  concrete: 0x9e9e9e,
  polluted: 0x6d4c41,
} as const;

// Left-face shade (darker, simulates depth)
export const TILE_LEFT: Record<GroundType, number> = {
  dirt: 0x9e6d3a,
  grass: 0x388e3c,
  water: 0x1565c0,
  concrete: 0x757575,
  polluted: 0x4e342e,
} as const;

// Right-face shade (darkest)
export const TILE_RIGHT: Record<GroundType, number> = {
  dirt: 0x7a5028,
  grass: 0x2e7d32,
  water: 0x0d47a1,
  concrete: 0x616161,
  polluted: 0x3e2723,
} as const;

// Determine visual tile appearance from tile health + ground type
export function getTileColor(tile: TileState): number {
  if (tile.groundType === "water") return TILE_COLORS.water;
  if (tile.groundType === "concrete") return TILE_COLORS.concrete;

  // Health-based color gradient for soil tiles
  const h = tile.health;
  if (h < 20) return TILE_COLORS.polluted;
  if (h < 45) return lerpColor(TILE_COLORS.polluted, TILE_COLORS.dirt, (h - 20) / 25);
  if (h < 70) return lerpColor(TILE_COLORS.dirt, TILE_COLORS.grass, (h - 45) / 25);
  return TILE_COLORS.grass;
}

export function getTileLeftColor(tile: TileState): number {
  return darkenHex(getTileColor(tile), 0.68);
}

export function getTileRightColor(tile: TileState): number {
  return darkenHex(getTileColor(tile), 0.5);
}

// ─── Color helpers ───────────────────────────────────────────────────────────

function lerpColor(a: number, b: number, t: number): number {
  const ar = (a >> 16) & 0xff,
    ag = (a >> 8) & 0xff,
    ab = a & 0xff;
  const br = (b >> 16) & 0xff,
    bg = (b >> 8) & 0xff,
    bb = b & 0xff;
  return (
    (Math.round(ar + (br - ar) * t) << 16) |
    (Math.round(ag + (bg - ag) * t) << 8) |
    Math.round(ab + (bb - ab) * t)
  );
}

function darkenHex(color: number, factor: number): number {
  return (
    (Math.floor(((color >> 16) & 0xff) * factor) << 16) |
    (Math.floor(((color >> 8) & 0xff) * factor) << 8) |
    Math.floor((color & 0xff) * factor)
  );
}
