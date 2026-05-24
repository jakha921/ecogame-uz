import Phaser from "phaser";
import type { Level } from "@/api/types";
import {
  GAME_HEIGHT,
  GAME_WIDTH,
  ISO_SIDE_DEPTH,
  ISO_TILE_H,
  ISO_TILE_W,
  LEVEL_COMPLETION_THRESHOLD,
  OBJECT_STAGE_1_S,
  OBJECT_STAGE_2_S,
  OBJECT_STAGE_3_S,
  SPREAD_RADIUS,
} from "../data/constants";
import { EVENTS, EventBus } from "../events/EventBus";
import type { ToolSelectedPayload } from "../events/EventBus";
import { getTileColor, getTileLeftColor, getTileRightColor, GROUND_TYPES } from "../data/tilesets";
import type { GroundType, IsoMapConfig, TileState, ObjectStage } from "../data/worldTypes";

// ─── Object visual data ───────────────────────────────────────────────────────

const OBJECT_EMOJI: Record<string, string[]> = {
  plant_tree: ["🌱", "🌿", "🌳", "🌲"],
  plant_flowers: ["🌱", "🌸", "🌺", "🌻"],
  care_garden: ["🌱", "🌿", "🍀", "🌾"],
  clean_water: ["💧", "🫧", "🌊", "✨"],
  save_water: ["🪣", "💧", "🚿", "🌊"],
  sort_waste: ["🗑️", "♻️", "✅", "🌿"],
  recycle: ["🗑️", "♻️", "✅", "🌿"],
  install_solar: ["🔧", "⚡", "☀️", "✨"],
  save_energy: ["💡", "⚡", "☀️", "🌟"],
  protect_animal: ["🦺", "🐾", "🦌", "🌿"],
  bird_house: ["🏠", "🐦", "🦅", "🌿"],
  save_fish: ["🎣", "🐟", "🐠", "🌊"],
};

// ─── Scene ────────────────────────────────────────────────────────────────────

export class IsoMainScene extends Phaser.Scene {
  private tiles: TileState[][] = [];
  private mapW = 10;
  private mapH = 8;
  private originX = 0;
  private originY = 0;

  private tileGfx!: Phaser.GameObjects.Graphics;
  private highlightGfx!: Phaser.GameObjects.Graphics;

  private hoveredTile: { col: number; row: number } | null = null;
  private selectedTool: string | null = null;
  private resources = 100;
  private maxResources = 200;
  private regenRate = 0.2; // coins/sec
  private regenAccum = 0;

  // Ecosystem simulation
  private simAccumMs = 0;
  private completionEmitted = false;

  // Object sprite cache: "col,row" → Phaser Text (emoji label)
  private objectSprites = new Map<string, Phaser.GameObjects.Text>();

  constructor() {
    super({ key: "IsoMainScene" });
  }

  create() {
    const levelConfig = this.registry.get("levelConfig") as Level;
    const mc = (levelConfig.map_config ?? {}) as unknown as IsoMapConfig;

    this.mapW = mc.iso_width ?? 10;
    this.mapH = mc.iso_height ?? 8;
    this.resources = mc.initial_resources ?? 100;
    this.maxResources = (mc.initial_resources ?? 100) * 2;
    this.regenRate = mc.regen_rate ?? 0.2;

    // Build tile grid
    this.tiles = this.buildGrid(mc);

    // Position origin so map is centered horizontally and padded from top
    const mapPixelW = (this.mapW + this.mapH) * (ISO_TILE_W / 2);
    const mapPixelH = (this.mapW + this.mapH) * (ISO_TILE_H / 2) + ISO_SIDE_DEPTH;
    this.originX = (GAME_WIDTH - mapPixelW) / 2 + (this.mapH * ISO_TILE_W) / 2;
    this.originY = 60; // top padding for HUD

    // Create graphics layers in draw order
    this.tileGfx = this.add.graphics();
    this.highlightGfx = this.add.graphics();

    // Camera
    const camW = Math.max(GAME_WIDTH, mapPixelW + 120);
    const camH = Math.max(GAME_HEIGHT, mapPixelH + 120);
    this.cameras.main.setBounds(
      -(camW - GAME_WIDTH) / 2 - 60,
      -40,
      camW + 120,
      camH + 80,
    );

    // Input handlers
    this.input.on(Phaser.Input.Events.POINTER_MOVE, this.onPointerMove, this);
    this.input.on(Phaser.Input.Events.POINTER_DOWN, this.onPointerDown, this);
    this.input.on(Phaser.Input.Events.GAME_OUT, this.onPointerOut, this);
    this.input.on("wheel", this.onWheel, this);

    // React → Phaser: tool selection
    EventBus.on(EVENTS.TOOL_SELECTED, (payload: ToolSelectedPayload) => {
      this.selectedTool = payload.actionKey;
    });

    // Initial render
    this.redrawTiles();

    // Emit initial state to React HUD
    EventBus.emit(EVENTS.ECOSYSTEM_CHANGED, this.computeGlobalState());
    EventBus.emit(EVENTS.RESOURCES_CHANGED, {
      resources: this.resources,
      maxResources: this.maxResources,
    });
  }

