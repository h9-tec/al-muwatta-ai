import { useState } from 'react';
import { Lightbulb, BookOpen, Sparkles, Search, Heart } from 'lucide-react';

interface Suggestion {
  icon: React.ReactNode;
  label: string;
  prompt: string;
}

const suggestions: Suggestion[] = [
  // English suggestions
  {
    icon: <BookOpen size={16} />,
    label: 'Surah Al-Fatiha',
    prompt: 'Please show me Surah Al-Fatiha with translation',
  },
  {
    icon: <Sparkles size={16} />,
    label: 'Daily Reminder',
    prompt: 'Give me a daily Islamic reminder about gratitude',
  },
  {
    icon: <Search size={16} />,
    label: 'Maliki Wudu Ruling',
    prompt: 'What is the Maliki position on wudu?',
  },
  {
    icon: <Heart size={16} />,
    label: '99 Names of Allah',
    prompt: 'Tell me about the 99 names of Allah',
  },
  // Arabic suggestions
  {
    icon: <BookOpen size={16} />,
    label: 'سورة الفاتحة',
    prompt: 'أرني سورة الفاتحة مع الترجمة',
  },
  {
    icon: <Search size={16} />,
    label: 'حكم الوضوء عند المالكية',
    prompt: 'ما هو حكم الوضوء في المذهب المالكي؟',
  },
  {
    icon: <BookOpen size={16} />,
    label: 'أركان الإسلام',
    prompt: 'ما هي أركان الإسلام الخمسة؟',
  },
  {
    icon: <Sparkles size={16} />,
    label: 'أسماء الله الحسنى',
    prompt: 'أخبرني عن أسماء الله الحسنى',
  },
  {
    icon: <Search size={16} />,
    label: 'أحاديث الصلاة',
    prompt: 'ابحث عن أحاديث عن الصلاة',
  },
  {
    icon: <Heart size={16} />,
    label: 'فضل الوالدين',
    prompt: 'ما هي أحاديث فضل الوالدين؟',
  },
];

interface SuggestionsButtonProps {
  onSelect: (prompt: string) => void;
  disabled?: boolean;
}

export function SuggestionsButton({ onSelect, disabled }: SuggestionsButtonProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [closeTimeout, setCloseTimeout] = useState<number | null>(null);

  const handleMouseEnter = () => {
    if (closeTimeout) {
      clearTimeout(closeTimeout);
      setCloseTimeout(null);
    }
    setIsOpen(true);
  };

  const handleMouseLeave = () => {
    const timeout = window.setTimeout(() => {
      setIsOpen(false);
    }, 300); // 300ms delay before closing
    setCloseTimeout(timeout);
  };

  return (
    <div 
      className="relative"
      onMouseEnter={handleMouseEnter}
      onMouseLeave={handleMouseLeave}
    >
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="px-4 py-2 text-sm font-medium text-gray-700 hover:text-islamic-green transition-colors flex items-center gap-2 border border-gray-300 rounded-lg hover:border-islamic-green"
        disabled={disabled}
      >
        <Lightbulb size={18} />
        <span>Suggestions</span>
      </button>

      {isOpen && (
        <div className="absolute bottom-full left-0 mb-2 w-72 bg-white rounded-lg shadow-2xl border border-gray-200 py-2 z-50 max-h-96 overflow-y-auto"
        >
          <div className="px-4 py-2 text-xs font-semibold text-gray-500 border-b">
            English Suggestions
          </div>
          {suggestions.slice(0, 4).map((suggestion, index) => (
            <button
              key={index}
              onClick={() => {
                onSelect(suggestion.prompt);
                setIsOpen(false);
              }}
              className="w-full px-4 py-2.5 text-left hover:bg-gray-50 transition-colors flex items-center gap-3 text-sm"
            >
              <span className="text-gray-600">{suggestion.icon}</span>
              <span className="text-gray-800">{suggestion.label}</span>
            </button>
          ))}
          
          <div className="px-4 py-2 text-xs font-semibold text-gray-500 border-t border-b mt-1 text-right arabic-text">
            اقتراحات عربية
          </div>
          {suggestions.slice(4).map((suggestion, index) => (
            <button
              key={index + 4}
              onClick={() => {
                onSelect(suggestion.prompt);
                setIsOpen(false);
              }}
              className="w-full px-4 py-2.5 text-right hover:bg-gray-50 transition-colors flex items-center gap-3 text-sm arabic-text"
            >
              <span className="text-gray-800">{suggestion.label}</span>
              <span className="text-gray-600 mr-auto">{suggestion.icon}</span>
            </button>
          ))}
        </div>
      )}
    </div>
  );
}

