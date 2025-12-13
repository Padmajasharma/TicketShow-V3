// Authentication utilities

/**
 * Decode a JWT token without verification (client-side only)
 * @param {string} token - JWT token
 * @returns {object|null} - Decoded payload or null if invalid
 */
export function decodeToken(token) {
  try {
    if (!token) return null;
    const parts = token.split('.');
    if (parts.length !== 3) return null;
    
    const payload = parts[1];
    const decoded = atob(payload.replace(/-/g, '+').replace(/_/g, '/'));
    return JSON.parse(decoded);
  } catch (e) {
    console.error('Error decoding token:', e);
    return null;
  }
}

/**
 * Check if a token is expired
 * @param {string} token - JWT token
 * @returns {boolean} - true if expired or invalid
 */
export function isTokenExpired(token) {
  const decoded = decodeToken(token);
  if (!decoded || !decoded.exp) return true;
  
  // exp is in seconds, Date.now() is in milliseconds
  const expirationTime = decoded.exp * 1000;
  return Date.now() >= expirationTime;
}

/**
 * Get the time until token expires (in milliseconds)
 * @param {string} token - JWT token
 * @returns {number} - milliseconds until expiration, or 0 if expired/invalid
 */
export function getTimeUntilExpiry(token) {
  const decoded = decodeToken(token);
  if (!decoded || !decoded.exp) return 0;
  
  const expirationTime = decoded.exp * 1000;
  const timeLeft = expirationTime - Date.now();
  return timeLeft > 0 ? timeLeft : 0;
}

/**
 * Clear all auth data from localStorage
 */
export function clearAuthData() {
  localStorage.removeItem('access_token');
  localStorage.removeItem('user_id');
  localStorage.removeItem('role');
}

/**
 * Check if user is authenticated with a valid token
 * @returns {boolean}
 */
export function isAuthenticated() {
  const token = localStorage.getItem('access_token');
  return token && !isTokenExpired(token);
}