  update(_time: number, delta: number) {
    this.redrawTiles();
    this.drawHighlight();

    // Ecosystem simulation (1-second ticks)
    this.simAccumMs += delta;
    if (this.simAccumMs >= 1000) {
      const ticks = Math.floor(this.simAccumMs / 1000);
      this.simAccumMs -= ticks * 1000;
      this.simulateTicks(ticks);
      this.redrawObjectLayer();
    }

    // Resource regeneration
    this.regenAccum += delta / 1000;
    if (this.regenAccum >= 1) {
      const gained = Math.floor(this.regenAccum * this.regenRate);
      this.regenAccum -= gained / this.regenRate;
      if (gained > 0) {
        this.resources = Math.min(this.maxResources, this.resources + gained);
        EventBus.emit(EVENTS.RESOURCES_CHANGED, {
          resources: this.resources,
          maxResources: this.maxResources,
        });
      }
    }

    // Level completion check
    if (!this.completionEmitted && this.isLevelComplete()) {
      this.completionEmitted = true;
      const levelConfig = this.registry.get("levelConfig") as Level;
      EventBus.emit(EVENTS.LEVEL_COMPLETED, { levelNumber: levelConfig.number });
    }
  }

  // ─── Grid setup ──────────────────────────────────────────────────────────────

  private buildGrid(mc: IsoMapConfig): TileState[][] {
    const grid: TileState[][] = [];
    const groundArr = mc.ground;
    const pollutionArr = mc.pollution;

    for (let row = 0; row < this.mapH; row++) {
      grid[row] = [];
      for (let col = 0; col < this.mapW; col++) {
        const idx = row * this.mapW + col;
        let groundType: GroundType;
        let pollution: number;

        if (groundArr) {
          groundType = GROUND_TYPES[groundArr[idx] ?? 0] ?? "dirt";
          pollution = pollutionArr?.[idx] ?? 50;
        } else {
          // Default pattern: outer concrete, inner pollution gradient
          groundType = this.defaultGroundType(col, row);
          pollution = this.defaultPollution(col, row);
        }

        grid[row][col] = {
          col,
          row,
          groundType,
          placedObject: null,
          objectStage: 0,
          pollution,
          health: Math.max(0, Math.min(100, 80 - pollution * 0.8)),
          moisture: groundType === "water" ? 90 : 20,
        };
      }
    }
    return grid;
  }

  private defaultGroundType(col: number, row: number): GroundType {
    const border = 1;
    if (col < border || col >= this.mapW - border || row < border || row >= this.mapH - border) {
      return "concrete";
    }
    const innerBorder = 2;
    if (
      col < innerBorder ||
      col >= this.mapW - innerBorder ||
      row < innerBorder ||
      row >= this.mapH - innerBorder
    ) {
      return "polluted";
    }
    return "dirt";
  }

