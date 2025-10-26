import { useState, useEffect } from 'react';
import axios from 'axios';
import { Calendar } from 'lucide-react';

interface HijriDateInfo {
  date: string;
  month: { en: string; ar: string };
  year: string;
  weekday: { en: string; ar: string };
}

export function HijriDate() {
  const [hijriDate, setHijriDate] = useState<HijriDateInfo | null>(null);
  const [gregorianDate, setGregorianDate] = useState<Date>(new Date());

  useEffect(() => {
    fetchCurrentDate();
  }, []);

  const fetchCurrentDate = async () => {
    try {
      const response = await axios.get(
        'http://localhost:8000/api/v1/prayer-times/date/current'
      );
      
      const data = response.data.date;
      setHijriDate(data.hijri);
      setGregorianDate(new Date(data.gregorian.date));
    } catch (error) {
      console.error('Failed to fetch Hijri date:', error);
    }
  };

  if (!hijriDate) {
    return (
      <div className="glass-morphism rounded-xl p-4 shadow-lg animate-pulse">
        <div className="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
        <div className="h-4 bg-gray-200 rounded w-1/2"></div>
      </div>
    );
  }

  return (
    <div className="glass-morphism rounded-xl p-4 shadow-lg">
      <div className="flex items-center gap-2 mb-3">
        <Calendar size={20} className="text-islamic-green" />
        <h4 className="font-semibold text-gray-700">Today</h4>
      </div>

      {/* Hijri Date */}
      <div className="mb-3">
        <p className="text-sm text-gray-600">Hijri Calendar</p>
        <p className="text-lg font-bold text-islamic-green arabic-text text-right">
          {hijriDate.date} {hijriDate.month.ar} {hijriDate.year}
        </p>
        <p className="text-xs text-gray-600 arabic-text text-right">
          {hijriDate.weekday.ar}
        </p>
      </div>

      {/* Gregorian Date */}
      <div className="pt-3 border-t border-gray-200">
        <p className="text-sm text-gray-600">Gregorian Calendar</p>
        <p className="text-base font-semibold text-gray-700">
          {gregorianDate.toLocaleDateString('en-US', {
            weekday: 'long',
            year: 'numeric',
            month: 'long',
            day: 'numeric',
          })}
        </p>
      </div>
    </div>
  );
}

