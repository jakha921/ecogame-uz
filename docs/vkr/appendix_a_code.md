# Приложение А. Ключевые фрагменты исходного кода

## А.1. Модели базы данных (`backend/apps/game/models.py`)

```python
class Level(models.Model):
    """Уровень игры — определяет карту и начальное состояние экосистемы."""

    number = models.PositiveSmallIntegerField(unique=True, verbose_name="Номер уровня")
    name_uz = models.CharField(max_length=100, verbose_name="Название (уз)")
    description_uz = models.TextField(verbose_name="Описание (уз)")
    required_score = models.PositiveIntegerField(default=0, verbose_name="Очки для разблокировки")
    map_config = models.JSONField(default=dict, verbose_name="Конфигурация карты")
    ecosystem_initial = models.JSONField(
        default=dict, verbose_name="Начальные значения экосистемы"
    )

    class Meta:
        verbose_name = "Уровень"
        verbose_name_plural = "Уровни"
        ordering = ["number"]

    def __str__(self) -> str:
        return f"Уровень {self.number}: {self.name_uz}"


class EcoAction(models.Model):
    """Каталог экологических действий игрока."""

    class Category(models.TextChoices):
        FLORA = "FLORA", "Флора"
        WATER = "WATER", "Вода"
        WASTE = "WASTE", "Отходы"
        ENERGY = "ENERGY", "Энергия"
        FAUNA = "FAUNA", "Фауна"

    key = models.CharField(max_length=50, unique=True, verbose_name="Ключ")
    name_uz = models.CharField(max_length=100, verbose_name="Название (уз)")
    description_uz = models.TextField(verbose_name="Описание (уз)")
    category = models.CharField(
        max_length=10, choices=Category.choices, verbose_name="Категория"
    )
    score_value = models.PositiveIntegerField(verbose_name="Очки")
    air_impact = models.FloatField(default=0.0, verbose_name="Влияние на воздух")
    water_impact = models.FloatField(default=0.0, verbose_name="Влияние на воду")
    soil_impact = models.FloatField(default=0.0, verbose_name="Влияние на почву")
    biodiversity_impact = models.FloatField(
        default=0.0, verbose_name="Влияние на биоразнообразие"
    )
    cooldown_seconds = models.PositiveIntegerField(default=30, verbose_name="Кулдаун (сек)")
    unlock_level = models.ForeignKey(
        Level, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="unlocked_actions", verbose_name="Уровень разблокировки"
    )
    sprite_key = models.CharField(max_length=50, verbose_name="Ключ спрайта")

    class Meta:
        verbose_name = "Экологическое действие"
        verbose_name_plural = "Экологические действия"
        ordering = ["category", "key"]

    def __str__(self) -> str:
        return f"{self.get_category_display()}: {self.name_uz}"


class GameProgress(models.Model):
    """Прогресс игрока на конкретном уровне."""

    player = models.ForeignKey(
        "accounts.Player", on_delete=models.CASCADE, related_name="progress",
        verbose_name="Игрок"
    )
    level = models.ForeignKey(
        Level, on_delete=models.CASCADE, related_name="progress", verbose_name="Уровень"
    )
    score = models.PositiveIntegerField(default=0, verbose_name="Очки")
    air_quality = models.FloatField(default=0.0, verbose_name="Качество воздуха")
    water_purity = models.FloatField(default=0.0, verbose_name="Чистота воды")
    soil_health = models.FloatField(default=0.0, verbose_name="Здоровье почвы")
    biodiversity = models.FloatField(default=0.0, verbose_name="Биоразнообразие")
    actions_performed = models.JSONField(default=dict, verbose_name="Выполненные действия")
    completed = models.BooleanField(default=False, verbose_name="Завершён")
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name="Дата завершения")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Обновлён")

    class Meta:
        verbose_name = "Прогресс игры"
        verbose_name_plural = "Прогресс игры"
        unique_together = ("player", "level")

    def __str__(self) -> str:
        return f"{self.player.nickname} — Уровень {self.level.number} ({self.score} очков)"
```

## А.2. Сервис игровой логики (`backend/apps/game/services.py`)

