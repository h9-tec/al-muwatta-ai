export interface AIResponse {
  content: string;
  language: string;
  model: string;
  metadata?: Record<string, unknown>;
}

const API_BASE: string = (import.meta as any).env?.VITE_API_BASE_URL ?? 'http://localhost:8000';

export const aiApi = {
  ask: async (
    question: string,
    language: string,
    madhabs?: string[],
    quranHealingMode?: boolean,
    asMode?: boolean,
    webSearchEnabled?: boolean,
    webSearchAttempts?: number,
  ): Promise<AIResponse> => {
    // Get provider and model from localStorage
    // Default to Ollama (local, no API key required)
    const provider = localStorage.getItem('llm_provider') || 'ollama';
    const model = localStorage.getItem('llm_model') || undefined;
    const apiKey = localStorage.getItem(`${provider}_api_key`) || undefined;

    const response = await fetch(`${API_BASE}/api/v1/ai/ask`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        question,
        language,
        madhabs,
        provider,
        model,
        api_key: apiKey,
        quran_healing_mode: Boolean(quranHealingMode),
        as_mode: Boolean(asMode),
        web_search_enabled: Boolean(webSearchEnabled),
        web_search_attempts: webSearchAttempts ?? 2,
      }),
    });

    if (!response.ok) {
      const detail = await response.text().catch(() => '');
      throw new Error(`AI ask failed: ${response.status} ${detail}`);
    }

    const data = (await response.json()) as AIResponse;
    return data;
  },
};

export const prayerTimesApi = {
  getTimings: async (latitude: number, longitude: number, method?: number, date?: string) => {
    const params = new URLSearchParams({
      latitude: latitude.toString(),
      longitude: longitude.toString(),
      ...(method && { method: method.toString() }),
      ...(date && { date }),
    });

    const response = await fetch(`${API_BASE}/api/v1/prayer-times/timings?${params}`);
    if (!response.ok) {
      throw new Error(`Prayer times request failed: ${response.status}`);
    }
    return response.json();
  },

  getQiblaDirection: async (latitude: number, longitude: number) => {
    const params = new URLSearchParams({
      latitude: latitude.toString(),
      longitude: longitude.toString(),
    });

    const response = await fetch(`${API_BASE}/api/v1/prayer-times/qibla?${params}`);
    if (!response.ok) {
      throw new Error(`Qibla request failed: ${response.status}`);
    }
    return response.json();
  },

  getTimingsByCity: async (city: string, country: string, method?: number, date?: string) => {
    const params = new URLSearchParams({
      city,
      country,
      ...(method && { method: method.toString() }),
      ...(date && { date }),
    });

    const response = await fetch(`${API_BASE}/api/v1/prayer-times/timings/city?${params}`);
    if (!response.ok) {
      throw new Error(`Prayer times by city request failed: ${response.status}`);
    }
    return response.json();
  },
};

export const api = {
  get: async (url: string) => {
    const response = await fetch(`${API_BASE}${url}`);
    if (!response.ok) {
      throw new Error(`GET ${url} failed: ${response.status}`);
    }
    return response.json();
  },

  post: async (url: string, data?: any) => {
    const response = await fetch(`${API_BASE}${url}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: data ? JSON.stringify(data) : undefined,
    });
    if (!response.ok) {
      throw new Error(`POST ${url} failed: ${response.status}`);
    }
    return response.json();
  },

  getSettings: async () => {
    const response = await fetch(`${API_BASE}/api/v1/settings`);
    if (!response.ok) {
      throw new Error(`Settings request failed: ${response.status}`);
    }
    return response.json();
  },

  updateSettings: async (config: any) => {
    const response = await fetch(`${API_BASE}/api/v1/settings`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(config),
    });
    if (!response.ok) {
      throw new Error(`Settings update failed: ${response.status}`);
    }
    return response.json();
  },
};


