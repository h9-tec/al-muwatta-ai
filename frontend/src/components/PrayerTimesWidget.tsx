import { useEffect, useState } from 'react';
import { Clock, MapPin, Compass } from 'lucide-react';
import { prayerTimesApi } from '../lib/api';
import { formatTime } from '../lib/utils';

interface PrayerTimes {
  Fajr: string;
  Dhuhr: string;
  Asr: string;
  Maghrib: string;
  Isha: string;
}

export function PrayerTimesWidget() {
  const [prayerTimes, setPrayerTimes] = useState<PrayerTimes | null>(null);
  const [location, setLocation] = useState<string>('Loading...');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Try to get user's location
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        async (position) => {
          try {
            const response = await prayerTimesApi.getTimings(
              position.coords.latitude,
              position.coords.longitude
            );
            setPrayerTimes(response.timings.timings);
            
            // Try to get city name from response
            const meta = response.timings?.meta;
            if (meta) {
              const city = meta.timezone || 'Your Location';
              setLocation(city.split('/').pop() || 'Your Location');
            } else {
              setLocation('Your Location');
            }
          } catch (error) {
            console.error('Failed to fetch prayer times:', error);
            // Fallback to Makkah
            await loadDefaultPrayerTimes();
          } finally {
            setLoading(false);
          }
        },
        async () => {
          // If user denies location, use Makkah as default
          await loadDefaultPrayerTimes();
          setLoading(false);
        }
      );
    } else {
      loadDefaultPrayerTimes();
      setLoading(false);
    }
  }, []);

  const loadDefaultPrayerTimes = async () => {
    try {
      // Makkah coordinates
      const response = await prayerTimesApi.getTimings(21.3891, 39.8579);
      setPrayerTimes(response.timings.timings);
      setLocation('Makkah, Saudi Arabia');
    } catch (error) {
      console.error('Failed to load default prayer times:', error);
    }
  };

  if (loading) {
    return (
      <div className="glass-morphism rounded-xl p-6 shadow-lg">
        <div className="animate-pulse space-y-3">
          <div className="h-4 bg-gray-200 rounded w-3/4"></div>
          <div className="h-4 bg-gray-200 rounded w-1/2"></div>
        </div>
      </div>
    );
  }

  if (!prayerTimes) {
    return null;
  }

  const prayers = [
    { name: 'Fajr', time: prayerTimes.Fajr, icon: '🌅' },
    { name: 'Dhuhr', time: prayerTimes.Dhuhr, icon: '☀️' },
    { name: 'Asr', time: prayerTimes.Asr, icon: '🌤️' },
    { name: 'Maghrib', time: prayerTimes.Maghrib, icon: '🌆' },
    { name: 'Isha', time: prayerTimes.Isha, icon: '🌙' },
  ];

  return (
    <div className="glass-morphism rounded-xl p-6 shadow-lg animate-fade-in">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gradient flex items-center gap-2">
          <Clock size={20} className="text-islamic-green" />
          Prayer Times
        </h3>
        <div className="flex items-center gap-1 text-xs text-gray-600">
          <MapPin size={14} />
          <span>{location}</span>
        </div>
      </div>

      <div className="space-y-2">
        {prayers.map((prayer) => (
          <div
            key={prayer.name}
            className="flex items-center justify-between p-3 rounded-lg hover:bg-white/50 transition-colors"
          >
            <div className="flex items-center gap-3">
              <span className="text-2xl">{prayer.icon}</span>
              <span className="font-medium text-gray-700">{prayer.name}</span>
            </div>
            <span className="font-semibold text-islamic-green">
              {formatTime(prayer.time)}
            </span>
          </div>
        ))}
      </div>

      <div className="mt-4 pt-4 border-t border-gray-200">
        <button className="w-full flex items-center justify-center gap-2 text-sm text-islamic-teal hover:text-islamic-green transition-colors">
          <Compass size={16} />
          <span>Find Qibla Direction</span>
        </button>
      </div>
    </div>
  );
}

