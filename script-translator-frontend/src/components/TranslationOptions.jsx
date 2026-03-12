import React from 'react';

const LANGUAGES = [
  { code: 'mr', name: 'Marathi' },
  { code: 'hi', name: 'Hindi' },
  { code: 'gu', name: 'Gujarati' },
  { code: 'ta', name: 'Tamil' },
  { code: 'te', name: 'Telugu' },
  { code: 'bn', name: 'Bengali' },
  { code: 'kn', name: 'Kannada' },
  { code: 'ml', name: 'Malayalam' },
];

const TARGET_LANGUAGES = [
  { code: 'en', name: 'English' },
];

const PROVIDERS = [
  { code: 'openai', name: 'OpenAI' },
  { code: 'google', name: 'Google Translate' },
  { code: 'deepl', name: 'DeepL' },
  { code: 'indictrans', name: 'IndicTrans' },
];

const TranslationOptions = ({
  sourceLang,
  targetLang,
  provider,
  onSourceLangChange,
  onTargetLangChange,
  onProviderChange,
  disabled = false,
}) => {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
      <div>
        <label
          htmlFor="source-lang"
          className="block text-sm font-medium text-gray-700 mb-1"
        >
          Source Language
        </label>
        <select
          id="source-lang"
          value={sourceLang}
          onChange={(e) => onSourceLangChange(e.target.value)}
          disabled={disabled}
          className="block w-full px-3 py-2 bg-white border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 disabled:bg-gray-50 disabled:text-gray-500"
        >
          {LANGUAGES.map((lang) => (
            <option key={lang.code} value={lang.code}>
              {lang.name}
            </option>
          ))}
        </select>
      </div>

      <div>
        <label
          htmlFor="target-lang"
          className="block text-sm font-medium text-gray-700 mb-1"
        >
          Target Language
        </label>
        <select
          id="target-lang"
          value={targetLang}
          onChange={(e) => onTargetLangChange(e.target.value)}
          disabled={disabled}
          className="block w-full px-3 py-2 bg-white border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 disabled:bg-gray-50 disabled:text-gray-500"
        >
          {TARGET_LANGUAGES.map((lang) => (
            <option key={lang.code} value={lang.code}>
              {lang.name}
            </option>
          ))}
        </select>
      </div>

      <div>
        <label
          htmlFor="provider"
          className="block text-sm font-medium text-gray-700 mb-1"
        >
          Provider
        </label>
        <select
          id="provider"
          value={provider}
          onChange={(e) => onProviderChange(e.target.value)}
          disabled={disabled}
          className="block w-full px-3 py-2 bg-white border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 disabled:bg-gray-50 disabled:text-gray-500"
        >
          {PROVIDERS.map((p) => (
            <option key={p.code} value={p.code}>
              {p.name}
            </option>
          ))}
        </select>
      </div>
    </div>
  );
};

export default TranslationOptions;
