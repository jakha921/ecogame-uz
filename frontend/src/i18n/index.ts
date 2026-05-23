import uz from "./uz.json";

type NestedKeyOf<T, Prefix extends string = ""> = T extends object
  ? {
      [K in keyof T]: K extends string
        ? Prefix extends ""
          ? NestedKeyOf<T[K], K>
          : NestedKeyOf<T[K], `${Prefix}.${K}`>
        : never;
    }[keyof T]
  : Prefix;

type TranslationKey = NestedKeyOf<typeof uz>;

export function t(key: TranslationKey): string {
  const parts = (key as string).split(".");
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  let current: any = uz;
  for (const part of parts) {
    current = current?.[part];
  }
  return typeof current === "string" ? current : key;
}