  private defaultPollution(col: number, row: number): number {
    const border = 1;
    if (col < border || col >= this.mapW - border || row < border || row >= this.mapH - border) {
      return 0; // concrete border
    }
    // Distance from center gives pollution
    const cx = this.mapW / 2;
    const cy = this.mapH / 2;
    const dist = Math.sqrt((col - cx) ** 2 + (row - cy) ** 2);
    const maxDist = Math.sqrt(cx ** 2 + cy ** 2);
    return Math.round((dist / maxDist) * 80);
  }

  // ─── Coordinate conversion ────────────────────────────────────────────────────

  gridToScreen(col: number, row: number): { x: number; y: number } {
    return {
      x: this.originX + (col - row) * (ISO_TILE_W / 2),
      y: this.originY + (col + row) * (ISO_TILE_H / 2),
    };
  }

  private screenToGrid(
    screenX: number,
    screenY: number,
  ): { col: number; row: number } | null {
    const world = this.cameras.main.getWorldPoint(screenX, screenY);
    const relX = world.x - this.originX;
    const relY = world.y - this.originY;

    // Inverse isometric projection
    const col = Math.floor((relX / (ISO_TILE_W / 2) + relY / (ISO_TILE_H / 2)) / 2);
    const row = Math.floor((relY / (ISO_TILE_H / 2) - relX / (ISO_TILE_W / 2)) / 2);

    if (col < 0 || col >= this.mapW || row < 0 || row >= this.mapH) return null;
    return { col, row };
  }

  // ─── Rendering ───────────────────────────────────────────────────────────────

  private redrawTiles() {
    this.tileGfx.clear();

    // Draw in diagonal-stripe order for correct depth (small col+row first = furthest)
    for (let sum = 0; sum < this.mapW + this.mapH - 1; sum++) {
      const rowStart = Math.max(0, sum - this.mapW + 1);
      const rowEnd = Math.min(sum, this.mapH - 1);
      for (let row = rowStart; row <= rowEnd; row++) {
        const col = sum - row;
        this.drawSingleTile(this.tiles[row][col]);
      }
    }
  }

  private drawSingleTile(tile: TileState) {
    const { x, y } = this.gridToScreen(tile.col, tile.row);
    const hw = ISO_TILE_W / 2;
    const hh = ISO_TILE_H / 2;
    const d = ISO_SIDE_DEPTH;

    const topColor = getTileColor(tile);
    const leftColor = getTileLeftColor(tile);
    const rightColor = getTileRightColor(tile);

    // Top diamond face
    this.tileGfx.fillStyle(topColor, 1);
    this.tileGfx.fillPoints(
      [
        { x: x + hw, y },
        { x: x + ISO_TILE_W, y: y + hh },
        { x: x + hw, y: y + ISO_TILE_H },
        { x, y: y + hh },
      ],
      true,
    );

    // Left side face (water has no side depth)
    if (tile.groundType !== "water") {
      this.tileGfx.fillStyle(leftColor, 1);
      this.tileGfx.fillPoints(
        [
          { x, y: y + hh },
          { x: x + hw, y: y + ISO_TILE_H },
          { x: x + hw, y: y + ISO_TILE_H + d },
          { x, y: y + hh + d },
        ],
        true,
      );

      // Right side face
      this.tileGfx.fillStyle(rightColor, 1);
      this.tileGfx.fillPoints(
        [
          { x: x + hw, y: y + ISO_TILE_H },
          { x: x + ISO_TILE_W, y: y + hh },
          { x: x + ISO_TILE_W, y: y + hh + d },
          { x: x + hw, y: y + ISO_TILE_H + d },
        ],
        true,
      );
    }

    // Thin border on top face for grid clarity
    this.tileGfx.lineStyle(0.5, 0x000000, 0.25);
    this.tileGfx.strokePoints(
      [
        { x: x + hw, y },
        { x: x + ISO_TILE_W, y: y + hh },
        { x: x + hw, y: y + ISO_TILE_H },
        { x, y: y + hh },
      ],
      true,
    );
  }

