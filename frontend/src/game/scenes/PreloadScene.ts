import Phaser from "phaser";
import { GAME_HEIGHT, GAME_WIDTH } from "../data/constants";

export class PreloadScene extends Phaser.Scene {
  constructor() {
    super({ key: "PreloadScene" });
  }

  preload() {
    this.createProgressBar();

    // All assets use programmatic graphics (no external image files required)
    // Sprite textures are generated procedurally in MainScene using Phaser Graphics API
  }

  create() {
    this.scene.start("MainScene");
    this.scene.launch("HUDScene");
  }

  private createProgressBar() {
    const cx = GAME_WIDTH / 2;
    const cy = GAME_HEIGHT / 2;

    const bg = this.add.rectangle(cx, cy, 400, 40, 0x1a1a2e);
    bg.setStrokeStyle(2, 0x4caf50);

    const bar = this.add.rectangle(cx - 198, cy, 0, 36, 0x4caf50);
    bar.setOrigin(0, 0.5);

    const label = this.add
      .text(cx, cy - 40, "EcoGame — Yuklanmoqda...", {
        fontSize: "18px",
        color: "#ffffff",
      })
      .setOrigin(0.5);

    this.load.on("progress", (value: number) => {
      bar.width = 396 * value;
      label.setText(`${Math.round(value * 100)}%`);
    });

    this.load.on("complete", () => {
      label.setText("Tayyor!");
    });
  }
}
