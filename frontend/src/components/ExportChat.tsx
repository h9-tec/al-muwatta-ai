import { Download, Copy, Share2, FileDown } from 'lucide-react';
import jsPDF from 'jspdf';
import html2canvas from 'html2canvas';
import { useState } from 'react';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

interface ExportChatProps {
  messages: Message[];
  targetId?: string;
}

export function ExportChat({ messages, targetId = 'chat-container' }: ExportChatProps) {
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

  const exportAsPdf = async () => {
    const container = document.getElementById(targetId);
    if (!(container instanceof HTMLElement)) {
      alert('Unable to find chat content for PDF export.');
      return;
    }

    const previous = {
      overflow: container.style.overflow,
      maxHeight: container.style.maxHeight,
      height: container.style.height,
      width: container.style.width,
      position: container.style.position,
      top: container.style.top,
      left: container.style.left,
    };

    try {
      const scrollWidth = container.scrollWidth;
      const scrollHeight = container.scrollHeight;

      container.style.overflow = 'visible';
      container.style.maxHeight = 'none';
      container.style.height = `${scrollHeight}px`;
      container.style.width = `${scrollWidth}px`;
      container.style.position = 'relative';
      container.style.top = '0';
      container.style.left = '0';

      await new Promise((resolve) => requestAnimationFrame(() => resolve(undefined)));

      const canvas = await html2canvas(container, {
        scale: Math.min(window.devicePixelRatio || 2, 3),
        useCORS: true,
        backgroundColor: '#ffffff',
        logging: false,
        width: scrollWidth,
        height: scrollHeight,
        windowWidth: scrollWidth,
        windowHeight: scrollHeight,
        scrollY: -window.scrollY,
        scrollX: -window.scrollX,
      });

      const imageData = canvas.toDataURL('image/png');
      const pdf = new jsPDF('p', 'mm', 'a4');

      const pageWidth = pdf.internal.pageSize.getWidth();
      const pageHeight = pdf.internal.pageSize.getHeight();

      const margin = 10;
      const usableWidth = pageWidth - margin * 2;
      const usableHeight = pageHeight - margin * 2;

      const imgWidth = usableWidth;
      const imgHeight = (canvas.height * imgWidth) / canvas.width;

      let heightLeft = imgHeight;
      let offset = margin;

      pdf.addImage(imageData, 'PNG', margin, offset, imgWidth, imgHeight);
      heightLeft -= usableHeight;

      while (heightLeft > 0) {
        pdf.addPage();
        offset = margin - (imgHeight - heightLeft);
        pdf.addImage(imageData, 'PNG', margin, offset, imgWidth, imgHeight);
        heightLeft -= usableHeight;
      }

      pdf.save(`almuwatta-chat-${new Date().toISOString().slice(0, 10)}.pdf`);
    } catch (error) {
      console.error('PDF export failed', error);
      alert('Failed to export PDF. Please try again.');
    } finally {
      container.style.overflow = previous.overflow;
      container.style.maxHeight = previous.maxHeight;
      container.style.height = previous.height;
      container.style.width = previous.width;
      container.style.position = previous.position;
      container.style.top = previous.top;
      container.style.left = previous.left;
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
              exportAsPdf();
              setIsOpen(false);
            }}
            className="w-full px-4 py-2 text-left hover:bg-gray-50 transition-colors flex items-center gap-3 text-sm"
          >
            <FileDown size={16} className="text-gray-600" />
            <span>Export as PDF</span>
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

