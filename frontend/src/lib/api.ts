export interface AIResponse {
  content: string;
  language: string;
  model: string;
  metadata?: Record<string, unknown>;
}

const API_BASE: string = (import.meta as any).env?.VITE_API_BASE_URL ?? 'http://localhost:8000';

export const aiApi = {
  ask: async (question: string, language: string, madhabs?: string[]): Promise<AIResponse> => {
    const response = await fetch(`${API_BASE}/api/v1/ai/ask`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question, language, madhabs }),
    });

    if (!response.ok) {
      const detail = await response.text().catch(() => '');
      throw new Error(`AI ask failed: ${response.status} ${detail}`);
    }

    const data = (await response.json()) as AIResponse;
    return data;
  },
};


