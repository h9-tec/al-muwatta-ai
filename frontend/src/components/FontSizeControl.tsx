import { useState, useEffect } from 'react';
import { Type } from 'lucide-react';

type FontSize = 'small' | 'medium' | 'large' | 'xlarge';

const FONT_SIZES = {
  small: { label: 'Small', size: '14px', arabicSize: '15.4px' },
  medium: { label: 'Medium', size: '16px', arabicSize: '17.6px' },
  large: { label: 'Large', size: '18px', arabicSize: '19.8px' },
  xlarge: { label: 'Extra Large', size: '20px', arabicSize: '22px' },
};

export function FontSizeControl() {
  const [fontSize, setFontSize] = useState<FontSize>('medium');

  useEffect(() => {
    const saved = localStorage.getItem('font_size') as FontSize;
    if (saved && saved in FONT_SIZES) {
      setFontSize(saved);
    }
  }, []);

  useEffect(() => {
    // Apply font size to document
    const root = document.documentElement;
    const config = FONT_SIZES[fontSize];
    
    root.style.setProperty('--base-font-size', config.size);
    root.style.setProperty('--arabic-font-size', config.arabicSize);
    
    // Save preference
    localStorage.setItem('font_size', fontSize);
  }, [fontSize]);

  return (
    <div className="glass-morphism rounded-xl p-4 shadow-lg">
      <div className="flex items-center gap-2 mb-3">
        <Type size={20} className="text-islamic-green" />
        <h4 className="font-semibold text-gray-700">Font Size</h4>
      </div>

      <div className="grid grid-cols-2 gap-2">
        {Object.entries(FONT_SIZES).map(([key, config]) => (
          <button
            key={key}
            onClick={() => setFontSize(key as FontSize)}
            className={`py-2 px-3 rounded-lg text-sm font-medium transition-all ${
              fontSize === key
                ? 'bg-islamic-green text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            {config.label}
          </button>
        ))}
      </div>

      <div className="mt-3 pt-3 border-t border-gray-200">
        <p className="text-xs text-gray-600">
          Preview: <span style={{ fontSize: FONT_SIZES[fontSize].size }}>
            The quick brown fox
          </span>
        </p>
        <p className="text-xs text-gray-600 arabic-text mt-1">
          مثال: <span style={{ fontSize: FONT_SIZES[fontSize].arabicSize }}>
            بسم الله الرحمن الرحيم
          </span>
        </p>
      </div>
    </div>
  );
}

