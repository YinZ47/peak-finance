/**
 * API Client for Peak Finance Backend
 * Handles all HTTP requests with auth token management
 */

class APIClient {
  constructor(baseURL = '/api') {
    this.baseURL = baseURL;
  }

  /**
   * Get auth token from cookie or localStorage
   */
  getToken() {
    // Check localStorage first (for mobile/SPA)
    const token = localStorage.getItem('access_token');
    if (token) return token;
    
    // Cookie is handled by browser automatically for same-origin requests
    return null;
  }

  /**
   * Build headers with auth token
   */
  getHeaders(includeAuth = true, isFormData = false) {
    const headers = {
      'Accept': 'application/json'
    };

    if (!isFormData) {
      headers['Content-Type'] = 'application/json';
    }

    if (includeAuth) {
      const token = this.getToken();
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }
    }

    return headers;
  }

  /**
   * Extract error message from various error formats
   */
  extractErrorMessage(data) {
    if (!data) return 'Request failed';
    
    // If it's already a string
    if (typeof data === 'string') return data;
    
    // Check for detail property (FastAPI standard)
    if (data.detail) {
      // If detail is a string
      if (typeof data.detail === 'string') {
        return data.detail;
      }
      
      // If detail is an array (validation errors)
      if (Array.isArray(data.detail)) {
        return data.detail.map(err => {
          if (typeof err === 'string') return err;
          return err.msg || err.message || JSON.stringify(err);
        }).join(', ');
      }
      
      // If detail is an object
      if (typeof data.detail === 'object') {
        return data.detail.message || data.detail.msg || JSON.stringify(data.detail);
      }
    }
    
    // Check for message property
    if (data.message) return data.message;
    if (data.msg) return data.msg;
    if (data.error) return data.error;
    
    // Last resort
    return 'Request failed';
  }

  /**
   * Generic request handler
   */
  async request(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`;
    const { auth = true, headers: customHeaders, ...rest } = options;
    const isFormData = rest.body instanceof FormData;

    const config = {
      ...rest,
      headers: {
        ...this.getHeaders(auth !== false, isFormData),
        ...(customHeaders || {})
      }
    };

    try {
      const response = await fetch(url, config);
      
      // Handle 401 Unauthorized
      if (response.status === 401) {
        localStorage.removeItem('access_token');
        if (window.location.pathname !== '/auth') {
          window.location.href = '/auth';
        }
        throw new Error('Unauthorized - please login');
      }

      let data = null;
      let rawBody = '';

      if (response.status !== 204) {
        try {
          rawBody = await response.text();
        } catch (e) {
          rawBody = '';
        }

        if (rawBody && rawBody.trim().length) {
          try {
            data = JSON.parse(rawBody);
          } catch (parseError) {
            data = { detail: rawBody };
          }
        }
      }

      if (!response.ok) {
        const errorMessage = this.extractErrorMessage(data);
        throw new Error(errorMessage);
      }

      return data;
    } catch (error) {
      console.error('API Error:', error);
      // Re-throw with a proper error message
      if (error.message) {
        throw error;
      } else {
        throw new Error('Network error. Please check your connection and try again.');
      }
    }
  }

  /**
   * GET request
   */
  async get(endpoint, options = {}) {
    return this.request(endpoint, {
      ...options,
      method: 'GET',
    });
  }

  /**
   * POST request
   */
  async post(endpoint, data, options = {}) {
    const config = {
      ...options,
      method: 'POST',
    };

    if (options.body === undefined) {
      if (typeof FormData !== 'undefined' && data instanceof FormData) {
        config.body = data;
      } else if (data !== undefined && data !== null) {
        config.body = JSON.stringify(data);
      }
    }

    return this.request(endpoint, config);
  }

  /**
   * PUT request
   */
  async put(endpoint, data, options = {}) {
    const config = {
      ...options,
      method: 'PUT',
    };

    if (options.body === undefined) {
      if (typeof FormData !== 'undefined' && data instanceof FormData) {
        config.body = data;
      } else if (data !== undefined && data !== null) {
        config.body = JSON.stringify(data);
      }
    }

    return this.request(endpoint, config);
  }

  /**
   * DELETE request
   */
  async delete(endpoint, options = {}) {
    return this.request(endpoint, {
      ...options,
      method: 'DELETE',
    });
  }
}

// Global API instance
const API = new APIClient();