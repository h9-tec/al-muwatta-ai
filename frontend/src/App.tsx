import { useState, useRef, useEffect } from 'react';
import { Send, Loader2, Sparkles, Moon, Sun } from 'lucide-react';
import { ChatMessage } from './components/ChatMessage';
import { PrayerTimesWidget } from './components/PrayerTimesWidget';
import { QuickActions } from './components/QuickActions';
import { UploadButton } from './components/UploadButton';
import { SettingsModal } from './components/SettingsModal';
import { aiApi } from './lib/api';
import { detectLanguage, getLanguageInstruction } from './lib/language-detector';
import { cn } from './lib/utils';
import './index.css';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

function App() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      role: 'assistant',
      content: "السلام عليكم ورحمة الله وبركاته\n\nمرحباً بك في الموطأ - Al-Muwatta!\nمساعدك الذكي المتخصص في الفقه المالكي 🕌\n\nأستطيع مساعدتك في:\n• الفقه المالكي من مصادر أصيلة (الرسالة، مختصر خليل)\n• آيات القرآن والتفسير\n• البحث في الأحاديث\n• أوقات الصلاة والتقويم الهجري\n• أسئلة فقهية وإسلامية\n\n📚 قاعدة معرفة: 21+ كتاب في الفقه المالكي\n🤖 مدعوم بالذكاء الاصطناعي\n\nكيف يمكنني خدمتك اليوم؟",
      timestamp: new Date(),
    },
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [isDark, setIsDark] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

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
      
      // Send with language instruction
      const enhancedPrompt = languageInstruction + messageText;
      const response = await aiApi.ask(enhancedPrompt, detectedLang);
      
      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: response.content,
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, assistantMessage]);
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

  const handleQuickAction = (prompt: string) => {
    handleSend(prompt);
  };

  return (
    <div className={`min-h-screen ${isDark ? 'bg-gray-900' : 'bg-gradient-to-br from-slate-50 via-teal-50 to-emerald-50'}`}>
      {/* Header */}
      <header className={`sticky top-0 z-50 shadow-lg ${isDark ? 'bg-gray-800/90 backdrop-blur-lg' : 'glass-morphism'}`}>
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 rounded-full gradient-islamic flex items-center justify-center text-white shadow-lg">
                <Sparkles size={24} />
              </div>
              <div>
                <h1 className={`text-2xl font-bold ${isDark ? 'text-white' : 'text-gradient'}`}>Al-Muwatta</h1>
                <p className={`text-sm arabic-text font-bold ${isDark ? 'text-gray-300' : 'text-gray-600'}`}>الموطأ</p>
              </div>
            </div>
            
            <div className="flex items-center gap-2">
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
              <div className={`h-[calc(100vh-200px)] overflow-y-auto p-6 space-y-4 ${isDark ? 'bg-gray-900' : 'islamic-pattern'}`}>
                {messages.length === 1 && (
                  <div className="text-center py-8">
                    <div className={`inline-block p-6 rounded-2xl mb-4 ${isDark ? 'bg-islamic-green/20' : 'bg-gradient-to-br from-islamic-green/10 to-islamic-teal/10'}`}>
                      <Sparkles size={48} className={`mx-auto ${isDark ? 'text-islamic-gold' : 'text-islamic-green'}`} />
                    </div>
                    <h2 className={`text-2xl font-bold mb-2 ${isDark ? 'text-white' : 'text-gradient'}`}>
                      Ask me anything about Islam
                    </h2>
                    <p className={isDark ? 'text-gray-300' : 'text-gray-600'}>
                      Get authentic answers from Quran, Hadith, and Islamic scholarship
                    </p>
                  </div>
                )}

                {messages.map((message) => (
                  <ChatMessage
                    key={message.id}
                    role={message.role}
                    content={message.content}
                    timestamp={message.timestamp}
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

              {/* Quick Actions */}
              {messages.length === 1 && (
                <div className="border-t border-gray-200 bg-white/50">
                  <QuickActions onActionClick={handleQuickAction} />
                </div>
              )}

              {/* Input Area */}
              <div className={`border-t p-4 ${isDark ? 'border-gray-700 bg-gray-800/90' : 'border-gray-200 bg-white/80'}`}>
                <div className="flex gap-3">
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
                <p className={`text-xs mt-2 text-center ${isDark ? 'text-gray-400' : 'text-gray-500'}`}>
                  Powered by Google Gemini AI • Press Enter to send
                </p>
              </div>
            </div>
          </div>

          {/* Sidebar - Collapsible */}
          <div className={cn(
            "transition-all duration-300 space-y-4",
            "w-80 flex-shrink-0 hidden xl:block"
          )}>
            <PrayerTimesWidget />

            {/* Islamic Date */}
            <div className="glass-morphism rounded-xl p-4 shadow-lg">
              <h3 className="text-base font-semibold text-gradient mb-2">Today</h3>
              <p className="text-xs text-gray-600">
                {new Date().toLocaleDateString('en-US', {
                  weekday: 'long',
                  year: 'numeric',
                  month: 'long',
                  day: 'numeric',
                })}
              </p>
            </div>

            {/* Tips */}
            <div className="glass-morphism rounded-xl p-4 shadow-lg">
              <h3 className="text-base font-semibold text-gradient mb-2">💡 Tips</h3>
              <ul className="text-xs text-gray-600 space-y-1">
                <li>• Ask in any language</li>
                <li>• Search Hadiths by topic</li>
                <li>• Get Quran explanations</li>
                <li>• Daily Islamic reminders</li>
              </ul>
            </div>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="mt-2 py-3 text-center text-xs text-gray-600">
        <p>Built with ❤️ for the Muslim Ummah • الحمد لله رب العالمين</p>
      </footer>
    </div>
  );
}

export default App;