```python
class GameService:
    """Бизнес-логика игры. Все мутации прогресса проходят через этот сервис."""

    @staticmethod
    @transaction.atomic
    def perform_actions(
        session: GameSession, actions: list[dict]
    ) -> GameProgress:
        """Обработать батч действий, обновить прогресс и экосистемные индикаторы."""
        progress, _ = GameProgress.objects.select_for_update().get_or_create(
            player=session.player, level=session.level,
            defaults=GameService._initial_progress(session.level),
        )

        for action_data in actions:
            try:
                action = EcoAction.objects.get(key=action_data["action_key"])
            except EcoAction.DoesNotExist:
                continue

            # Обновить индикаторы экосистемы
            deltas = GameService.calculate_ecosystem(progress, action)
            progress.air_quality = min(100.0, max(0.0, progress.air_quality + deltas["air"]))
            progress.water_purity = min(100.0, max(0.0, progress.water_purity + deltas["water"]))
            progress.soil_health = min(100.0, max(0.0, progress.soil_health + deltas["soil"]))
            progress.biodiversity = min(
                100.0, max(0.0, progress.biodiversity + deltas["biodiversity"])
            )
            progress.score += action.score_value

            # Записать в лог
            ActionLog.objects.create(
                session=session,
                action=action,
                position_x=action_data.get("position_x", 0.0),
                position_y=action_data.get("position_y", 0.0),
                result_delta=deltas,
            )

            # Обновить счётчик действий
            counts = progress.actions_performed
            counts[action.key] = counts.get(action.key, 0) + 1
            progress.actions_performed = counts

        # Проверить завершение уровня
        if GameService.check_level_completion(progress):
            progress.completed = True
            progress.completed_at = timezone.now()

        progress.save()
        GameService.check_achievements(session.player, progress)
        return progress

    @staticmethod
    def calculate_ecosystem(progress: GameProgress, action: EcoAction) -> dict:
        """Рассчитать изменения индикаторов с учётом compound-эффектов."""
        multiplier = 1.0
        # Compound: высокое биоразнообразие усиливает эффект флора-действий
        if action.category == EcoAction.Category.FLORA and progress.biodiversity > 50:
            multiplier += (progress.biodiversity - 50) / 200  # до +25%

        return {
            "air": action.air_impact * 10 * multiplier,
            "water": action.water_impact * 10 * multiplier,
            "soil": action.soil_impact * 10 * multiplier,
            "biodiversity": action.biodiversity_impact * 10 * multiplier,
        }

    @staticmethod
    def check_level_completion(progress: GameProgress) -> bool:
        """Уровень завершён, когда все 4 индикатора достигают 80."""
        return all([
            progress.air_quality >= 80.0,
            progress.water_purity >= 80.0,
            progress.soil_health >= 80.0,
            progress.biodiversity >= 80.0,
        ])
```

## А.3. EventBus — связь Phaser.js с React (`frontend/src/game/events/EventBus.ts`)

```typescript
import Phaser from "phaser";

/**
 * Singleton EventEmitter для двусторонней связи Phaser ↔ React.
 * React-компоненты подписываются через EventBus.on(), Phaser-сцены — через emit().
 *
 * Используемые события:
 *   "score-updated"        → { score: number }
 *   "ecosystem-changed"    → EcosystemState
 *   "action-performed"     → ActionLogEntry
 *   "achievement-unlocked" → { achievementKey: string; nameUz: string }
 *   "level-completed"      → { levelNumber: number }
 *   "game-paused"          → {}
 *   "game-resumed"         → {}
 */
export const EventBus = new Phaser.Events.EventEmitter();
```

## А.4. EcosystemManager — симуляция экосистемы (`frontend/src/game/systems/EcosystemManager.ts`)

```typescript
export class EcosystemManager {
  private state: EcosystemState;
  private readonly DEGRADATION_RATE = { air: 0.02, water: 0.015, soil: 0.01, biodiversity: 0.025 };

  constructor(initial: EcosystemState) {
    this.state = { ...initial };
  }

  /** Тик деградации (delta в миллисекундах, вызывается из MainScene.update). */
  tick(delta: number): void {
    const seconds = delta / 1000;
    this.state = {
      air: clamp(this.state.air - this.DEGRADATION_RATE.air * seconds),
      water: clamp(this.state.water - this.DEGRADATION_RATE.water * seconds),
      soil: clamp(this.state.soil - this.DEGRADATION_RATE.soil * seconds),
      biodiversity: this.applyCompound(
        clamp(this.state.biodiversity - this.DEGRADATION_RATE.biodiversity * seconds)
      ),
    };
    EventBus.emit("ecosystem-changed", { ...this.state });
  }

  /** Compound-эффект: высокое биоразнообразие замедляет деградацию остальных. */
  private applyCompound(biodiversity: number): number {
    if (this.state.biodiversity > 50) {
      const bonus = (this.state.biodiversity - 50) * 0.0005;
      this.state.air = clamp(this.state.air + bonus);
      this.state.water = clamp(this.state.water + bonus);
      this.state.soil = clamp(this.state.soil + bonus);
    }
    return biodiversity;
  }

  applyAction(action: EcoActionData): void {
    this.state = {
      air: clamp(this.state.air + action.air_impact * 10),
      water: clamp(this.state.water + action.water_impact * 10),
      soil: clamp(this.state.soil + action.soil_impact * 10),
      biodiversity: clamp(this.state.biodiversity + action.biodiversity_impact * 10),
    };
    EventBus.emit("ecosystem-changed", { ...this.state });
  }

  getState(): Readonly<EcosystemState> {
    return this.state;
  }
}

function clamp(value: number): number {
  return Math.min(100, Math.max(0, value));
}
```
