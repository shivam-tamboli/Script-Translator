import React from 'react';
import Layout from '../components/Layout';
import FileUpload from '../components/FileUpload';
import TranslationOptions from '../components/TranslationOptions';
import StatusDisplay from '../components/StatusDisplay';
import { useTranslation } from '../hooks/useTranslation';

const HomePage = () => {
  const {
    file,
    sourceLang,
    targetLang,
    provider,
    status,
    downloadUrl,
    error,
    setFile,
    setSourceLang,
    setTargetLang,
    setProvider,
    startTranslation,
    reset,
  } = useTranslation();

  const isUploading = status === 'pending' || status === 'processing';
  const canTranslate = file && !isUploading;

  const handleDownload = async () => {
    if (!downloadUrl) return;
    
    const filename = downloadUrl.split('/').pop();
    if (!filename) return;

    const { translateApi } = await import('../api/translateApi');
    
    try {
      const blob = await translateApi.downloadFile(filename);
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (err) {
      console.error('Download failed:', err);
    }
  };

  return (
    <Layout>
      <div className="space-y-6">
        <FileUpload
          file={file}
          onFileSelect={setFile}
          onFileRemove={() => setFile(null)}
          disabled={isUploading}
        />

        <TranslationOptions
          sourceLang={sourceLang}
          targetLang={targetLang}
          provider={provider}
          onSourceLangChange={setSourceLang}
          onTargetLangChange={setTargetLang}
          onProviderChange={setProvider}
          disabled={isUploading}
        />

        <div className="flex justify-center">
          <button
            onClick={startTranslation}
            disabled={!canTranslate}
            className={`px-8 py-3 rounded-md font-medium text-white transition-colors ${
              canTranslate
                ? 'bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500'
                : 'bg-gray-400 cursor-not-allowed'
            }`}
          >
            {isUploading ? 'Translating...' : 'Translate'}
          </button>
        </div>

        {error && (
          <div className="p-4 bg-red-50 border border-red-200 rounded-md">
            <p className="text-sm text-red-600">{error}</p>
          </div>
        )}

        <StatusDisplay
          status={status}
          downloadUrl={downloadUrl}
          error={error}
          onDownload={handleDownload}
          onRetry={reset}
        />
      </div>
    </Layout>
  );
};

export default HomePage;
