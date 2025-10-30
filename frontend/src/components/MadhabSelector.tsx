
interface Option {
  key: string;
  label: string;
}

const MADHAB_OPTIONS: Option[] = [
  { key: 'maliki', label: 'Maliki • المالكي' },
  { key: 'hanafi', label: 'Hanafi • الحنفي' },
  { key: 'shafii', label: "Shafi'i • الشافعي" },
  { key: 'hanbali', label: 'Hanbali • الحنبلي' },
];

export interface MadhabSelectorProps {
  value: string[];
  onChange: (next: string[]) => void;
  className?: string;
}

export function MadhabSelector({ value, onChange, className }: MadhabSelectorProps) {
  const selected = new Set((value ?? []).map((v) => v.toLowerCase()));

  const toggle = (key: string) => {
    const next = new Set(selected);
    if (next.has(key)) next.delete(key); else next.add(key);
    onChange(Array.from(next));
  };

  const toggleAll = () => {
    if (selected.size === MADHAB_OPTIONS.length) onChange([]);
    else onChange(MADHAB_OPTIONS.map((o) => o.key));
  };

  return (
    <div className={className}>
      <div className="flex items-center justify-between mb-2">
        <label className="block text-sm font-semibold text-gray-700">Fiqh Schools (المذاهب)</label>
        <button
          type="button"
          onClick={toggleAll}
          className="text-xs text-islamic-green hover:underline"
        >
          {selected.size === MADHAB_OPTIONS.length ? 'Clear' : 'Select all'}
        </button>
      </div>

      <div className="grid grid-cols-2 gap-2">
        {MADHAB_OPTIONS.map((opt) => (
          <label key={opt.key} className="flex items-center gap-2 p-2 rounded-lg border border-gray-200 hover:bg-gray-50">
            <input
              type="checkbox"
              className="w-4 h-4"
              checked={selected.has(opt.key)}
              onChange={() => toggle(opt.key)}
            />
            <span className="text-sm">{opt.label}</span>
          </label>
        ))}
      </div>
      <p className="text-xs text-gray-500 mt-2">If none selected, all schools will be used.</p>
    </div>
  );
}


