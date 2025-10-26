/**
 * Qibla direction calculation utilities
 */

const MAKKAH_LAT = 21.4225;
const MAKKAH_LNG = 39.8262;

export function calculateQiblaDirection(userLat: number, userLng: number): number {
  /**
   * Calculate Qibla direction from user's location to Makkah
   * Returns angle in degrees from North (0-360)
   */
  
  // Convert to radians
  const lat1 = (userLat * Math.PI) / 180;
  const lat2 = (MAKKAH_LAT * Math.PI) / 180;
  const lng1 = (userLng * Math.PI) / 180;
  const lng2 = (MAKKAH_LNG * Math.PI) / 180;

  // Calculate bearing
  const y = Math.sin(lng2 - lng1) * Math.cos(lat2);
  const x =
    Math.cos(lat1) * Math.sin(lat2) -
    Math.sin(lat1) * Math.cos(lat2) * Math.cos(lng2 - lng1);
  
  let bearing = Math.atan2(y, x);
  
  // Convert to degrees
  bearing = (bearing * 180) / Math.PI;
  
  // Normalize to 0-360
  bearing = (bearing + 360) % 360;
  
  return bearing;
}

export function getCardinalDirection(degrees: number): string {
  /**
   * Get cardinal direction from degrees
   */
  const directions = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW'];
  const index = Math.round(degrees / 45) % 8;
  return directions[index];
}

export function formatQiblaDirection(degrees: number): string {
  /**
   * Format Qibla direction for display
   */
  const cardinal = getCardinalDirection(degrees);
  return `${degrees.toFixed(1)}° (${cardinal})`;
}

