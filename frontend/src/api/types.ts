export interface Player {
  id: number;
  username: string;
  nickname: string;
  email: string;
  avatar: string;
  total_score: number;
  date_joined: string;
}

export interface EcosystemState {
  air: number;
  water: number;
  soil: number;
  biodiversity: number;
}

export interface MapZone {
  type: "FLORA" | "WATER" | "WASTE" | "ENERGY" | "FAUNA";
  x: number;
  y: number;
  label?: string;
}

export interface MapConfig {
  width: number;
  height: number;
  zones: MapZone[];
}

export interface Level {
  id: number;
  number: number;
  name_uz: string;
  description_uz: string;
  required_score: number;
  map_config: MapConfig;
  ecosystem_initial: EcosystemState;
  is_unlocked: boolean;
}

export type ActionCategory = "FLORA" | "WATER" | "WASTE" | "ENERGY" | "FAUNA";

export interface EcoAction {
  id: number;
  key: string;
  name_uz: string;
  description_uz: string;
  category: ActionCategory;
  score_value: number;
  air_impact: number;
  water_impact: number;
  soil_impact: number;
  biodiversity_impact: number;
  cooldown_seconds: number;
  unlock_level: number;
  sprite_key: string;
}

export interface GameProgress {
  id: number;
  level: Level;
  score: number;
  air_quality: number;
  water_purity: number;
  soil_health: number;
  biodiversity: number;
  actions_performed: Record<string, number>;
  completed: boolean;
  completed_at: string | null;
  updated_at: string;
}

export interface GameSession {
  id: number;
  level: Level;
  started_at: string;
  ended_at: string | null;
  is_active: boolean;
}

export type ConditionType = "SCORE" | "ACTION_COUNT" | "LEVEL_COMPLETE" | "INDICATOR";

export interface Achievement {
  id: number;
  key: string;
  name_uz: string;
  description_uz: string;
  icon: string;
  condition_type: ConditionType;
  is_unlocked: boolean;
}

export interface PlayerAchievement {
  id: number;
  achievement: Achievement;
  unlocked_at: string;
}

export interface LeaderboardEntry {
  rank: number;
  player_nickname: string;
  player_avatar: string;
  total_score: number;
  levels_completed: number;
  achievements_count: number;
}

export interface EducationalContent {
  id: number;
  title_uz: string;
  body_uz: string;
  category: ActionCategory;
  image: string | null;
  order: number;
}

export interface EcoFact {
  id: number;
  text_uz: string;
  source: string;
  category: ActionCategory;
}

export interface AuthTokens {
  access: string;
  refresh: string;
}

export interface RegisterData {
  username: string;
  nickname: string;
  email: string;
  password: string;
  password_confirm: string;
}

export interface LoginData {
  username: string;
  password: string;
}

export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

export interface ActionItem {
  action_key: string;
  position_x: number;
  position_y: number;
}
