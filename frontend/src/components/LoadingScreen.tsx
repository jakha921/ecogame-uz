interface LoadingScreenProps {
  factText?: string;
}

export function LoadingScreen({ factText }: LoadingScreenProps) {
  return (
    <div className="flex flex-col items-center justify-center min-h-[60vh] gap-6">
      <div className="w-16 h-16 border-4 border-green-200 border-t-green-600 rounded-full animate-spin" />
      <p className="text-green-700 font-semibold text-lg">Yuklanmoqda...</p>
      {factText && (
        <div className="max-w-sm text-center bg-green-50 rounded-xl p-4">
          <p className="text-xs text-green-600 font-semibold mb-1">💡 Bilasizmi?</p>
          <p className="text-sm text-gray-600">{factText}</p>
        </div>
      )}
    </div>
  );
}
