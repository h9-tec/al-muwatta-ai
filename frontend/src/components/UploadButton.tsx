import { useState } from 'react';
import { Upload, FileText, Image as ImageIcon, Loader2 } from 'lucide-react';
import axios from 'axios';

interface UploadButtonProps {
  onUploadComplete?: (message: string) => void;
}

export function UploadButton({ onUploadComplete }: UploadButtonProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [uploadType, setUploadType] = useState<'image' | 'pdf' | 'text'>('image');

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setUploading(true);

    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('title', file.name.split('.')[0]);
      formData.append('category', 'general');
      formData.append('add_to_knowledge_base', 'true');

      const endpoint = uploadType === 'pdf' 
        ? '/api/v1/upload/book-pdf'
        : '/api/v1/upload/book-image';

      const response = await axios.post(
        `http://localhost:8000${endpoint}`,
        formData,
        {
          headers: { 'Content-Type': 'multipart/form-data' },
        }
      );

      if (response.data.status === 'success') {
        const message = `✅ تم رفع الكتاب بنجاح!\n\n${response.data.message}\n\nعدد الكلمات: ${response.data.word_count}`;
        onUploadComplete?.(message);
        setIsOpen(false);
      }
    } catch (error) {
      console.error('Upload failed:', error);
      onUploadComplete?.('❌ فشل رفع الملف. تأكد من تشغيل الخادم.');
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="p-2 rounded-full hover:bg-gray-100 transition-colors text-islamic-green"
        title="رفع كتاب للمعرفة"
      >
        <Upload size={20} />
      </button>

      {isOpen && (
        <div className="fixed bottom-24 left-4 glass-morphism rounded-xl shadow-2xl p-6 w-80 animate-slide-in z-[100] border-2 border-islamic-green/20">
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-bold text-lg text-islamic-green arabic-text">إضافة كتاب للمعرفة</h3>
            <button 
              onClick={() => setIsOpen(false)}
              className="text-gray-500 hover:text-gray-700 text-xl"
            >
              ×
            </button>
          </div>
          
          <div className="space-y-4">
            <label className="flex items-center gap-3 cursor-pointer hover:bg-white/70 p-3 rounded-lg border-2 border-transparent hover:border-islamic-teal/30 transition-all">
              <input
                type="file"
                accept="image/*"
                onChange={handleFileUpload}
                disabled={uploading}
                className="hidden"
              />
              <div className="p-2 bg-islamic-teal/10 rounded-lg">
                <ImageIcon size={20} className="text-islamic-teal" />
              </div>
              <div className="flex-1 text-right arabic-text">
                <div className="font-semibold text-sm">صورة صفحة كتاب</div>
                <div className="text-xs text-gray-600">JPG, PNG</div>
              </div>
            </label>

            <label className="flex items-center gap-3 cursor-pointer hover:bg-white/70 p-3 rounded-lg border-2 border-transparent hover:border-islamic-green/30 transition-all">
              <input
                type="file"
                accept=".pdf"
                onChange={(e) => {
                  setUploadType('pdf');
                  handleFileUpload(e);
                }}
                disabled={uploading}
                className="hidden"
              />
              <div className="p-2 bg-islamic-green/10 rounded-lg">
                <FileText size={20} className="text-islamic-green" />
              </div>
              <div className="flex-1 text-right arabic-text">
                <div className="font-semibold text-sm">ملف PDF كامل</div>
                <div className="text-xs text-gray-600">كتب الفقه المالكي</div>
              </div>
            </label>

            {uploading && (
              <div className="flex items-center justify-center gap-2 text-sm text-islamic-teal py-4 bg-white/50 rounded-lg">
                <Loader2 size={20} className="animate-spin" />
                <span className="font-semibold arabic-text">جاري المعالجة...</span>
              </div>
            )}
          </div>

          <div className="mt-4 pt-4 border-t border-gray-200">
            <p className="text-xs text-gray-600 text-right arabic-text leading-relaxed">
              💡 رفع كتب الفقه المالكي يضيفها تلقائياً لقاعدة المعرفة
            </p>
            <p className="text-xs text-islamic-green mt-1 text-right arabic-text font-semibold">
              📚 {21} كتاب في قاعدة البيانات حالياً
            </p>
          </div>
        </div>
      )}
    </div>
  );
}

