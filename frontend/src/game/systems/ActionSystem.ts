import type { EcosystemManager, EcosystemState } from "./EcosystemManager";

export class ActionSystem {
  private cooldowns = new Map<string, number>();
  private readonly cooldownMs = 500;
  private ecosystemManager: EcosystemManager;

  constructor(ecosystemManager: EcosystemManager) {
    this.ecosystemManager = ecosystemManager;
  }

  applyZoneAction(zoneType: string): EcosystemState | null {
    const now = Date.now();
    const lastUsed = this.cooldowns.get(zoneType) ?? 0;
    if (now - lastUsed < this.cooldownMs) return null;

    this.cooldowns.set(zoneType, now);
    return this.ecosystemManager.applyZoneImpact(zoneType);
  }
}
