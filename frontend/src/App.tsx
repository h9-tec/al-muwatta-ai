import { useState, useRef, useEffect } from 'react';
import { Send, Loader2, Sparkles, Moon, Sun, Plus, Bookmark } from 'lucide-react';
import { ChatMessage } from './components/ChatMessage';
import { PrayerTimesWidget } from './components/PrayerTimesWidget';
import { SuggestionsButton } from './components/SuggestionsButton';
import { UploadButton } from './components/UploadButton';
import { SettingsModal } from './components/SettingsModal';
import { QiblaCompass } from './components/QiblaCompass';
import { TasbeehCounter } from './components/TasbeehCounter';
import { HijriDate } from './components/HijriDate';
import { ExportChat } from './components/ExportChat';
import { BookmarksView } from './components/BookmarksView';
import { FontSizeControl } from './components/FontSizeControl';
import { MadhabSelector } from './components/MadhabSelector';
import { aiApi } from './lib/api';
import { detectLanguage, getLanguageInstruction } from './lib/language-detector';
import { cn } from './lib/utils';
import './index.css';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  metadata?: Record<string, unknown>;
}

type StoredMessage = Omit<Message, 'timestamp'> & {
  timestamp?: string | number | Date;
};

const parseStoredMessages = (raw: StoredMessage[] | null, fallback: Message[]): Message[] => {
  if (!raw || !Array.isArray(raw)) return fallback;

  return raw
    .map((item) => {
      const parsedTimestamp = (() => {
        if (!item.timestamp) return new Date();
        if (item.timestamp instanceof Date) return item.timestamp;
        if (typeof item.timestamp === 'number') return new Date(item.timestamp);
        const parsed = new Date(item.timestamp);
        return Number.isNaN(parsed.getTime()) ? new Date() : parsed;
      })();

      const normalizedMetadata =
        item.metadata && typeof item.metadata === 'object'
          ? (item.metadata as Record<string, unknown>)
          : undefined;

      return {
        id: item.id ?? crypto.randomUUID(),
        role: item.role === 'user' ? 'user' : 'assistant',
        content: item.content ?? '',
        timestamp: parsedTimestamp,
        metadata: normalizedMetadata,
      } satisfies Message;
    })
    .filter((message) => Boolean(message.content.trim()));
};

