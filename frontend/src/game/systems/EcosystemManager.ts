import { INDICATOR_MAX, INDICATOR_MIN } from "../data/constants";

export interface EcosystemState {
  air: number;
  water: number;
  soil: number;
  biodiversity: number;
}

// Per-second passive degradation
const DEGRADATION = { air: 0.02, water: 0.015, soil: 0.01, biodiversity: 0.025 };

// Impact multiplier per zone click
const ZONE_IMPACT: Record<string, Partial<EcosystemState>> = {
  FLORA: { air: 3, soil: 2, biodiversity: 2 },
  WATER: { water: 4, biodiversity: 1 },
  WASTE: { air: 1, soil: 3 },
  ENERGY: { air: 2 },
  FAUNA: { biodiversity: 4, air: 1 },
};

function clamp(v: number): number {
  return Math.max(INDICATOR_MIN, Math.min(INDICATOR_MAX, v));
}

export class EcosystemManager {
  private state: EcosystemState;
  private accumMs = 0;

  constructor(air: number, water: number, soil: number, biodiversity: number) {
    this.state = { air, water, soil, biodiversity };
  }

  tick(deltaMs: number) {
    this.accumMs += deltaMs;
    // Apply degradation once per second
    if (this.accumMs < 1000) return;
    const seconds = Math.floor(this.accumMs / 1000);
    this.accumMs -= seconds * 1000;

    this.state.air = clamp(this.state.air - DEGRADATION.air * seconds);
    this.state.water = clamp(this.state.water - DEGRADATION.water * seconds);
    this.state.soil = clamp(this.state.soil - DEGRADATION.soil * seconds);
    this.state.biodiversity = clamp(this.state.biodiversity - DEGRADATION.biodiversity * seconds);

    // Compound: high biodiversity slightly boosts others
    if (this.state.biodiversity > 50) {
      const bonus = ((this.state.biodiversity - 50) / 10) * 0.005 * seconds;
      this.state.air = clamp(this.state.air + bonus);
      this.state.water = clamp(this.state.water + bonus);
      this.state.soil = clamp(this.state.soil + bonus);
    }
  }

  applyZoneImpact(zoneType: string): EcosystemState {
    const impact = ZONE_IMPACT[zoneType] ?? {};
    if (impact.air) this.state.air = clamp(this.state.air + impact.air);
    if (impact.water) this.state.water = clamp(this.state.water + impact.water);
    if (impact.soil) this.state.soil = clamp(this.state.soil + impact.soil);
    if (impact.biodiversity) this.state.biodiversity = clamp(this.state.biodiversity + impact.biodiversity);
    return { ...this.state };
  }

  getState(): EcosystemState {
    return { ...this.state };
  }
}
