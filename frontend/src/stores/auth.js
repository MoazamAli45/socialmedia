import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/services/api'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const token = ref(localStorage.getItem('token'))
  const isLoading = ref(false)

  const isAuthenticated = computed(() => !!token.value)

  const login = async (credentials) => {
    try {
      isLoading.value = true
      const response = await api.post('/login', credentials)
      console.log('Login response:', response.data)

      token.value = response.data.token
      user.value = response.data.user

      localStorage.setItem('token', token.value)
      // Store user ID in localStorage for persistence
      localStorage.setItem('userId', response.data.user.id)
      // Use consistent Authorization header (e.g., Token)
      api.defaults.headers.common['Authorization'] = `Token ${token.value}`

      return { success: true }
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.message || 'Login failed',
      }
    } finally {
      isLoading.value = false
    }
  }

  const signup = async (userData) => {
    try {
      isLoading.value = true
      const response = await api.post('/signup', userData)
      console.log('Signup MES response:', response.data)

      token.value = response.data.token
      user.value = response.data.user

      localStorage.setItem('token', token.value)
      localStorage.setItem('userId', response.data.user.id)
      // Use consistent Authorization header (e.g., Token)
      api.defaults.headers.common['Authorization'] = `Token ${token.value}`

      return { success: true }
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.message || 'Signup failed',
      }
    } finally {
      isLoading.value = false
    }
  }

  const logout = () => {
    token.value = null
    user.value = null
    localStorage.removeItem('token')
    localStorage.removeItem('userId')
    delete api.defaults.headers.common['Authorization']
  }

  const fetchUser = async (userId) => {
    try {
      isLoading.value = true
      // Use provided userId or fallback to localStorage
      const id = userId || localStorage.getItem('userId')
      if (!id) {
        throw new Error('User ID is required to fetch user')
      }
      console.log('Fetching user with ID:', id)
      const response = await api.get(`/users/profile?user=${id}`)
      user.value = response.data
    } catch (error) {
      console.error('Failed to fetch user:', error)
      // Only logout if the error indicates an invalid token (e.g., 401 Unauthorized)
      if (error.response?.status === 401) {
        logout()
      }
    } finally {
      isLoading.value = false
    }
  }

  // Initialize auth state
  if (token.value) {
    api.defaults.headers.common['Authorization'] = `Token ${token.value}`
    // Only call fetchUser if userId is available
    const storedUserId = localStorage.getItem('userId')
    if (storedUserId) {
      fetchUser(storedUserId)
    }
  }

  return {
    user,
    token,
    isLoading,
    isAuthenticated,
    login,
    signup,
    logout,
    fetchUser,
  }
})
