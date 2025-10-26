import { useState, useEffect } from 'react';
import { Bookmark, BookmarkCheck } from 'lucide-react';

interface BookmarkButtonProps {
  messageId: string;
  content: string;
  question?: string;
}

interface BookmarkedMessage {
  id: string;
  content: string;
  question?: string;
  timestamp: string;
}

export function BookmarkButton({ messageId, content, question }: BookmarkButtonProps) {
  const [isBookmarked, setIsBookmarked] = useState(false);

  useEffect(() => {
    const bookmarks: BookmarkedMessage[] = JSON.parse(
      localStorage.getItem('bookmarks') || '[]'
    );
    setIsBookmarked(bookmarks.some((b) => b.id === messageId));
  }, [messageId]);

  const toggleBookmark = () => {
    const bookmarks: BookmarkedMessage[] = JSON.parse(
      localStorage.getItem('bookmarks') || '[]'
    );

    if (isBookmarked) {
      // Remove bookmark
      const filtered = bookmarks.filter((b) => b.id !== messageId);
      localStorage.setItem('bookmarks', JSON.stringify(filtered));
      setIsBookmarked(false);
    } else {
      // Add bookmark
      const newBookmark: BookmarkedMessage = {
        id: messageId,
        content,
        question,
        timestamp: new Date().toISOString(),
      };
      bookmarks.unshift(newBookmark);
      localStorage.setItem('bookmarks', JSON.stringify(bookmarks));
      setIsBookmarked(true);
    }
  };

  return (
    <button
      onClick={toggleBookmark}
      className={`p-1.5 rounded-full transition-colors ${
        isBookmarked
          ? 'text-islamic-gold hover:text-islamic-gold/80'
          : 'text-gray-400 hover:text-gray-600'
      }`}
      title={isBookmarked ? 'Remove bookmark' : 'Bookmark this answer'}
    >
      {isBookmarked ? <BookmarkCheck size={16} /> : <Bookmark size={16} />}
    </button>
  );
}

