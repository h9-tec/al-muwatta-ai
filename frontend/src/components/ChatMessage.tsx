import { useState } from 'react';
import { Bot, User, ChevronDown, ChevronUp } from 'lucide-react';
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
  metadata?: Record<string, unknown>;
}

// Detect if text is Arabic
const isArabicText = (text: string): boolean => {
  const arabicPattern = /[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF]/;
  const arabicMatches = text.match(new RegExp(arabicPattern, 'g'));
  return arabicMatches ? arabicMatches.length > 10 : false;
};

const renderSources = (metadata?: Record<string, unknown>) => {
  if (!metadata) return null;
  const sources = metadata.sources as Array<{ type: string; content: string }> | undefined;
  if (!sources || sources.length === 0) return null;

  return (
    <div className="mt-3 space-y-2 text-xs text-gray-600 border-t border-gray-200 pt-3">
      <p className="font-semibold">Sources referenced:</p>
      {sources.map((source, index) => (
        <div key={index} className="bg-white/60 rounded-lg p-2">
          <p className="uppercase tracking-wide text-[10px] text-gray-500 mb-1">{source.type}</p>
          <pre className="whitespace-pre-wrap break-words text-gray-700">{source.content}</pre>
        </div>
      ))}
    </div>
  );
};

export function ChatMessage({ id, role, content, timestamp, question, metadata }: ChatMessageProps) {
  const isUser = role === 'user';
  const isArabic = isArabicText(content);
  const [showRagChunks, setShowRagChunks] = useState(false);

  const ragChunks = Array.isArray(metadata?.rag_chunks)
    ? (metadata?.rag_chunks as Array<Record<string, unknown>>)
    : [];

  const renderRagChunks = () => {
    if (!ragChunks.length) return null;

    return (
      <div className="mt-3 border-t border-gray-200 pt-3 text-xs">
        <button
          type="button"
          onClick={() => setShowRagChunks((prev) => !prev)}
          className="w-full flex items-center justify-between rounded-lg bg-white/60 px-3 py-2 text-left font-semibold text-gray-700 hover:bg-white/80"
        >
          <span>Retrieved Maliki context ({ragChunks.length})</span>
          {showRagChunks ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
        </button>

        {showRagChunks && (
          <div className="mt-3 space-y-3">
            {ragChunks.map((chunk, index) => {
              const metadata = (chunk.metadata as Record<string, unknown>) || {};
              const score = typeof chunk.score === 'number' ? chunk.score.toFixed(2) : undefined;
              return (
                <div
                  key={(chunk.id as string) ?? index}
                  className="rounded-lg bg-white/70 p-3 shadow-sm"
                >
                  <div className="flex flex-wrap items-center justify-between gap-2 text-[11px] uppercase tracking-wide text-gray-500">
                    <span>{(metadata.topic as string) || 'Maliki fiqh reference'}</span>
                    <span>{score ? `Score: ${score}` : null}</span>
                  </div>
                  <pre className="mt-2 whitespace-pre-wrap break-words text-gray-700">
                    {(chunk.text as string) ?? ''}
                  </pre>
                </div>
              );
            })}
          </div>
        )}
      </div>
    );
  };

  return (
    <div
      className={cn(
        'flex gap-3 p-4 animate-slide-in',
        isUser ? 'flex-row-reverse' : 'flex-row'
      )}
    >
      <div
        className={cn(
          'flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center shadow-sm',
          isUser
            ? 'bg-gradient-paradise text-white'
            : 'bg-prophetic-cream border border-paradise-500/20 text-paradise-600'
        )}
      >
        {isUser ? <User size={20} /> : <Bot size={20} />}
      </div>

      <div className={cn('flex flex-col', isUser ? 'items-end' : 'items-start', 'max-w-[90%]')}>
        <div
          className={cn(
            'rounded-2xl px-6 py-4',
            isUser
              ? 'bg-gradient-paradise text-white shadow-prophetic rounded-tr-none'
              : 'glass-morphism text-neutral-800 shadow-prophetic-sm rounded-tl-none border border-paradise-500/10'
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
              {renderSources(metadata)}
              {renderRagChunks()}
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

