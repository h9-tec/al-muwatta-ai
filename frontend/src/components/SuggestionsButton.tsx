import { useState } from 'react';
import { Lightbulb, BookOpen, Sparkles, Search, Heart } from 'lucide-react';

interface Suggestion {
  icon: React.ReactNode;
  label: string;
  prompt: string;
}

const suggestions: Suggestion[] = [
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
    label: 'Search Hadith',
    prompt: 'Search for Hadiths about prayer',
  },
  {
    icon: <Heart size={16} />,
    label: '99 Names of Allah',
    prompt: 'Tell me about the 99 names of Allah',
  },
  {
    icon: <BookOpen size={16} />,
    label: 'Maliki Wudu Ruling',
    prompt: 'What is the Maliki position on wudu?',
  },
  {
    icon: <Search size={16} />,
    label: 'Prayer Times Explanation',
    prompt: 'Explain the five daily prayers in Islam',
  },
];

interface SuggestionsButtonProps {
  onSelect: (prompt: string) => void;
  disabled?: boolean;
}

export function SuggestionsButton({ onSelect, disabled }: SuggestionsButtonProps) {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <div className="relative">
      <button
        onMouseEnter={() => setIsOpen(true)}
        onMouseLeave={() => setIsOpen(false)}
        className="px-4 py-2 text-sm font-medium text-gray-700 hover:text-islamic-green transition-colors flex items-center gap-2 border border-gray-300 rounded-lg hover:border-islamic-green"
        disabled={disabled}
      >
        <Lightbulb size={18} />
        <span>Suggestions</span>
      </button>

      {isOpen && (
        <div
          onMouseEnter={() => setIsOpen(true)}
          onMouseLeave={() => setIsOpen(false)}
          className="absolute bottom-full left-0 mb-2 w-64 bg-white rounded-lg shadow-2xl border border-gray-200 py-2 z-50"
        >
          {suggestions.map((suggestion, index) => (
            <button
              key={index}
              onClick={() => {
                onSelect(suggestion.prompt);
                setIsOpen(false);
              }}
              className="w-full px-4 py-2 text-left hover:bg-gray-50 transition-colors flex items-center gap-3 text-sm"
            >
              <span className="text-gray-600">{suggestion.icon}</span>
              <span className="text-gray-800">{suggestion.label}</span>
            </button>
          ))}
        </div>
      )}
    </div>
  );
}

