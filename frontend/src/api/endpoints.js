export const API_PREFIX = '/Thuancyber'

export const ENDPOINTS = {
  // Authentication & Profile
  AUTH: {
    REGISTER: `${API_PREFIX}/auth/register`,
    LOGIN: `${API_PREFIX}/auth/login`,
    ME: `${API_PREFIX}/auth/me`,
    CHANGE_PASSWORD: `${API_PREFIX}/auth/change-password`,
  },

  // Users & Roles Management
  USERS: {
    BASE: `${API_PREFIX}/users`,
    STATUS: (id) => `${API_PREFIX}/users/${id}/status`,
    ROLE: (id) => `${API_PREFIX}/users/${id}/role`,
    ROLES: `${API_PREFIX}/users/roles`,
    ROLES_ALL: `${API_PREFIX}/users/roles/all`,
  },

  // Categories
  CATEGORIES: {
    BASE: `${API_PREFIX}/categories`,
    BY_ID: (id) => `${API_PREFIX}/categories/${id}`,
  },

  // Products
  PRODUCTS: {
    BASE: `${API_PREFIX}/products`,
    BY_ID: (id) => `${API_PREFIX}/products/${id}`,
  },
}
