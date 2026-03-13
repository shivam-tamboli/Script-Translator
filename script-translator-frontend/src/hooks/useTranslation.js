import { useState, useEffect, useCallback, useRef } from 'react';
import { translateApi } from '../api/translateApi';

const POLLING_INTERVAL = 2000;

export const useTranslation = () => {
  const [file, setFile] = useState(null);
  const [sourceLang] = useState('mr');
  const [targetLang, setTargetLang] = useState('en');
  
  const [jobId, setJobId] = useState(null);
  const [status, setStatus] = useState(null);
  const [progress, setProgress] = useState(null);
  const [downloadUrl, setDownloadUrl] = useState(null);
  const [error, setError] = useState(null);
  const [isPolling, setIsPolling] = useState(false);
  
  const pollingIntervalRef = useRef(null);

  const pollJobStatus = useCallback(async (id) => {
    try {
      const response = await translateApi.getJobStatus(id);
      setStatus(response.status);
      
      if (response.progress !== undefined && response.progress !== null) {
        setProgress(response.progress);
      }
      
      if (response.download_url) {
        setDownloadUrl(response.download_url);
      }
      
      if (response.error) {
        setError(response.error);
      }
      
      if (response.status === 'completed' || response.status === 'failed') {
        setIsPolling(false);
        if (pollingIntervalRef.current) {
          clearInterval(pollingIntervalRef.current);
          pollingIntervalRef.current = null;
        }
      }
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to check status';
      setError(message);
      setIsPolling(false);
    }
  }, []);

  useEffect(() => {
    if (jobId && isPolling) {
      pollingIntervalRef.current = setInterval(() => {
        pollJobStatus(jobId);
      }, POLLING_INTERVAL);
    }

    return () => {
      if (pollingIntervalRef.current) {
        clearInterval(pollingIntervalRef.current);
        pollingIntervalRef.current = null;
      }
    };
  }, [jobId, isPolling, pollJobStatus]);

  const startTranslation = useCallback(async () => {
    if (!file) {
      setError('Please select a file');
      return;
    }

    setError(null);
    setStatus(null);
    setProgress(null);
    setDownloadUrl(null);

    try {
      const response = await translateApi.uploadFile(file, {
        sourceLang,
        targetLang,
      });

      setJobId(response.job_id);
      setStatus(response.status);
      setIsPolling(true);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Upload failed';
      setError(message);
    }
  }, [file, sourceLang, targetLang]);

  const reset = useCallback(() => {
    setFile(null);
    setJobId(null);
    setStatus(null);
    setProgress(null);
    setDownloadUrl(null);
    setError(null);
    setIsPolling(false);
    if (pollingIntervalRef.current) {
      clearInterval(pollingIntervalRef.current);
      pollingIntervalRef.current = null;
    }
  }, []);

  return {
    file,
    sourceLang,
    targetLang,
    status,
    progress,
    downloadUrl,
    error,
    isPolling,
    setFile,
    setTargetLang,
    startTranslation,
    reset,
  };
};
