import React from 'react';

const TARGET_LANGUAGES = [
  { code: 'en', name: 'English' },
  { code: 'hi', name: 'Hindi' },
];

const TranslationOptions = ({
  sourceLang,
  targetLang,
  onSourceLangChange,
  onTargetLangChange,
  disabled = false,
}) => {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
      <div>
        <label
          htmlFor="source-lang"
          className="block text-sm font-medium text-gray-700 mb-1"
        >
          Source Language
        </label>
        <div className="block w-full px-3 py-2 bg-gray-100 border border-gray-300 rounded-md text-gray-700">
          Marathi
        </div>
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
    </div>
  );
};

export default TranslationOptions;
