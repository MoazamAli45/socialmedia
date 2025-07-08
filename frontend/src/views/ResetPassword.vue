<!-- src/components/ResetPassword.vue -->
<template>
  <div class="min-h-screen bg-gray-50 flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
    <div class="max-w-md w-full space-y-8">
      <div>
        <h2 class="text-center text-3xl font-bold text-gray-900">Set New Password</h2>
        <p class="mt-2 text-center text-sm text-gray-600">Enter your new password below.</p>
      </div>
      <form class="mt-8 space-y-6" @submit.prevent="submit">
        <div class="-space-y-px flex flex-col gap-4">
          <div>
            <label for="new-password" class="sr-only">New Password</label>
            <input
              id="new-password"
              v-model="newPassword"
              type="password"
              required
              class="appearance-none rounded-md relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm"
              placeholder="New Password"
            />
          </div>
          <div>
            <label for="confirm-password" class="sr-only">Confirm Password</label>
            <input
              id="confirm-password"
              v-model="confirmPassword"
              type="password"
              required
              class="appearance-none rounded-md relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm"
              placeholder="Confirm Password"
            />
          </div>
        </div>

        <div v-if="error" class="text-red-600 text-sm text-center">{{ error }}</div>
        <div v-if="message" class="text-green-600 text-sm text-center">{{ message }}</div>

        <div>
          <button
            type="submit"
            :disabled="isLoading || newPassword !== confirmPassword"
            class="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50"
          >
            <span v-if="isLoading" class="absolute left-0 inset-y-0 flex items-center pl-3">
              <svg
                class="animate-spin h-5 w-5 text-white"
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
              >
                <circle
                  class="opacity-25"
                  cx="12"
                  cy="12"
                  r="10"
                  stroke="currentColor"
                  stroke-width="4"
                ></circle>
                <path
                  class="opacity-75"
                  fill="currentColor"
                  d="M4 12a8 8 0 018-8v8h8a8 8 0 01-16 0z"
                ></path>
              </svg>
            </span>
            Reset Password
          </button>
        </div>
      </form>
      <div class="text-center">
        <router-link to="/login" class="font-medium text-indigo-600 hover:text-indigo-500">
          Back to Login
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useRouter, useRoute } from 'vue-router'
import { toast } from 'vue-sonner'

const authStore = useAuthStore()
const router = useRouter()
const route = useRoute()

const newPassword = ref('')
const confirmPassword = ref('')
const isLoading = ref(false)
const error = ref('')
const message = ref('')

const token = route.params.token

const submit = async () => {
  if (newPassword.value !== confirmPassword.value) {
    error.value = 'Passwords do not match'
    return
  }

  isLoading.value = true
  error.value = ''
  message.value = ''

  try {
    await authStore.confirmPasswordReset(token, newPassword.value)
    message.value = 'Password reset successfully. You can now log in.'
    toast.success(message.value)
    setTimeout(() => router.push('/login'), 2000)
  } catch (err) {
    error.value = err.message || 'Failed to reset password. The link may be invalid or expired.'
  } finally {
    isLoading.value = false
  }
}
</script>