  private drawHighlight() {
    this.highlightGfx.clear();
    if (!this.hoveredTile) return;

    const { col, row } = this.hoveredTile;
    const tile = this.tiles[row]?.[col];
    if (!tile) return;

    const { x, y } = this.gridToScreen(col, row);
    const hw = ISO_TILE_W / 2;
    const hh = ISO_TILE_H / 2;

    // Glow outline — white if tool selected, yellow if browsing
    const color = this.selectedTool ? 0x00ff88 : 0xffffff;
    this.highlightGfx.lineStyle(2.5, color, 0.9);
    this.highlightGfx.strokePoints(
      [
        { x: x + hw, y },
        { x: x + ISO_TILE_W, y: y + hh },
        { x: x + hw, y: y + ISO_TILE_H },
        { x, y: y + hh },
      ],
      true,
    );
  }

  private redrawObjectLayer() {
    // Remove sprites for objects that no longer exist
    for (const [key, sprite] of this.objectSprites) {
      const [col, row] = key.split(",").map(Number);
      const tile = this.tiles[row]?.[col];
      if (!tile?.placedObject) {
        sprite.destroy();
        this.objectSprites.delete(key);
      }
    }

    // Create/update sprites for all placed objects
    for (const row of this.tiles) {
      for (const tile of row) {
        if (!tile.placedObject) continue;
        const key = `${tile.col},${tile.row}`;
        const { x, y } = this.gridToScreen(tile.col, tile.row);
        const cx = x + ISO_TILE_W / 2;
        const cy = y + ISO_TILE_H / 2 - 8;

        if (!this.objectSprites.has(key)) {
          const emoji =
            (OBJECT_EMOJI[tile.placedObject]?.[tile.objectStage] ?? "🌱");
          const text = this.add
            .text(cx, cy, emoji, { fontSize: "18px" })
            .setOrigin(0.5)
            .setDepth((tile.col + tile.row) * 10 + 5);
          this.objectSprites.set(key, text);
        } else {
          const sprite = this.objectSprites.get(key)!;
          const emoji =
            (OBJECT_EMOJI[tile.placedObject]?.[tile.objectStage] ?? "🌱");
          sprite.setText(emoji);
          sprite.setPosition(cx, cy);
        }
      }
    }
  }

  // ─── Ecosystem simulation ─────────────────────────────────────────────────────

  private simulateTicks(ticks: number) {
    for (let t = 0; t < ticks; t++) {
      this.progressObjectStages();
      this.applyObjectEffects();
      this.applyDegradation();
    }
    EventBus.emit(EVENTS.ECOSYSTEM_CHANGED, this.computeGlobalState());
  }

  private progressObjectStages() {
    const now = Date.now() / 1000;
    for (const rowArr of this.tiles) {
      for (const tile of rowArr) {
        if (!tile.placedObject || !tile.placedAt) continue;
        const age = now - tile.placedAt;
        let newStage: ObjectStage;
        if (age >= OBJECT_STAGE_3_S) newStage = 3;
        else if (age >= OBJECT_STAGE_2_S) newStage = 2;
        else if (age >= OBJECT_STAGE_1_S) newStage = 1;
        else newStage = 0;
        tile.objectStage = newStage;
      }
    }
  }

  private applyObjectEffects() {
    for (const rowArr of this.tiles) {
      for (const tile of rowArr) {
        if (!tile.placedObject || tile.objectStage < 1) continue;
        const action = this.getActionData(tile.placedObject);
        if (!action) continue;

        const radius = SPREAD_RADIUS[tile.placedObject] ?? 2;
        const stageMult = [0, 0.3, 0.7, 1.0][tile.objectStage] ?? 0;

        for (let dr = -radius; dr <= radius; dr++) {
          for (let dc = -radius; dc <= radius; dc++) {
            const dist = Math.sqrt(dr * dr + dc * dc);
            if (dist > radius) continue;
            const neighbor = this.tiles[tile.row + dr]?.[tile.col + dc];
            if (!neighbor || neighbor.groundType === "concrete") continue;

            const falloff = 1 - dist / radius;
            const factor = stageMult * falloff * 0.08; // per tick

            neighbor.health = clamp(neighbor.health + action.soil_impact * factor * 10);
            neighbor.pollution = clamp(
              neighbor.pollution - action.air_impact * factor * 10,
            );
            neighbor.moisture = clamp(
              neighbor.moisture + action.water_impact * factor * 10,
            );
          }
        }
      }
    }
  }

