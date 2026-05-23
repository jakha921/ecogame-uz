import Phaser from "phaser";
import { EVENTS, EventBus, type EcosystemChangedPayload, type ScoreUpdatedPayload } from "../events/EventBus";

const BAR_WIDTH = 140;
const BAR_HEIGHT = 12;
const HUD_Y = 16;
const LABELS = ["Havo", "Suv", "Tuproq", "Biologik"];
const COLORS = [0x87ceeb, 0x00bcd4, 0x8d6e63, 0x4caf50];

export class HUDScene extends Phaser.Scene {
  private bars: Phaser.GameObjects.Rectangle[] = [];
  private barBgs: Phaser.GameObjects.Rectangle[] = [];
  private scoreText!: Phaser.GameObjects.Text;
  private score = 0;

  constructor() {
    super({ key: "HUDScene" });
  }

  create() {
    const startX = 10;
    const spacing = 155;

    LABELS.forEach((label, i) => {
      const x = startX + i * spacing;

      this.add.text(x, HUD_Y, label, { fontSize: "10px", color: "#ffffff" }).setDepth(10);

      const bg = this.add
        .rectangle(x, HUD_Y + 16, BAR_WIDTH, BAR_HEIGHT, 0x333333)
        .setOrigin(0, 0.5)
        .setDepth(10);
      this.barBgs.push(bg);

      const bar = this.add
        .rectangle(x, HUD_Y + 16, 0, BAR_HEIGHT, COLORS[i])
        .setOrigin(0, 0.5)
        .setDepth(11);
      this.bars.push(bar);
    });

    this.scoreText = this.add
      .text(790, HUD_Y + 4, "Ball: 0", { fontSize: "12px", color: "#ffd700" })
      .setOrigin(1, 0)
      .setDepth(10);

    // Subscribe to EventBus
    EventBus.on(EVENTS.ECOSYSTEM_CHANGED, this.onEcosystemChanged, this);
    EventBus.on(EVENTS.SCORE_UPDATED, this.onScoreUpdated, this);
    this.events.on(Phaser.Scenes.Events.SHUTDOWN, this.cleanup, this);
  }

  private onEcosystemChanged(payload: EcosystemChangedPayload) {
    const values = [payload.air, payload.water, payload.soil, payload.biodiversity];
    values.forEach((v, i) => {
      this.bars[i].width = (Math.min(100, Math.max(0, v)) / 100) * BAR_WIDTH;
    });
  }

  private onScoreUpdated(payload: ScoreUpdatedPayload) {
    this.score += payload.score;
    this.scoreText.setText(`Ball: ${this.score}`);
  }

  private cleanup() {
    EventBus.off(EVENTS.ECOSYSTEM_CHANGED, this.onEcosystemChanged, this);
    EventBus.off(EVENTS.SCORE_UPDATED, this.onScoreUpdated, this);
  }
}