function App() {
  const initialMessage: Message = {
    id: '1',
    role: 'assistant',
    content: "السلام عليكم ورحمة الله وبركاته\n\nمرحباً بك في الموطأ - Al-Muwatta!\nمساعدك الذكي المتخصص في الفقه المالكي 🕌\n\nأستطيع مساعدتك في:\n• الفقه المالكي من مصادر أصيلة (الرسالة، مختصر خليل)\n• آيات القرآن والتفسير\n• البحث في الأحاديث\n• أوقات الصلاة والتقويم الهجري\n• أسئلة فقهية وإسلامية\n\n📚 قاعدة معرفة: 21+ كتاب في الفقه المالكي\n🤖 مدعوم بالذكاء الاصطناعي\n\nكيف يمكنني خدمتك اليوم؟",
    timestamp: new Date(),
  };

  // Load from localStorage on mount
  const [messages, setMessages] = useState<Message[]>(() => {
    try {
      const saved = localStorage.getItem('chat_messages');
      if (!saved) return [initialMessage];

      const parsed = JSON.parse(saved) as StoredMessage[];
      const hydrated = parseStoredMessages(parsed, [initialMessage]);
      return hydrated.length ? hydrated : [initialMessage];
    } catch (error) {
      console.warn('Failed to parse stored messages, resetting.', error);
      localStorage.removeItem('chat_messages');
      return [initialMessage];
    }
  });
  
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  
  // Load dark mode from localStorage
  const [isDark, setIsDark] = useState(() => {
    if (typeof window === 'undefined') return false;
    const saved = window.localStorage.getItem('dark_mode');
    return saved === 'true';
  });
  
  const [showBookmarks, setShowBookmarks] = useState(false);
  const [activeTab, setActiveTab] = useState<'chat' | 'qibla' | 'tasbeeh'>('chat');
  const [selectedMadhabs, setSelectedMadhabs] = useState<string[]>(() => {
    try {
      const saved = localStorage.getItem('selected_madhabs');
      if (!saved) return [];
      const arr = JSON.parse(saved);
      return Array.isArray(arr) ? (arr as string[]) : [];
    } catch {
      return [];
    }
  });
  // Modes
  const [asMode, setAsMode] = useState<boolean>(() => {
    try {
      const saved = localStorage.getItem('as_mode');
      return saved === 'true';
    } catch {
      return false;
    }
  });
  const [quranHealingMode, setQuranHealingMode] = useState<boolean>(() => {
    try {
      const saved = localStorage.getItem('quran_healing_mode');
      return saved === 'true';
    } catch {
      return false;
    }
  });
  
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Save messages to localStorage
  useEffect(() => {
    const serializable = messages.map((message) => ({
      id: message.id,
      role: message.role,
      content: message.content,
      timestamp: message.timestamp.toISOString(),
      metadata: message.metadata ?? undefined,
    } satisfies StoredMessage));

    window.localStorage.setItem('chat_messages', JSON.stringify(serializable));
  }, [messages]);

  // Save dark mode to localStorage
  useEffect(() => {
    window.localStorage.setItem('dark_mode', isDark.toString());
  }, [isDark]);

  // Persist madhab selection
  useEffect(() => {
    try {
      window.localStorage.setItem('selected_madhabs', JSON.stringify(selectedMadhabs ?? []));
    } catch {}
  }, [selectedMadhabs]);

  // Persist modes
  useEffect(() => {
    try {
      window.localStorage.setItem('as_mode', String(asMode));
      window.localStorage.setItem('quran_healing_mode', String(quranHealingMode));
    } catch {}
  }, [asMode, quranHealingMode]);

  const handleSend = async (customPrompt?: string) => {
    const messageText = customPrompt || input;
    if (!messageText.trim() || loading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: messageText,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      // Detect user's language
      const detectedLang = detectLanguage(messageText);
      const languageInstruction = getLanguageInstruction(detectedLang, messageText);
      const enhancedPrompt = languageInstruction + messageText;

      // Single backend request; orchestrator decides multi-madhab based on question
      const response = await aiApi.ask(
        enhancedPrompt,
        detectedLang,
        selectedMadhabs,
        quranHealingMode,
        asMode,
      );

      const assistantMsg: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: response.content,
        timestamp: new Date(),
        metadata: response.metadata ?? {},
      };

      setMessages((prev) => [...prev, assistantMsg]);
    } catch (error) {
      console.error('Failed to get response:', error);
      
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: "I apologize, but I'm having trouble connecting to the server. Please make sure the backend is running and try again.",
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setLoading(false);
      inputRef.current?.focus();
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleSuggestion = (prompt: string) => {
    handleSend(prompt);
  };

  const startNewChat = () => {
    if (!window.confirm('Start a new chat session? Current conversation will be saved.')) return;

    setMessages([initialMessage]);
    window.localStorage.removeItem('chat_messages');
  };

  return (
    <div className={`min-h-screen ${isDark ? 'bg-neutral-900' : ''}`}>
      {/* Header */}
      <header className={`sticky top-0 z-50 shadow-lg ${isDark ? 'bg-gray-800/90 backdrop-blur-lg' : 'glass-morphism'}`}>
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 rounded-full bg-gradient-paradise flex items-center justify-center text-white shadow-prophetic">
                <Sparkles size={24} />
              </div>
              <div>
                <h1 className={`text-2xl font-bold ${isDark ? 'text-white' : 'text-gradient'}`}>Al-Muwatta</h1>
                <p className={`text-sm arabic-text font-bold ${isDark ? 'text-gray-300' : 'text-gray-600'}`}>الموطأ</p>
              </div>
            </div>
            
            <div className="flex items-center gap-2">
              <button
                onClick={startNewChat}
                className={`px-3 py-2 rounded-lg transition-colors flex items-center gap-2 text-sm font-medium ${
                  isDark ? 'hover:bg-gray-700 text-gray-300' : 'hover:bg-gray-100 text-gray-700'
                }`}
                title="New Chat"
              >
                <Plus size={18} />
                <span className="hidden sm:inline">New Chat</span>
              </button>
              
              <button
                onClick={() => setShowBookmarks(true)}
                className={`px-3 py-2 rounded-lg transition-colors flex items-center gap-2 text-sm font-medium ${
                  isDark ? 'hover:bg-gray-700 text-gray-300' : 'hover:bg-gray-100 text-gray-700'
                }`}
                title="Bookmarks"
              >
                <Bookmark size={18} />
                <span className="hidden sm:inline">Saved</span>
              </button>
              
              <ExportChat messages={messages} />
              <SettingsModal />
              
              <button
                onClick={() => setIsDark(!isDark)}
                className={`p-2 rounded-full transition-colors ${isDark ? 'hover:bg-gray-700 text-yellow-400' : 'hover:bg-gray-100 text-gray-700'}`}
                aria-label="Toggle theme"
              >
                {isDark ? <Sun size={20} /> : <Moon size={20} />}
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-full mx-auto px-2 py-2">
        <div className="flex gap-4">
          {/* Chat Area - Full Width */}
          <div className="flex-1 space-y-4">
            {/* Messages */}
            <div className={`rounded-2xl shadow-xl overflow-hidden ${isDark ? 'bg-gray-800/90 backdrop-blur-lg border border-gray-700' : 'glass-morphism'}`}>
              <div
                id="chat-container"
                className={`h-[calc(100vh-200px)] overflow-y-auto p-6 space-y-4 ${isDark ? 'bg-gray-900' : 'bg-white/60 pattern-islamic'}`}
              >
                {messages.length === 1 && (
                  <div className="text-center py-8">
                    <div className={`inline-block p-6 rounded-2xl mb-4 ${isDark ? 'bg-paradise-500/20' : 'bg-gradient-to-br from-islamic-green to-islamic-teal/20'}`}>
                      <Sparkles size={48} className={`mx-auto ${isDark ? 'text-islamic-gold' : 'text-islamic-green'}`} />
                    </div>
                    <h2 className={`text-2xl font-bold mb-2 ${isDark ? 'text-white' : 'text-gradient'}`}>
                      Ask me anything about Islam
                    </h2>
                    <p className={isDark ? 'text-gray-300' : 'text-gray-700'}>
                      Get authentic answers from Quran, Hadith, and Islamic scholarship
                    </p>
                  </div>
                )}

                {messages.map((message, index) => (
                  <ChatMessage
                    key={message.id}
                    id={message.id}
                    role={message.role}
                    content={message.content}
                    timestamp={message.timestamp}
                    question={index > 0 ? messages[index - 1]?.content : undefined}
                    metadata={message.metadata}
                  />
                ))}

                {loading && (
                  <div className="flex items-center gap-3 p-4">
                    <div className="w-10 h-10 rounded-full bg-white border-2 border-islamic-gold flex items-center justify-center">
                      <Loader2 size={20} className="animate-spin text-islamic-green" />
                    </div>
                    <div className="glass-morphism rounded-2xl rounded-tl-none px-4 py-3">
                      <div className="flex gap-1">
                        <div className="w-2 h-2 bg-islamic-green rounded-full animate-bounce"></div>
                        <div className="w-2 h-2 bg-islamic-green rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                        <div className="w-2 h-2 bg-islamic-green rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                      </div>
                    </div>
                  </div>
                )}

                <div ref={messagesEndRef} />
              </div>


              {/* Input Area */}
              <div className={`border-t p-4 ${isDark ? 'border-gray-700 bg-gray-800/90' : 'border-gray-200 bg-white/80'}`}>
                <div className="flex gap-3">
                  <SuggestionsButton onSelect={handleSuggestion} disabled={loading} />
                  <UploadButton
                    onUploadComplete={(message) => {
                      const uploadMessage: Message = {
                        id: Date.now().toString(),
                        role: 'assistant',
                        content: message,
                        timestamp: new Date(),
                      };
                      setMessages((prev) => [...prev, uploadMessage]);
                    }}
                  />
                  <input
                    ref={inputRef}
                    type="text"
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    onKeyPress={handleKeyPress}
                    placeholder="Ask about Quran, Hadith, or Islamic guidance..."
                    className={`flex-1 px-4 py-3 rounded-xl border outline-none transition-all ${
                      isDark 
                        ? 'bg-gray-700 border-gray-600 text-white placeholder-gray-400 focus:border-islamic-gold focus:ring-2 focus:ring-islamic-gold/20' 
                        : 'bg-white border-gray-300 text-gray-900 focus:border-islamic-green focus:ring-2 focus:ring-islamic-green/20'
                    }`}
                    disabled={loading}
                  />
                  <button
                    onClick={() => handleSend()}
                    disabled={!input.trim() || loading}
                    className="px-6 py-3 gradient-islamic text-white rounded-xl hover:shadow-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
                  >
                    {loading ? (
                      <Loader2 size={20} className="animate-spin" />
                    ) : (
                      <>
                        <Send size={20} />
                        <span className="hidden sm:inline">Send</span>
                      </>
                    )}
                  </button>
                </div>
                <p className={`text-sm mt-2 arabic-center font-semibold ${isDark ? 'text-gray-300' : 'text-gray-700'}`}>
                  لا إمام سوى مالك
                </p>
              </div>
            </div>
          </div>

          {/* Sidebar - Collapsible */}
          <div className={cn(
            "transition-all duration-300 space-y-4",
            "w-80 flex-shrink-0 hidden xl:block"
          )}>
            {/* Tab selector */}
            <div className="flex gap-2 mb-4">
              <button
                onClick={() => setActiveTab('chat')}
                className={`flex-1 py-2 text-sm font-medium rounded-lg transition-colors ${
                  activeTab === 'chat'
                    ? 'bg-islamic-green text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                Chat
              </button>
              <button
                onClick={() => setActiveTab('qibla')}
                className={`flex-1 py-2 text-sm font-medium rounded-lg transition-colors ${
                  activeTab === 'qibla'
                    ? 'bg-islamic-green text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                Qibla
              </button>
              <button
                onClick={() => setActiveTab('tasbeeh')}
                className={`flex-1 py-2 text-sm font-medium rounded-lg transition-colors ${
                  activeTab === 'tasbeeh'
                    ? 'bg-islamic-green text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                Tasbeeh
              </button>
            </div>

            {activeTab === 'chat' && (
              <>
                <PrayerTimesWidget />
                <HijriDate />
                <FontSizeControl />
                <MadhabSelector
                  value={selectedMadhabs}
                  onChange={setSelectedMadhabs}
                />
              {/* Modes */}
              <div className={`p-4 rounded-xl ${isDark ? 'bg-gray-800/70 border border-gray-700' : 'bg-white shadow-sm'}`}>
                <div className="flex items-center justify-between mb-2">
                  <label className={`text-sm font-semibold ${isDark ? 'text-gray-200' : 'text-gray-800'}`}>AS Mode</label>
                  <input
                    type="checkbox"
                    checked={asMode}
                    onChange={(e) => setAsMode(e.target.checked)}
                  />
                </div>
                <p className={`text-xs mb-3 ${isDark ? 'text-gray-400' : 'text-gray-600'}`}>
                  Search each madhab separately and synthesize a comparative answer.
                </p>
                <div className="flex items-center justify-between mb-2">
                  <label className={`text-sm font-semibold ${isDark ? 'text-gray-200' : 'text-gray-800'}`}>Quran Healing</label>
                  <input
                    type="checkbox"
                    checked={quranHealingMode}
                    onChange={(e) => setQuranHealingMode(e.target.checked)}
                  />
                </div>
                <p className={`text-xs ${isDark ? 'text-gray-400' : 'text-gray-600'}`}>
                  Provide comforting Quran/Hadith excerpts from cache, unmodified.
                </p>
              </div>
              </>
            )}

            {activeTab === 'qibla' && <QiblaCompass />}
            
            {activeTab === 'tasbeeh' && <TasbeehCounter />}
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="mt-2 py-3 text-center text-xs text-gray-600">
        <p>Built with love for the Muslim Ummah • الحمد لله رب العالمين</p>
      </footer>

      {/* Bookmarks Modal */}
      <BookmarksView isOpen={showBookmarks} onClose={() => setShowBookmarks(false)} />
    </div>
  );
}

export default App;
