import Phaser from "phaser";
import type { Level, MapZone } from "@/api/types";
import { GAME_HEIGHT, GAME_WIDTH, LEVEL_COMPLETION_THRESHOLD, TILE_SIZE } from "../data/constants";
import { EVENTS, EventBus } from "../events/EventBus";
import { EcosystemManager } from "../systems/EcosystemManager";
import { ActionSystem } from "../systems/ActionSystem";
import { ScoreSystem } from "../systems/ScoreSystem";

const ZONE_COLORS: Record<string, number> = {
  FLORA: 0x4caf50,
  WATER: 0x2196f3,
  WASTE: 0xff9800,
  ENERGY: 0xffc107,
  FAUNA: 0x9c27b0,
};

const ZONE_EMOJI: Record<string, string> = {
  FLORA: "🌳",
  WATER: "💧",
  WASTE: "♻️",
  ENERGY: "☀️",
  FAUNA: "🦁",
};

export class MainScene extends Phaser.Scene {
  private ecosystemManager!: EcosystemManager;
  private actionSystem!: ActionSystem;
  private scoreSystem!: ScoreSystem;
  private levelConfig!: Level;
  private zoneObjects: Phaser.GameObjects.Container[] = [];
  private completionEmitted = false;

  constructor() {
    super({ key: "MainScene" });
  }

  create() {
    this.levelConfig = this.registry.get("levelConfig") as Level;

    this.drawBackground();
    this.drawGrid();
    this.createZones();

    const initial = this.levelConfig.ecosystem_initial;
    this.ecosystemManager = new EcosystemManager(
      initial.air,
      initial.water,
      initial.soil,
      initial.biodiversity,
    );
    this.actionSystem = new ActionSystem(this.ecosystemManager);
    this.scoreSystem = new ScoreSystem();

    // Emit initial ecosystem state for HUD
    EventBus.emit(EVENTS.ECOSYSTEM_CHANGED, this.ecosystemManager.getState());
  }

  update(_time: number, delta: number) {
    this.ecosystemManager.tick(delta);
    EventBus.emit(EVENTS.ECOSYSTEM_CHANGED, this.ecosystemManager.getState());
    this.updateVisuals();

    if (!this.completionEmitted && this.isLevelComplete()) {
      this.completionEmitted = true;
      EventBus.emit(EVENTS.LEVEL_COMPLETED, { levelNumber: this.levelConfig.number });
    }
  }

  private drawBackground() {
    // Sky gradient via rectangles
    this.add.rectangle(GAME_WIDTH / 2, GAME_HEIGHT / 2, GAME_WIDTH, GAME_HEIGHT, 0x87ceeb);
    // Ground strip
    this.add.rectangle(GAME_WIDTH / 2, GAME_HEIGHT - 40, GAME_WIDTH, 80, 0x6a9e5a);
  }

  private drawGrid() {
    const graphics = this.add.graphics();
    graphics.lineStyle(1, 0xffffff, 0.1);

    const cols = Math.floor(GAME_WIDTH / TILE_SIZE);
    const rows = Math.floor(GAME_HEIGHT / TILE_SIZE);

    for (let c = 0; c <= cols; c++) {
      graphics.moveTo(c * TILE_SIZE, 0);
      graphics.lineTo(c * TILE_SIZE, GAME_HEIGHT);
    }
    for (let r = 0; r <= rows; r++) {
      graphics.moveTo(0, r * TILE_SIZE);
      graphics.lineTo(GAME_WIDTH, r * TILE_SIZE);
    }
    graphics.strokePath();
  }

  private createZones() {
    const zones: MapZone[] = this.levelConfig.map_config?.zones ?? [];

    zones.forEach((zone) => {
      const px = zone.x * TILE_SIZE;
      const py = zone.y * TILE_SIZE + 40; // offset for HUD

      const container = this.add.container(px, py);

      // Zone background
      const bg = this.add.rectangle(0, 0, TILE_SIZE * 2, TILE_SIZE * 2, ZONE_COLORS[zone.type] ?? 0x888888, 0.7);
      bg.setInteractive({ useHandCursor: true });

      // Emoji label
      const label = this.add
        .text(0, -4, ZONE_EMOJI[zone.type] ?? "?", { fontSize: "20px" })
        .setOrigin(0.5);

      const typeText = this.add
        .text(0, 20, zone.label ?? zone.type, { fontSize: "8px", color: "#ffffff" })
        .setOrigin(0.5);

      container.add([bg, label, typeText]);
      this.zoneObjects.push(container);

      // Pulse animation
      this.tweens.add({
        targets: bg,
        alpha: { from: 0.7, to: 1.0 },
        duration: 1200 + Math.random() * 800,
        yoyo: true,
        repeat: -1,
      });

      // Click → perform action
      bg.on(Phaser.Input.Events.POINTER_DOWN, () => {
        this.handleZoneClick(zone, px, py);
      });
    });
  }

  private handleZoneClick(zone: MapZone, px: number, py: number) {
    const delta = this.actionSystem.applyZoneAction(zone.type);
    if (!delta) return;

    // Score
    const points = this.scoreSystem.addPoints(10);
    EventBus.emit(EVENTS.SCORE_UPDATED, { score: points });

    // Visual feedback
    this.showActionFeedback(px, py, zone.type);

    // Notify React for API sync
    EventBus.emit(EVENTS.ACTION_PERFORMED, {
      actionKey: this.zoneTypeToActionKey(zone.type),
      positionX: px,
      positionY: py,
    });
  }

  private showActionFeedback(x: number, y: number, zoneType: string) {
    const emoji = ZONE_EMOJI[zoneType] ?? "✨";
    const text = this.add
      .text(x + TILE_SIZE, y, `${emoji} +10`, {
        fontSize: "14px",
        color: "#ffffff",
        stroke: "#000",
        strokeThickness: 2,
      })
      .setOrigin(0.5);

    this.tweens.add({
      targets: text,
      y: y - 40,
      alpha: 0,
      duration: 1000,
      onComplete: () => text.destroy(),
    });
  }

  private zoneTypeToActionKey(zoneType: string): string {
    const map: Record<string, string> = {
      FLORA: "plant_tree",
      WATER: "clean_water",
      WASTE: "sort_waste",
      ENERGY: "install_solar",
      FAUNA: "protect_animal",
    };
    return map[zoneType] ?? zoneType.toLowerCase();
  }

  private updateVisuals() {
    const state = this.ecosystemManager.getState();
    // Sky color based on air quality
    const airRatio = state.air / 100;
    const skyR = Math.floor(100 + airRatio * 35);
    const skyG = Math.floor(149 + airRatio * 57);
    const skyB = Math.floor(180 + airRatio * 55);
    this.cameras.main.setBackgroundColor(
      `rgb(${skyR},${skyG},${skyB})`,
    );
  }

  private isLevelComplete(): boolean {
    const s = this.ecosystemManager.getState();
    return (
      s.air >= LEVEL_COMPLETION_THRESHOLD &&
      s.water >= LEVEL_COMPLETION_THRESHOLD &&
      s.soil >= LEVEL_COMPLETION_THRESHOLD &&
      s.biodiversity >= LEVEL_COMPLETION_THRESHOLD
    );
  }
}
