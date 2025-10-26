import { Download, Copy, Share2 } from 'lucide-react';
import { useState } from 'react';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

interface ExportChatProps {
  messages: Message[];
}

export function ExportChat({ messages }: ExportChatProps) {
  const [isOpen, setIsOpen] = useState(false);

  const exportAsText = () => {
    const text = messages
      .map((m) => {
        const time = new Date(m.timestamp).toLocaleString();
        const role = m.role === 'user' ? 'You' : 'Al-Muwatta';
        return `[${time}] ${role}:\n${m.content}\n`;
      })
      .join('\n---\n\n');

    const blob = new Blob([text], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `almuwatta-chat-${Date.now()}.txt`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const exportAsMarkdown = () => {
    const markdown = messages
      .map((m) => {
        const time = new Date(m.timestamp).toLocaleString();
        const role = m.role === 'user' ? '**You**' : '**Al-Muwatta**';
        return `### ${role} (${time})\n\n${m.content}\n`;
      })
      .join('\n---\n\n');

    const fullMarkdown = `# Al-Muwatta Conversation\n\nExported: ${new Date().toLocaleString()}\n\n---\n\n${markdown}`;

    const blob = new Blob([fullMarkdown], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `almuwatta-chat-${Date.now()}.md`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const copyToClipboard = async () => {
    const text = messages
      .map((m) => `${m.role === 'user' ? 'Q' : 'A'}: ${m.content}`)
      .join('\n\n');

    try {
      await navigator.clipboard.writeText(text);
      alert('Conversation copied to clipboard!');
    } catch (err) {
      alert('Failed to copy to clipboard');
    }
  };

  return (
    <div className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="p-2 rounded-full hover:bg-gray-100 transition-colors text-gray-700"
        title="Export conversation"
      >
        <Download size={20} />
      </button>

      {isOpen && (
        <div className="absolute top-full right-0 mt-2 w-56 bg-white rounded-lg shadow-2xl border border-gray-200 py-2 z-50">
          <button
            onClick={() => {
              exportAsText();
              setIsOpen(false);
            }}
            className="w-full px-4 py-2 text-left hover:bg-gray-50 transition-colors flex items-center gap-3 text-sm"
          >
            <Download size={16} className="text-gray-600" />
            <span>Export as Text</span>
          </button>

          <button
            onClick={() => {
              exportAsMarkdown();
              setIsOpen(false);
            }}
            className="w-full px-4 py-2 text-left hover:bg-gray-50 transition-colors flex items-center gap-3 text-sm"
          >
            <Download size={16} className="text-gray-600" />
            <span>Export as Markdown</span>
          </button>

          <button
            onClick={() => {
              copyToClipboard();
              setIsOpen(false);
            }}
            className="w-full px-4 py-2 text-left hover:bg-gray-50 transition-colors flex items-center gap-3 text-sm"
          >
            <Copy size={16} className="text-gray-600" />
            <span>Copy to Clipboard</span>
          </button>

          <button
            onClick={() => setIsOpen(false)}
            className="w-full px-4 py-2 text-left hover:bg-gray-50 transition-colors flex items-center gap-3 text-sm border-t border-gray-200 mt-1"
          >
            <Share2 size={16} className="text-gray-600" />
            <span>Share (Coming Soon)</span>
          </button>
        </div>
      )}
    </div>
  );
}

