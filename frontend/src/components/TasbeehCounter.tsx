import { useState, useEffect } from 'react';
import { RotateCcw, Save } from 'lucide-react';

const DHIKR_PHRASES = [
  { arabic: 'سبحان الله', transliteration: 'SubhanAllah', translation: 'Glory be to Allah' },
  { arabic: 'الحمد لله', transliteration: 'Alhamdulillah', translation: 'All praise to Allah' },
  { arabic: 'الله أكبر', transliteration: 'Allahu Akbar', translation: 'Allah is the Greatest' },
  { arabic: 'لا إله إلا الله', transliteration: 'La ilaha illallah', translation: 'No god but Allah' },
  { arabic: 'أستغفر الله', transliteration: 'Astaghfirullah', translation: 'I seek forgiveness from Allah' },
  { arabic: 'لا حول ولا قوة إلا بالله', transliteration: 'La hawla wala quwwata illa billah', translation: 'No power except with Allah' },
];

const TARGET_COUNTS = [33, 99, 100, 500, 1000];

export function TasbeehCounter() {
  const [count, setCount] = useState(0);
  const [target, setTarget] = useState(33);
  const [phraseIndex, setPhraseIndex] = useState(0);
  const [history, setHistory] = useState<Array<{ phrase: string; count: number; date: Date }>>([]);

  const currentPhrase = DHIKR_PHRASES[phraseIndex];

  // Load from localStorage
  useEffect(() => {
    const saved = localStorage.getItem('tasbeeh_count');
    if (saved) setCount(parseInt(saved));
    
    const savedHistory = localStorage.getItem('tasbeeh_history');
    if (savedHistory) setHistory(JSON.parse(savedHistory));
  }, []);

  // Save to localStorage
  useEffect(() => {
    localStorage.setItem('tasbeeh_count', count.toString());
  }, [count]);

  const increment = () => {
    const newCount = count + 1;
    setCount(newCount);
    
    // Haptic feedback
    if (navigator.vibrate) {
      navigator.vibrate(10);
    }
    
    // Completion
    if (newCount === target) {
      if (navigator.vibrate) {
        navigator.vibrate([100, 50, 100]);
      }
      // Auto-save to history
      saveToHistory();
    }
  };

  const reset = () => {
    if (count > 0 && confirm('Reset counter? Current progress will be lost unless saved.')) {
      setCount(0);
    }
  };

  const saveToHistory = () => {
    const entry = {
      phrase: currentPhrase.arabic,
      count: count,
      date: new Date(),
    };
    
    const newHistory = [entry, ...history.slice(0, 49)]; // Keep last 50
    setHistory(newHistory);
    localStorage.setItem('tasbeeh_history', JSON.stringify(newHistory));
    
    alert(`Saved: ${count} x ${currentPhrase.arabic}`);
  };

  return (
    <div className="glass-morphism rounded-xl p-6 shadow-lg max-w-md mx-auto">
      <h3 className="text-lg font-semibold text-center text-islamic-green mb-4">
        Tasbeeh Counter
      </h3>

      {/* Phrase Selector */}
      <div className="mb-4">
        <select
          value={phraseIndex}
          onChange={(e) => setPhraseIndex(parseInt(e.target.value))}
          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:border-islamic-green outline-none text-center"
        >
          {DHIKR_PHRASES.map((phrase, idx) => (
            <option key={idx} value={idx}>
              {phrase.arabic} - {phrase.transliteration}
            </option>
          ))}
        </select>
        <p className="text-xs text-gray-600 text-center mt-1">{currentPhrase.translation}</p>
      </div>

      {/* Counter Display */}
      <div className="text-center mb-6">
        <div className="text-7xl font-bold text-islamic-green mb-2">
          {count}
        </div>
        <div className="text-2xl text-gray-600">/ {target}</div>
        
        {/* Progress bar */}
        <div className="w-full bg-gray-200 rounded-full h-2 mt-4">
          <div
            className="bg-gradient-to-r from-islamic-green to-islamic-teal h-2 rounded-full transition-all duration-300"
            style={{ width: `${Math.min((count / target) * 100, 100)}%` }}
          />
        </div>
      </div>

      {/* Main Counter Button */}
      <button
        onClick={increment}
        className="w-full h-32 gradient-islamic text-white rounded-xl hover:shadow-lg transition-all active:scale-95 mb-4"
      >
        <p className="text-3xl arabic-text font-bold">{currentPhrase.arabic}</p>
        <p className="text-sm opacity-90 mt-2">Tap to count</p>
      </button>

      {/* Target Selector */}
      <div className="flex gap-2 mb-4">
        {TARGET_COUNTS.map((t) => (
          <button
            key={t}
            onClick={() => setTarget(t)}
            className={`flex-1 py-2 rounded-lg text-sm font-semibold transition-colors ${
              target === t
                ? 'bg-islamic-green text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            {t}
          </button>
        ))}
      </div>

      {/* Actions */}
      <div className="flex gap-2">
        <button
          onClick={reset}
          className="flex-1 flex items-center justify-center gap-2 px-4 py-2 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors"
        >
          <RotateCcw size={16} />
          <span className="text-sm">Reset</span>
        </button>
        
        <button
          onClick={saveToHistory}
          disabled={count === 0}
          className="flex-1 flex items-center justify-center gap-2 px-4 py-2 bg-islamic-teal text-white hover:bg-islamic-teal/90 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <Save size={16} />
          <span className="text-sm">Save</span>
        </button>
      </div>

      {/* History */}
      {history.length > 0 && (
        <div className="mt-4 pt-4 border-t border-gray-200">
          <p className="text-xs font-semibold text-gray-600 mb-2">Recent History</p>
          <div className="space-y-1 max-h-32 overflow-y-auto">
            {history.slice(0, 5).map((entry, idx) => (
              <div key={idx} className="text-xs text-gray-600 flex justify-between">
                <span className="arabic-text">{entry.phrase}</span>
                <span>{entry.count}x</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

