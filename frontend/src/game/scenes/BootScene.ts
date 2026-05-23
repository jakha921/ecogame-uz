import Phaser from "phaser";

export class BootScene extends Phaser.Scene {
  constructor() {
    super({ key: "BootScene" });
  }

  preload() {
    // Load minimal assets for progress bar display
    this.load.setBaseURL("/assets");
  }

  create() {
    this.scene.start("PreloadScene");
  }
}
