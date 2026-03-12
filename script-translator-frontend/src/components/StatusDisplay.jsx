import React from 'react';

const StatusDisplay = ({ status, downloadUrl, error, onDownload, onRetry }) => {
  if (!status) {
    return null;
  }

  if (status === 'pending' || status === 'processing') {
    return (
      <div className="flex flex-col items-center justify-center py-6">
        <div className="animate-spin rounded-full h-10 w-10 border-4 border-blue-500 border-t-transparent"></div>
        <p className="mt-4 text-sm text-gray-600">
          {status === 'pending' ? 'Preparing translation...' : 'Translating...'}
        </p>
      </div>
    );
  }

  if (status === 'completed') {
    return (
      <div className="flex flex-col items-center justify-center py-6">
        <div className="flex items-center justify-center h-12 w-12 rounded-full bg-green-100">
          <svg
            className="h-6 w-6 text-green-600"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M5 13l4 4L19 7"
            />
          </svg>
        </div>
        <p className="mt-4 text-sm font-medium text-gray-900">
          Translation completed!
        </p>
        {downloadUrl && (
          <button
            onClick={onDownload}
            className="mt-4 px-6 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
          >
            Download Translated File
          </button>
        )}
      </div>
    );
  }

  if (status === 'failed') {
    return (
      <div className="flex flex-col items-center justify-center py-6">
        <div className="flex items-center justify-center h-12 w-12 rounded-full bg-red-100">
          <svg
            className="h-6 w-6 text-red-600"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M6 18L18 6M6 6l12 12"
            />
          </svg>
        </div>
        <p className="mt-4 text-sm font-medium text-gray-900">
          Translation failed
        </p>
        {error && (
          <p className="mt-1 text-sm text-red-600 max-w-md text-center">
            {error}
          </p>
        )}
        <button
          onClick={onRetry}
          className="mt-4 px-6 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-500"
        >
          Try Again
        </button>
      </div>
    );
  }

  return null;
};

export default StatusDisplay;
