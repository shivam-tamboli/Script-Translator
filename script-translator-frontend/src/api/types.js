/**
 * @typedef {'pending' | 'processing' | 'completed' | 'failed'} JobStatus
 */

/**
 * @typedef {Object} TranslateResponse
 * @property {string} job_id
 * @property {JobStatus} status
 * @property {string} [message]
 */

/**
 * @typedef {Object} JobStatusResponse
 * @property {string} job_id
 * @property {JobStatus} status
 * @property {string|null} download_url
 * @property {string|null} error
 * @property {number|null} progress
 */

/**
 * @typedef {Object} Provider
 * @property {string} name
 * @property {boolean} requires_api_key
 */

/**
 * @typedef {Object} ProvidersResponse
 * @property {Provider[]} providers
 */

export const JobStatus = {
  PENDING: 'pending',
  PROCESSING: 'processing',
  COMPLETED: 'completed',
  FAILED: 'failed'
};