  private applyDegradation() {
    for (const rowArr of this.tiles) {
      for (const tile of rowArr) {
        if (tile.groundType === "concrete" || tile.groundType === "water") continue;
        // Passive health decay from pollution
        if (tile.pollution > 30) {
          tile.health = clamp(tile.health - 0.01);
        }
        // Pollution spreads slowly from highly polluted tiles
        if (tile.pollution > 60) {
          for (const [dr, dc] of [
            [0, 1],
            [1, 0],
            [0, -1],
            [-1, 0],
          ]) {
            const neighbor = this.tiles[tile.row + dr]?.[tile.col + dc];
            if (neighbor && neighbor.groundType !== "concrete") {
              neighbor.pollution = clamp(neighbor.pollution + 0.005);
            }
          }
        }
      }
    }
  }

  // Simple action data lookup (impacts used for spreading effect)
  private getActionData(actionKey: string) {
    const defaults: Record<string, { air_impact: number; water_impact: number; soil_impact: number }> =
      {
        plant_tree: { air_impact: 0.8, water_impact: 0.2, soil_impact: 0.6 },
        plant_flowers: { air_impact: 0.3, water_impact: 0.1, soil_impact: 0.4 },
        care_garden: { air_impact: 0.4, water_impact: 0.2, soil_impact: 0.5 },
        clean_water: { air_impact: 0.2, water_impact: 1.0, soil_impact: 0.3 },
        save_water: { air_impact: 0.1, water_impact: 0.8, soil_impact: 0.2 },
        sort_waste: { air_impact: 0.6, water_impact: 0.3, soil_impact: 0.7 },
        recycle: { air_impact: 0.5, water_impact: 0.2, soil_impact: 0.6 },
        install_solar: { air_impact: 0.9, water_impact: 0.0, soil_impact: 0.2 },
        save_energy: { air_impact: 0.5, water_impact: 0.0, soil_impact: 0.1 },
        protect_animal: { air_impact: 0.3, water_impact: 0.2, soil_impact: 0.4 },
        bird_house: { air_impact: 0.2, water_impact: 0.1, soil_impact: 0.3 },
        save_fish: { air_impact: 0.1, water_impact: 0.9, soil_impact: 0.2 },
      };
    return defaults[actionKey] ?? null;
  }

  private computeGlobalState() {
    let air = 0, water = 0, soil = 0, bio = 0;
    let count = 0;
    for (const rowArr of this.tiles) {
      for (const tile of rowArr) {
        if (tile.groundType === "concrete") continue;
        air += 100 - tile.pollution;
        water += tile.moisture;
        soil += tile.health;
        bio += tile.placedObject ? 15 : 0;
        count++;
      }
    }
    if (count === 0) return { air: 0, water: 0, soil: 0, biodiversity: 0 };
    return {
      air: clamp(air / count),
      water: clamp(water / count),
      soil: clamp(soil / count),
      biodiversity: clamp(bio / count),
    };
  }

  private isLevelComplete(): boolean {
    const s = this.computeGlobalState();
    return (
      s.air >= LEVEL_COMPLETION_THRESHOLD &&
      s.water >= LEVEL_COMPLETION_THRESHOLD &&
      s.soil >= LEVEL_COMPLETION_THRESHOLD &&
      s.biodiversity >= LEVEL_COMPLETION_THRESHOLD
    );
  }

  // ─── Input ───────────────────────────────────────────────────────────────────

