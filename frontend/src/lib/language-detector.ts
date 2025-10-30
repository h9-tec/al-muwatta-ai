export type SupportedLanguage = 'arabic' | 'english';

const arabicRegex = /[\u0600-\u06FF]/;

export const detectLanguage = (text: string): SupportedLanguage => {
  return arabicRegex.test(text) ? 'arabic' : 'english';
};

export const getLanguageInstruction = (language: SupportedLanguage, _text: string): string => {
  // Prefix the prompt with a concise language instruction
  return language === 'arabic' ? 'الرجاء الإجابة بالعربية: ' : 'Please answer in English: ';
};


