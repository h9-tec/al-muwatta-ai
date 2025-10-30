import { useEffect, useMemo, useState } from 'react';
import { Compass, MapPin, RefreshCw } from 'lucide-react';
import { prayerTimesApi } from '../lib/api';

interface QiblaResponse {
  direction: number;
  latitude?: number;
  longitude?: number;
  location?: string;
}

type GeolocationStatus = 'idle' | 'requesting' | 'granted' | 'denied' | 'unsupported' | 'error';

const useDeviceHeading = (): number => {
  const [heading, setHeading] = useState(0);

  useEffect(() => {
    const DeviceOrientationEventAny = DeviceOrientationEvent as typeof DeviceOrientationEvent & {
      requestPermission?: () => Promise<PermissionState>;
    };

    const supportsPermissionRequest = typeof DeviceOrientationEventAny?.requestPermission === 'function';

    const handleOrientation = (event: DeviceOrientationEvent) => {
      const webkitHeading = (event as DeviceOrientationEvent & { webkitCompassHeading?: number }).webkitCompassHeading;
      if (typeof webkitHeading === 'number') {
        setHeading(webkitHeading);
        return;
      }

      if (typeof event.absolute === 'boolean' && event.absolute && typeof event.alpha === 'number') {
        setHeading(event.alpha);
      } else if (typeof event.alpha === 'number') {
        setHeading(360 - event.alpha);
      }
    };

    const startListener = () => {
      window.addEventListener('deviceorientation', handleOrientation, true);
    };

    if (supportsPermissionRequest) {
      DeviceOrientationEventAny.requestPermission?.()
        .then((response) => {
          if (response === 'granted') startListener();
        })
        .catch(() => startListener());
    } else if ('DeviceOrientationEvent' in window) {
      startListener();
    }

    return () => {
      window.removeEventListener('deviceorientation', handleOrientation, true);
    };
  }, []);

  return heading;
};

export function QiblaCompass() {
  const [qiblaDirection, setQiblaDirection] = useState<number | null>(null);
  const [location, setLocation] = useState<string>('');
  const [status, setStatus] = useState<GeolocationStatus>('idle');
  const [error, setError] = useState<string>('');
  const deviceHeading = useDeviceHeading();

  const fetchQibla = (lat: number, lng: number, label?: string) => {
    setStatus('requesting');
    prayerTimesApi
      .getQiblaDirection(lat, lng)
      .then((response: { direction?: number; qibla?: QiblaResponse; source?: string }) => {
        const direction = response.qibla?.direction ?? response.direction;
        if (typeof direction === 'number') {
          setQiblaDirection(direction);
          setLocation(
            label ||
              response.qibla?.location ||
              `(${(response.qibla?.latitude ?? lat).toFixed(2)}, ${(response.qibla?.longitude ?? lng).toFixed(2)})`,
          );
          setStatus('granted');
          setError('');
        } else {
          throw new Error('Invalid qibla response');
        }
      })
      .catch((err: unknown) => {
        console.error('Qibla API error', err);
        setError('Failed to get Qibla direction');
        setStatus('error');
      });
  };

  useEffect(() => {
    if (!('geolocation' in navigator)) {
      setStatus('unsupported');
      setError('Geolocation is not supported in this browser');
      return;
    }

    setStatus('requesting');
    navigator.geolocation.getCurrentPosition(
      (position) => {
        fetchQibla(position.coords.latitude, position.coords.longitude, 'Your Location');
      },
      (geoError) => {
        if (geoError.code === geoError.PERMISSION_DENIED) {
          setStatus('denied');
          setError('Location permission denied. Use manual entry.');
        } else {
          setStatus('error');
          setError('Unable to access location. Please try manual lookup.');
        }
      },
      {
        enableHighAccuracy: true,
        timeout: 10000,
        maximumAge: 60000,
      },
    );
  }, []);

  const adjustedAngle = useMemo(() => {
    if (qiblaDirection === null) return 0;
    const normalizedHeading = ((deviceHeading % 360) + 360) % 360;
    const normalizedQibla = ((qiblaDirection % 360) + 360) % 360;
    return normalizedQibla - normalizedHeading;
  }, [qiblaDirection, deviceHeading]);

  const handleManualSearch = async () => {
    const city = window.prompt('Enter your city name for Qibla direction');
    const country = window.prompt('Enter your country name');
    if (!city || !country) return;

    setStatus('requesting');
    try {
      const timings = await prayerTimesApi.getTimingsByCity(city, country);
      const meta = timings?.timings?.meta || timings?.data?.meta || timings?.meta;
      const latitude = meta?.latitude;
      const longitude = meta?.longitude;

      if (typeof latitude === 'number' && typeof longitude === 'number') {
        fetchQibla(latitude, longitude, `${city}, ${country}`);
      } else {
        throw new Error('Location not found');
      }
    } catch (err) {
      console.error('Manual Qibla lookup failed', err);
      setStatus('error');
      setError('Could not determine Qibla for that city');
    }
  };

  if (status === 'requesting' || status === 'idle') {
    return (
      <div className="glass-morphism rounded-xl p-6 text-center">
        <div className="animate-pulse">Determining Qibla direction...</div>
      </div>
    );
  }

  if (status === 'unsupported' || status === 'denied' || status === 'error') {
    return (
      <div className="glass-morphism rounded-xl p-6 text-center space-y-3">
        <p className="text-red-600 text-sm">{error}</p>
        <button
          onClick={handleManualSearch}
          className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-islamic-green text-white text-sm hover:bg-islamic-green/90 transition"
        >
          <RefreshCw size={16} />
          Enter location manually
        </button>
      </div>
    );
  }

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
        <div className="absolute inset-0 border-4 border-gray-200 rounded-full" />

        <div className="absolute inset-0 flex items-center justify-center">
          <div className="absolute top-2 text-sm font-semibold text-gray-700">N</div>
          <div className="absolute right-2 text-sm font-semibold text-gray-700">E</div>
          <div className="absolute bottom-2 text-sm font-semibold text-gray-700">S</div>
          <div className="absolute left-2 text-sm font-semibold text-gray-700">W</div>
        </div>

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
        <p className="text-sm text-gray-600">from True North</p>
      </div>

      <p className="text-xs text-center text-gray-500 mt-4">
        Align your device with the arrow to face the Qibla
      </p>

      <div className="mt-4 text-center">
        <button
          onClick={handleManualSearch}
          className="text-xs text-islamic-green hover:text-islamic-green/80 underline"
        >
          Update location manually
        </button>
      </div>
    </div>
  );
}