  private onPointerMove(pointer: Phaser.Input.Pointer) {
    // Camera pan (right-click or middle-click drag)
    if (pointer.isDown && (pointer.rightButtonDown() || pointer.middleButtonDown())) {
      const cam = this.cameras.main;
      cam.scrollX -= (pointer.x - pointer.prevPosition.x) / cam.zoom;
      cam.scrollY -= (pointer.y - pointer.prevPosition.y) / cam.zoom;
    }

    // Hover highlight
    this.hoveredTile = this.screenToGrid(pointer.x, pointer.y);
  }

  private onPointerDown(pointer: Phaser.Input.Pointer) {
    if (pointer.rightButtonDown() || pointer.middleButtonDown()) return;
    const tile = this.screenToGrid(pointer.x, pointer.y);
    if (!tile) return;

    if (this.selectedTool) {
      this.placeObject(tile.col, tile.row);
    }
  }

  private onPointerOut() {
    this.hoveredTile = null;
  }

  private onWheel(
    _pointer: Phaser.Input.Pointer,
    _gameObjects: unknown,
    _deltaX: number,
    deltaY: number,
  ) {
    const cam = this.cameras.main;
    cam.zoom = Phaser.Math.Clamp(cam.zoom - deltaY * 0.0008, 0.4, 2.5);
  }

  // ─── Object placement ────────────────────────────────────────────────────────

  private placeObject(col: number, row: number) {
    const tile = this.tiles[row]?.[col];
    if (!tile || !this.selectedTool) return;
    if (tile.groundType === "concrete" || tile.groundType === "water") return;
    if (tile.placedObject) return; // already occupied

    const cost = this.getActionCost(this.selectedTool);
    if (this.resources < cost) return; // not enough coins

    tile.placedObject = this.selectedTool;
    tile.objectStage = 0;
    tile.placedAt = Date.now() / 1000;

    this.resources -= cost;
    EventBus.emit(EVENTS.RESOURCES_CHANGED, {
      resources: this.resources,
      maxResources: this.maxResources,
    });

    // Notify React for score + API sync
    EventBus.emit(EVENTS.ACTION_PERFORMED, {
      actionKey: this.selectedTool,
      positionX: col,
      positionY: row,
    });
    EventBus.emit(EVENTS.SCORE_UPDATED, { score: this.getActionScore(this.selectedTool) });

    // Floating "+points" feedback
    this.showFeedback(col, row, this.selectedTool);

    // World sync event for backend persistence
    EventBus.emit(EVENTS.WORLD_SYNC, {
      placements: [{ actionKey: this.selectedTool, col, row }],
      removals: [],
    });

    this.redrawObjectLayer();
  }

  private getActionCost(actionKey: string): number {
    const COSTS: Record<string, number> = {
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
    return COSTS[actionKey] ?? 10;
  }

  private getActionScore(actionKey: string): number {
    const SCORES: Record<string, number> = {
      plant_tree: 30,
      plant_flowers: 15,
      care_garden: 20,
      clean_water: 35,
      save_water: 15,
      sort_waste: 25,
      recycle: 20,
      install_solar: 40,
      save_energy: 15,
      protect_animal: 40,
      bird_house: 25,
      save_fish: 35,
    };
    return SCORES[actionKey] ?? 10;
  }

  private showFeedback(col: number, row: number, actionKey: string) {
    const { x, y } = this.gridToScreen(col, row);
    const cx = x + ISO_TILE_W / 2;
    const score = this.getActionScore(actionKey);

    const text = this.add
      .text(cx, y, `+${score}`, {
        fontSize: "14px",
        fontStyle: "bold",
        color: "#ffffff",
        stroke: "#000000",
        strokeThickness: 3,
      })
      .setOrigin(0.5)
      .setDepth(9999);

    this.tweens.add({
      targets: text,
      y: y - 40,
      alpha: 0,
      duration: 1200,
      ease: "Power2",
      onComplete: () => text.destroy(),
    });
  }
}

// ─── Utilities ────────────────────────────────────────────────────────────────

function clamp(v: number, min = 0, max = 100): number {
  return Math.min(max, Math.max(min, v));
}
