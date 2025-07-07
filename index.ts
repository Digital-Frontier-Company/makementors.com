
/**
 * Centralized configuration for the application
 * This file contains all configuration values that can be shared across
 * both client-side code and edge functions
 */

// Supabase Configuration - using environment variables only
export const SUPABASE_CONFIG = {
  url: import.meta.env.VITE_SUPABASE_URL!,
  anonKey: import.meta.env.VITE_SUPABASE_ANON_KEY!
};

// Other API configurations can be added here
export const API_CONFIG = {
  // Add other API configurations here as needed
};
