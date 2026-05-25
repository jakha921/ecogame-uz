export type BinType = "recyclable" | "organic" | "landfill";

export interface SortingItem {
  id: string;
  name_uz: string;
  emoji: string;
  correct_bin: BinType;
  points: number;
}

export const SORTING_ITEMS: SortingItem[] = [
  { id: "plastic_bottle", name_uz: "Plastik shisha", emoji: "🧴", correct_bin: "recyclable", points: 10 },
  { id: "glass_jar", name_uz: "Shisha banka", emoji: "🫙", correct_bin: "recyclable", points: 10 },
  { id: "paper", name_uz: "Qog'oz", emoji: "📄", correct_bin: "recyclable", points: 10 },
  { id: "cardboard", name_uz: "Karton quti", emoji: "📦", correct_bin: "recyclable", points: 10 },
  { id: "aluminum_can", name_uz: "Alyuminiy banka", emoji: "🥫", correct_bin: "recyclable", points: 10 },
  { id: "food_waste", name_uz: "Ovqat qoldiqlari", emoji: "🍌", correct_bin: "organic", points: 10 },
  { id: "leaves", name_uz: "Barglar", emoji: "🍂", correct_bin: "organic", points: 10 },
  { id: "eggshell", name_uz: "Tuxum po'chog'i", emoji: "🥚", correct_bin: "organic", points: 10 },
  { id: "coffee_grounds", name_uz: "Qahva qoldig'i", emoji: "☕", correct_bin: "organic", points: 10 },
  { id: "flower", name_uz: "Gul", emoji: "🌻", correct_bin: "organic", points: 10 },
  { id: "battery", name_uz: "Batareya", emoji: "🔋", correct_bin: "landfill", points: 15 },
  { id: "phone", name_uz: "Eski telefon", emoji: "📱", correct_bin: "landfill", points: 15 },
  { id: "diaper", name_uz: "Bir martalik taomil", emoji: "🧷", correct_bin: "landfill", points: 10 },
  { id: "chip_bag", name_uz: "Chips paketi", emoji: "🛍️", correct_bin: "landfill", points: 10 },
  { id: "styrofoam", name_uz: "Styrofoam", emoji: "📦", correct_bin: "landfill", points: 10 },
  { id: "metal_can", name_uz: "Metal quti", emoji: "🥫", correct_bin: "recyclable", points: 10 },
  { id: "newspaper", name_uz: "Gazeta", emoji: "📰", correct_bin: "recyclable", points: 10 },
  { id: "fruit_peel", name_uz: "Meva po'chog'i", emoji: "🍊", correct_bin: "organic", points: 10 },
  { id: "light_bulb", name_uz: "Chiroq (energiyatejamkor)", emoji: "💡", correct_bin: "landfill", points: 15 },
  { id: "wire", name_uz: "Sim", emoji: "🔌", correct_bin: "landfill", points: 15 },
];
