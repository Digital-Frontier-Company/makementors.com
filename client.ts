
import { createClient } from '@supabase/supabase-js'
import { SUPABASE_CONFIG } from '@/config'

// Only use the anon key in client-side code
// The service role key should ONLY be used in server-side edge functions
export const supabase = createClient(
  SUPABASE_CONFIG.url,
  SUPABASE_CONFIG.anonKey
)
