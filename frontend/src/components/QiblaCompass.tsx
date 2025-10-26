import { useEffect, useState } from 'react';
import { Compass, MapPin } from 'lucide-react';
import { prayerTimesApi } from '../lib/api';

export function QiblaCompass() {
  const [qiblaDirection, setQiblaDirection] = useState<number | null>(null);
  const [deviceHeading, setDeviceHeading] = useState<number>(0);
  const [location, setLocation] = useState<string>('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string>('');

  useEffect(() => {
    // Get user location and calculate Qibla
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        async (position) => {
          try {
            const response = await prayerTimesApi.getQiblaDirection(
              position.coords.latitude,
              position.coords.longitude
            );
            
            setQiblaDirection(response.qibla.direction);
            setLocation('Your Location');
            setLoading(false);
          } catch (err) {
            setError('Failed to get Qibla direction');
            setLoading(false);
          }
        },
        () => {
          setError('Location permission denied');
          setLoading(false);
        }
      );
    }

    // Listen to device orientation
    if ('DeviceOrientationEvent' in window) {
      const handleOrientation = (event: DeviceOrientationEvent) => {
        const heading = event.alpha || 0;
        setDeviceHeading(heading);
      };

      window.addEventListener('deviceorientation', handleOrientation);
      return () => window.removeEventListener('deviceorientation', handleOrientation);
    }
  }, []);

  if (loading) {
    return (
      <div className="glass-morphism rounded-xl p-6 text-center">
        <div className="animate-pulse">Loading Qibla direction...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="glass-morphism rounded-xl p-6 text-center">
        <p className="text-red-600">{error}</p>
      </div>
    );
  }

  const adjustedAngle = qiblaDirection !== null ? qiblaDirection - deviceHeading : 0;

  return (
    <div className="glass-morphism rounded-xl p-6 shadow-lg">
      <div className="text-center mb-4">
        <h3 className="text-lg font-semibold text-islamic-green flex items-center justify-center gap-2">
          <MapPin size={20} />
          Qibla Direction
        </h3>
        <p className="text-xs text-gray-600 mt-1">{location}</p>
      </div>

      <div className="relative w-48 h-48 mx-auto">
        {/* Compass background */}
        <div className="absolute inset-0 border-4 border-gray-200 rounded-full" />
        
        {/* Cardinal directions */}
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="absolute top-2 text-sm font-semibold text-gray-700">N</div>
          <div className="absolute right-2 text-sm font-semibold text-gray-700">E</div>
          <div className="absolute bottom-2 text-sm font-semibold text-gray-700">S</div>
          <div className="absolute left-2 text-sm font-semibold text-gray-700">W</div>
        </div>

        {/* Qibla arrow */}
        <div
          className="absolute inset-0 flex items-center justify-center transition-transform duration-300"
          style={{ transform: `rotate(${adjustedAngle}deg)` }}
        >
          <div className="flex flex-col items-center">
            <Compass size={64} className="text-islamic-green" />
            <div className="mt-2 text-xs font-semibold">Qibla</div>
          </div>
        </div>
      </div>

      <div className="text-center mt-4">
        <p className="text-2xl font-bold text-islamic-green">
          {qiblaDirection?.toFixed(1)}°
        </p>
        <p className="text-sm text-gray-600">from North</p>
      </div>

      <p className="text-xs text-center text-gray-500 mt-4">
        Point your device to match the compass
      </p>
    </div>
  );
}

