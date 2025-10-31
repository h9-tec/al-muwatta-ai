import { useState, useEffect } from 'react';
import { Settings, X, Check, Loader2 } from 'lucide-react';
import { api } from '../lib/api';
import { MadhabSelector } from './MadhabSelector';

interface Provider {
  name: string;
  requires_api_key: boolean;
}

interface Model {
  id: string;
  name: string;
  provider: string;
  size?: number;
}

export function SettingsModal() {
  const [isOpen, setIsOpen] = useState(false);
  
  // Initialize with providers list
  const [providers, setProviders] = useState<Record<string, Provider>>({
    ollama: { name: 'Ollama (Local)', requires_api_key: false },
    openrouter: { name: 'OpenRouter', requires_api_key: true },
    groq: { name: 'Groq', requires_api_key: true },
    openai: { name: 'OpenAI', requires_api_key: true },
    anthropic: { name: 'Claude (Anthropic)', requires_api_key: true },
    gemini: { name: 'Google Gemini', requires_api_key: true },
  });
  
  const [selectedProvider, setSelectedProvider] = useState('gemini');
  const [apiKey, setApiKey] = useState('');
  const [models, setModels] = useState<Model[]>([]);
  const [selectedModel, setSelectedModel] = useState('');
  const [loading, setLoading] = useState(false);
  const [testing, setTesting] = useState(false);
  const [selectedMadhabs, setSelectedMadhabs] = useState<string[]>([]);

  useEffect(() => {
    if (isOpen) {
      fetchProviders();
      // Load saved settings
      const savedProvider = localStorage.getItem('llm_provider');
      const savedModel = localStorage.getItem('llm_model');
      const savedKey = localStorage.getItem(`${selectedProvider}_api_key`);
      const savedMadhabs = localStorage.getItem('selected_madhabs');
      
      if (savedProvider) setSelectedProvider(savedProvider);
      if (savedModel) setSelectedModel(savedModel);
      if (savedKey) setApiKey(savedKey);
      if (savedMadhabs) {
        try {
          const arr = JSON.parse(savedMadhabs);
          if (Array.isArray(arr)) setSelectedMadhabs(arr);
        } catch {}
      }
    }
  }, [isOpen]);

  // When user switches provider, load any saved API key and clear model selection
  useEffect(() => {
    const key = localStorage.getItem(`${selectedProvider}_api_key`) || '';
    setApiKey(key);
    setModels([]);
    setSelectedModel('');
  }, [selectedProvider]);

  const fetchProviders = async () => {
    try {
      const response = await api.get('/api/v1/settings/providers');
      // Merge with defaults to ensure all providers remain selectable
      setProviders((prev) => ({
        ...prev,
        ...(response?.data?.providers ?? {}),
      }));
    } catch (error) {
      console.error('Failed to fetch providers:', error);
    }
  };

  const fetchModels = async () => {
    setLoading(true);
    try {
      const response = await api.post(
        `/api/v1/settings/providers/${selectedProvider}/models`,
        { api_key: apiKey }
      );
      setModels(response.data.models);
      if (response.data.models.length > 0) {
        setSelectedModel(response.data.models[0].id);
      }
    } catch (error) {
      console.error('Failed to fetch models:', error);
      const message = error instanceof Error ? error.message : 'Unknown error';
      alert(`Failed to fetch models: ${message}`);
    } finally {
      setLoading(false);
    }
  };

  const testConnection = async () => {
    setTesting(true);
    try {
      const response = await api.post(
        '/api/v1/settings/test-connection',
        {
          provider: selectedProvider,
          api_key: apiKey,
          model: selectedModel,
        }
      );
      alert(`✅ ${response.data.message}\n\nTest response: ${response.data.test_response}`);
    } catch (error) {
      alert('❌ Connection failed. Check your settings.');
    } finally {
      setTesting(false);
    }
  };

  const saveSettings = () => {
    // Save to localStorage
    localStorage.setItem('llm_provider', selectedProvider);
    localStorage.setItem('llm_model', selectedModel);
    if (apiKey) {
      localStorage.setItem(`${selectedProvider}_api_key`, apiKey);
    }
    localStorage.setItem('selected_madhabs', JSON.stringify(selectedMadhabs ?? []));
    alert('✅ Settings saved!');
    setIsOpen(false);
  };

  return (
    <>
      <button
        onClick={() => setIsOpen(true)}
        className="p-2 rounded-full hover:bg-gray-100 transition-colors text-gray-700"
        title="LLM Settings"
      >
        <Settings size={20} />
      </button>

      {isOpen && (
        <div 
          className="fixed inset-0 bg-black/50 flex items-center justify-center z-[200]"
          onClick={() => setIsOpen(false)}
        >
          <div 
            className="bg-white rounded-2xl shadow-2xl w-full max-w-2xl max-h-[90vh] overflow-y-auto"
            onClick={(e) => e.stopPropagation()}
          >
            {/* Header */}
            <div className="sticky top-0 bg-gradient-to-r from-islamic-green to-islamic-teal text-white p-6 rounded-t-2xl">
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-2xl font-bold">⚙️ LLM Settings</h2>
                  <p className="text-sm opacity-90">Configure your AI provider</p>
                </div>
                <div className="flex items-center gap-2">
                  <label className="text-xs opacity-90 hidden sm:block">Provider</label>
                  <select
                    value={selectedProvider}
                    onChange={(e) => setSelectedProvider(e.target.value)}
                    className="px-3 py-2 rounded-lg text-gray-900"
                  >
                    {Object.entries(providers).map(([key, provider]) => (
                      <option key={key} value={key}>
                        {provider.name}
                      </option>
                    ))}
                  </select>
                </div>
                <button
                  onClick={() => setIsOpen(false)}
                  className="p-2 hover:bg-white/20 rounded-full transition"
                >
                  <X size={24} />
                </button>
              </div>
            </div>

            {/* Body */}
            <div className="p-6 space-y-6">
              {/* Provider Selection */}
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  Select Provider
                </label>
                <select
                  value={selectedProvider}
                  onChange={(e) => setSelectedProvider(e.target.value)}
                  className="w-full px-4 py-3 border-2 border-gray-300 rounded-xl focus:border-islamic-green outline-none"
                >
                  {Object.entries(providers).map(([key, provider]) => (
                    <option key={key} value={key}>
                      {provider.name}
                    </option>
                  ))}
                </select>
              </div>

              {/* API Key Input (if required) */}
              {providers[selectedProvider]?.requires_api_key && (
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">
                    API Key
                  </label>
                  <input
                    type="password"
                    value={apiKey}
                    onChange={(e) => setApiKey(e.target.value)}
                    placeholder="Enter your API key..."
                    className="w-full px-4 py-3 border-2 border-gray-300 rounded-xl focus:border-islamic-green outline-none"
                  />
                  <p className="text-xs text-gray-500 mt-1">
                    Get API key from {providers[selectedProvider]?.name} website
                  </p>
                </div>
              )}

              {/* Fetch Models Button */}
              <button
                onClick={fetchModels}
                disabled={loading || (providers[selectedProvider]?.requires_api_key && !apiKey)}
                className="w-full py-3 bg-islamic-teal text-white rounded-xl hover:bg-islamic-teal/90 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2 font-semibold"
              >
                {loading ? (
                  <>
                    <Loader2 size={20} className="animate-spin" />
                    Fetching Models...
                  </>
                ) : (
                  <>
                    <Check size={20} />
                    Fetch Available Models
                  </>
                )}
              </button>

              {/* Models List */}
              {models.length > 0 && (
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">
                    Select Model ({models.length} available)
                  </label>
                  <select
                    value={selectedModel}
                    onChange={(e) => setSelectedModel(e.target.value)}
                    className="w-full px-4 py-3 border-2 border-gray-300 rounded-xl focus:border-islamic-green outline-none"
                    size={Math.min(models.length, 5)}
                  >
                    {models.map((model) => (
                      <option key={model.id} value={model.id}>
                        {model.name} {model.size ? `(${(model.size / 1e9).toFixed(1)}GB)` : ''}
                      </option>
                    ))}
                  </select>
                </div>
              )}

              {/* Fiqh Schools (madhab) selection */}
              <MadhabSelector
                value={selectedMadhabs}
                onChange={setSelectedMadhabs}
              />

              {/* Test Connection */}
              {selectedModel && (
                <button
                  onClick={testConnection}
                  disabled={testing}
                  className="w-full py-3 bg-purple-600 text-white rounded-xl hover:bg-purple-700 disabled:opacity-50 flex items-center justify-center gap-2 font-semibold"
                >
                  {testing ? (
                    <>
                      <Loader2 size={20} className="animate-spin" />
                      Testing...
                    </>
                  ) : (
                    '🧪 Test Connection'
                  )}
                </button>
              )}

              {/* Save Button */}
              {selectedModel && (
                <button
                  onClick={saveSettings}
                  className="w-full py-4 gradient-islamic text-white rounded-xl hover:shadow-lg transition-all flex items-center justify-center gap-2 font-bold text-lg"
                >
                  <Check size={24} />
                  Save Settings
                </button>
              )}
            </div>
          </div>
        </div>
      )}
    </>
  );
}

