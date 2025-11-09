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
  getHeaders(includeAuth = true) {
    const headers = {
      'Content-Type': 'application/json',
    };

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
    const config = {
      ...options,
      headers: this.getHeaders(options.auth !== false),
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

      let data;
      try {
        data = await response.json();
      } catch (e) {
        // If response is not JSON
        data = { detail: await response.text() || 'Request failed' };
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
    return this.request(endpoint, {
      ...options,
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  /**
   * PUT request
   */
  async put(endpoint, data, options = {}) {
    return this.request(endpoint, {
      ...options,
      method: 'PUT',
      body: JSON.stringify(data),
    });
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