/**
 * Authentication Module
 * Handles login, register, logout, and auth state
 */

const Auth = {
  /**
   * Check if user is authenticated
   */
  isAuthenticated() {
    const token = localStorage.getItem('access_token');
    return !!token;
  },

  /**
   * Get current user data
   */
  async getCurrentUser() {
    try {
      const user = await API.get('/auth/me');
      return user;
    } catch (error) {
      return null;
    }
  },

  /**
   * Register new user
   */
  async register(email, password) {
    try {
      const user = await API.post('/auth/register', { email, password }, { auth: false });
      showToast('Account created! Please login.', 'success');
      return user;
    } catch (error) {
      throw error;
    }
  },

  /**
   * Login user
   */
  async login(email, password) {
    try {
      const response = await API.post('/auth/login', { email, password }, { auth: false });
      
      // Store token
      localStorage.setItem('access_token', response.access_token);
      
      showToast('Login successful!', 'success');
      
      // Redirect to dashboard
      setTimeout(() => {
        window.location.href = '/dashboard';
      }, 500);
      
      return response;
    } catch (error) {
      throw error;
    }
  },

  /**
   * Logout user
   */
  async logout() {
    try {
      await API.post('/auth/logout');
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      localStorage.removeItem('access_token');
      showToast('Logged out successfully', 'success');
      window.location.href = '/';
    }
  },

  /**
   * Update nav UI based on auth state
   */
  async updateNavUI() {
    const navAuth = document.getElementById('navAuth');
    const navUser = document.getElementById('navUser');
    const userEmail = document.getElementById('userEmail');

    if (this.isAuthenticated()) {
      const user = await this.getCurrentUser();
      if (user) {
        navAuth.classList.add('hidden');
        navUser.classList.remove('hidden');
        userEmail.textContent = user.email;
      }
    } else {
      navAuth.classList.remove('hidden');
      navUser.classList.add('hidden');
    }
  }
};

// Login form handler
document.getElementById('loginFormElement')?.addEventListener('submit', async (e) => {
  e.preventDefault();
  
  const email = document.getElementById('loginEmail').value;
  const password = document.getElementById('loginPassword').value;
  const btnText = document.getElementById('loginBtnText');
  const btnLoader = document.getElementById('loginBtnLoader');

  btnText.classList.add('hidden');
  btnLoader.classList.remove('hidden');

  try {
    await Auth.login(email, password);
  } catch (error) {
    showToast(error.message || 'Login failed', 'error');
    btnText.classList.remove('hidden');
    btnLoader.classList.add('hidden');
  }
});

// Register form handler
document.getElementById('registerFormElement')?.addEventListener('submit', async (e) => {
  e.preventDefault();
  
  const email = document.getElementById('registerEmail').value;
  const password = document.getElementById('registerPassword').value;
  const confirmPassword = document.getElementById('confirmPassword').value;
  const btnText = document.getElementById('registerBtnText');
  const btnLoader = document.getElementById('registerBtnLoader');

  // Validate passwords match
  if (password !== confirmPassword) {
    showToast('Passwords do not match', 'error');
    return;
  }

  btnText.classList.add('hidden');
  btnLoader.classList.remove('hidden');

  try {
    await Auth.register(email, password);
    // Switch to login tab
    document.querySelector('[data-tab="login"]').click();
    // Clear form
    e.target.reset();
  } catch (error) {
    showToast(error.message || 'Registration failed', 'error');
  } finally {
    btnText.classList.remove('hidden');
    btnLoader.classList.add('hidden');
  }
});

// Logout button
document.getElementById('logoutBtn')?.addEventListener('click', () => {
  Auth.logout();
});