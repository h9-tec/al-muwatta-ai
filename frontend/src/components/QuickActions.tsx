import { BookOpen, Sparkles, Search, Heart } from 'lucide-react';

interface QuickAction {
  icon: React.ReactNode;
  label: string;
  prompt: string;
  gradient: string;
}

const quickActions: QuickAction[] = [
  {
    icon: <BookOpen size={20} />,
    label: 'Surah Al-Fatiha',
    prompt: 'Please show me Surah Al-Fatiha with translation',
    gradient: 'from-emerald-500 to-teal-500',
  },
  {
    icon: <Sparkles size={20} />,
    label: 'Daily Reminder',
    prompt: 'Give me a daily Islamic reminder about gratitude',
    gradient: 'from-purple-500 to-pink-500',
  },
  {
    icon: <Search size={20} />,
    label: 'Search Hadith',
    prompt: 'Search for Hadiths about prayer',
    gradient: 'from-blue-500 to-cyan-500',
  },
  {
    icon: <Heart size={20} />,
    label: '99 Names',
    prompt: 'Tell me about the 99 names of Allah',
    gradient: 'from-rose-500 to-orange-500',
  },
];

interface QuickActionsProps {
  onActionClick: (prompt: string) => void;
}

export function QuickActions({ onActionClick }: QuickActionsProps) {
  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-3 p-4">
      {quickActions.map((action) => (
        <button
          key={action.label}
          onClick={() => onActionClick(action.prompt)}
          className="group relative overflow-hidden rounded-xl p-4 text-white shadow-lg hover:shadow-xl transition-all duration-300 hover:scale-105"
          style={{
            background: `linear-gradient(135deg, var(--tw-gradient-stops))`,
          }}
        >
          <div className={`absolute inset-0 bg-gradient-to-br ${action.gradient} opacity-90 group-hover:opacity-100 transition-opacity`}></div>
          <div className="relative z-10 flex flex-col items-center gap-2 text-center">
            <div className="p-2 bg-white/20 rounded-lg backdrop-blur-sm">
              {action.icon}
            </div>
            <span className="text-sm font-medium">{action.label}</span>
          </div>
        </button>
      ))}
    </div>
  );
}

