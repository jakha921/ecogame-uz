export class ScoreSystem {
  private score = 0;
  private lastActionTime = 0;
  private readonly comboWindowMs = 2000;
  private comboCount = 0;

  addPoints(base: number): number {
    const now = Date.now();
    if (now - this.lastActionTime < this.comboWindowMs) {
      this.comboCount++;
    } else {
      this.comboCount = 0;
    }
    this.lastActionTime = now;

    // Combo bonus: 1.5x after 3 quick consecutive actions
    const multiplier = this.comboCount >= 3 ? 1.5 : 1.0;
    const points = Math.round(base * multiplier);
    this.score += points;
    return points;
  }

  getScore(): number {
    return this.score;
  }
}
