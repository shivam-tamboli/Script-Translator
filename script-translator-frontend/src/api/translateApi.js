import axiosClient from './axiosClient';

export const translateApi = {
  uploadFile: async (file, options = {}) => {
    const formData = new FormData();
    formData.append('file', file);
    
    if (options.targetLang) {
      formData.append('target_lang', options.targetLang);
    }
    if (options.provider) {
      formData.append('provider', options.provider);
    }
    if (options.sourceLang) {
      formData.append('source_lang', options.sourceLang);
    }

    const response = await axiosClient.post(
      '/api/v1/translate',
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    );
    return response.data;
  },

  getJobStatus: async (jobId) => {
    const response = await axiosClient.get(`/api/v1/translate/${jobId}`);
    return response.data;
  },

  getProviders: async () => {
    const response = await axiosClient.get('/providers');
    return response.data;
  },

  downloadFile: async (filename) => {
    const response = await axiosClient.get(`/api/v1/files/${filename}`, {
      responseType: 'blob',
    });
    return response.data;
  },
};
