import { Bot, User } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { cn } from '../lib/utils';
import { BookmarkButton } from './BookmarkButton';

interface ChatMessageProps {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp?: Date;
  question?: string;
}

// Detect if text is Arabic
const isArabicText = (text: string): boolean => {
  const arabicPattern = /[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF]/;
  const arabicMatches = text.match(new RegExp(arabicPattern, 'g'));
  return arabicMatches ? arabicMatches.length > 10 : false;
};

export function ChatMessage({ id, role, content, timestamp, question }: ChatMessageProps) {
  const isUser = role === 'user';
  const isArabic = isArabicText(content);

  return (
    <div
      className={cn(
        'flex gap-3 p-4 animate-slide-in',
        isUser ? 'flex-row-reverse' : 'flex-row'
      )}
    >
      <div
        className={cn(
          'flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center',
          isUser
            ? 'bg-gradient-to-br from-islamic-green to-islamic-teal text-white'
            : 'bg-gray-700 border-2 border-islamic-gold text-islamic-gold'
        )}
      >
        {isUser ? <User size={20} /> : <Bot size={20} />}
      </div>

      <div className={cn('flex flex-col', isUser ? 'items-end' : 'items-start', 'max-w-[90%]')}>
        <div
          className={cn(
            'rounded-2xl px-6 py-4 shadow-sm',
            isUser
              ? 'bg-gradient-to-br from-islamic-green to-islamic-teal text-white rounded-tr-none'
              : 'glass-morphism text-gray-800 rounded-tl-none'
          )}
        >
          {isUser ? (
            <p className={cn(
              "text-sm leading-relaxed whitespace-pre-wrap",
              isArabic && "text-right font-arabic"
            )}>
              {content}
            </p>
          ) : (
            <div className={cn(
              "prose prose-sm max-w-none markdown-content",
              isArabic && "text-right font-arabic arabic-markdown"
            )} dir={isArabic ? "rtl" : "ltr"}>
              <ReactMarkdown remarkPlugins={[remarkGfm]}>
                {content}
              </ReactMarkdown>
            </div>
          )}
        </div>
        <div className="flex items-center gap-2 mt-1 px-2">
          {timestamp && (
            <span className="text-xs text-gray-500">
              {timestamp.toLocaleTimeString('en-US', {
                hour: '2-digit',
                minute: '2-digit',
              })}
            </span>
          )}
          {!isUser && (
            <BookmarkButton messageId={id} content={content} question={question} />
          )}
        </div>
      </div>
    </div>
  );
}

