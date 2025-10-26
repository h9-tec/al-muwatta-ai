import { useState, useEffect } from 'react';
import { Bookmark, Trash2, X } from 'lucide-react';
import ReactMarkdown from 'react-markdown';

interface BookmarkedMessage {
  id: string;
  content: string;
  question?: string;
  timestamp: string;
}

interface BookmarksViewProps {
  isOpen: boolean;
  onClose: () => void;
}

export function BookmarksView({ isOpen, onClose }: BookmarksViewProps) {
  const [bookmarks, setBookmarks] = useState<BookmarkedMessage[]>([]);

  useEffect(() => {
    if (isOpen) {
      loadBookmarks();
    }
  }, [isOpen]);

  const loadBookmarks = () => {
    const saved = localStorage.getItem('bookmarks');
    setBookmarks(saved ? JSON.parse(saved) : []);
  };

  const deleteBookmark = (id: string) => {
    const filtered = bookmarks.filter((b) => b.id !== id);
    setBookmarks(filtered);
    localStorage.setItem('bookmarks', JSON.stringify(filtered));
  };

  const clearAll = () => {
    if (confirm('Delete all bookmarks?')) {
      setBookmarks([]);
      localStorage.removeItem('bookmarks');
    }
  };

  if (!isOpen) return null;

  return (
    <div
      className="fixed inset-0 bg-black/50 flex items-center justify-center z-[200]"
      onClick={onClose}
    >
      <div
        className="bg-white rounded-2xl shadow-2xl w-full max-w-4xl max-h-[90vh] overflow-hidden"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="sticky top-0 bg-gradient-to-r from-islamic-green to-islamic-teal text-white p-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Bookmark size={24} />
              <div>
                <h2 className="text-2xl font-bold">Saved Answers</h2>
                <p className="text-sm opacity-90">{bookmarks.length} bookmarks</p>
              </div>
            </div>
            <button
              onClick={onClose}
              className="p-2 hover:bg-white/20 rounded-full transition"
            >
              <X size={24} />
            </button>
          </div>
        </div>

        {/* Content */}
        <div className="p-6 overflow-y-auto max-h-[calc(90vh-120px)]">
          {bookmarks.length === 0 ? (
            <div className="text-center py-12">
              <Bookmark size={48} className="mx-auto text-gray-300 mb-4" />
              <p className="text-gray-600">No bookmarks yet</p>
              <p className="text-sm text-gray-500 mt-2">
                Bookmark important answers to save them here
              </p>
            </div>
          ) : (
            <div className="space-y-4">
              {bookmarks.map((bookmark) => (
                <div
                  key={bookmark.id}
                  className="glass-morphism rounded-xl p-4 hover:shadow-md transition-shadow"
                >
                  {bookmark.question && (
                    <div className="mb-3 pb-3 border-b border-gray-200">
                      <p className="text-sm font-semibold text-gray-700">Question:</p>
                      <p className="text-sm text-gray-600 mt-1">{bookmark.question}</p>
                    </div>
                  )}

                  <div className="prose prose-sm max-w-none">
                    <ReactMarkdown>{bookmark.content}</ReactMarkdown>
                  </div>

                  <div className="flex items-center justify-between mt-4 pt-3 border-t border-gray-200">
                    <span className="text-xs text-gray-500">
                      {new Date(bookmark.timestamp).toLocaleDateString()}
                    </span>
                    <button
                      onClick={() => deleteBookmark(bookmark.id)}
                      className="p-1.5 text-red-600 hover:bg-red-50 rounded transition-colors"
                      title="Delete bookmark"
                    >
                      <Trash2 size={16} />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Footer */}
        {bookmarks.length > 0 && (
          <div className="sticky bottom-0 bg-gray-50 p-4 border-t border-gray-200">
            <button
              onClick={clearAll}
              className="w-full py-2 text-sm text-red-600 hover:bg-red-50 rounded-lg transition-colors"
            >
              Clear All Bookmarks
            </button>
          </div>
        )}
      </div>
    </div>
  );
}

