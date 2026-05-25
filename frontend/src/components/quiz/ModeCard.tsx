interface ModeCardProps {
  title: string;
  description: string;
  icon: React.ReactNode;
  color: string;
  onClick: () => void;
  badge?: string;
}

export function ModeCard({ title, description, icon, color, onClick, badge }: ModeCardProps) {
  return (
    <button
      onClick={onClick}
      className="bg-white rounded-2xl border-2 border-transparent hover:border-green-400 hover:shadow-xl p-5 flex items-start gap-4 text-left transition-all w-full cursor-pointer"
    >
      <div className={`rounded-xl p-3 flex-shrink-0 ${color}`}>{icon}</div>
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2">
          <p className="font-bold text-gray-800">{title}</p>
          {badge && (
            <span className="text-xs font-semibold bg-green-100 text-green-700 px-2 py-0.5 rounded-full">
              {badge}
            </span>
          )}
        </div>
        <p className="text-sm text-gray-500 mt-0.5">{description}</p>
      </div>
    </button>
  );
}
