<template>
  <div class="min-h-screen bg-gray-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
    <div class="sm:mx-auto sm:w-full sm:max-w-md">
      <div class="text-center">
        <h2 class="text-3xl font-bold text-gray-900">Create your account</h2>
        <p class="mt-2 text-sm text-gray-600">
          Or
          <router-link to="/login" class="font-medium text-blue-600 hover:text-blue-500">
            sign in to your existing account
          </router-link>
        </p>
      </div>
    </div>

    <div class="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
      <div class="bg-white py-8 px-4 shadow sm:rounded-lg sm:px-10">
        <form class="space-y-6" @submit.prevent="handleSubmit">
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label for="first_name" class="block text-sm font-medium text-gray-700">
                First Name
              </label>
              <div class="mt-1">
                <input
                  id="first_name"
                  v-model="form.first_name"
                  type="text"
                  required
                  class="input-field"
                  :class="{ 'border-red-500': errors.first_name }"
                />
                <p v-if="errors.first_name" class="mt-1 text-sm text-red-600">
                  {{ errors.first_name }}
                </p>
              </div>
            </div>

            <div>
              <label for="last_name" class="block text-sm font-medium text-gray-700">
                Last Name
              </label>
              <div class="mt-1">
                <input
                  id="last_name"
                  v-model="form.last_name"
                  type="text"
                  required
                  class="input-field"
                  :class="{ 'border-red-500': errors.last_name }"
                />
                <p v-if="errors.last_name" class="mt-1 text-sm text-red-600">
                  {{ errors.last_name }}
                </p>
              </div>
            </div>
          </div>

          <div>
            <label for="username" class="block text-sm font-medium text-gray-700"> Username </label>
            <div class="mt-1">
              <input
                id="username"
                v-model="form.username"
                type="text"
                required
                class="input-field"
                :class="{ 'border-red-500': errors.username }"
              />
              <p v-if="errors.username" class="mt-1 text-sm text-red-600">{{ errors.username }}</p>
            </div>
          </div>

          <div>
            <label for="email" class="block text-sm font-medium text-gray-700">
              Email address
            </label>
            <div class="mt-1">
              <input
                id="email"
                v-model="form.email"
                type="email"
                required
                class="input-field"
                :class="{ 'border-red-500': errors.email }"
              />
              <p v-if="errors.email" class="mt-1 text-sm text-red-600">{{ errors.email }}</p>
            </div>
          </div>

          <div>
            <label for="password" class="block text-sm font-medium text-gray-700"> Password </label>
            <div class="mt-1">
              <input
                id="password"
                v-model="form.password"
                type="password"
                required
                class="input-field"
                :class="{ 'border-red-500': errors.password }"
              />
              <p v-if="errors.password" class="mt-1 text-sm text-red-600">{{ errors.password }}</p>
            </div>
          </div>

          <div>
            <label for="confirm_password" class="block text-sm font-medium text-gray-700">
              Confirm Password
            </label>
            <div class="mt-1">
              <input
                id="confirm_password"
                v-model="form.confirm_password"
                type="password"
                required
                class="input-field"
                :class="{ 'border-red-500': errors.confirm_password }"
              />
              <p v-if="errors.confirm_password" class="mt-1 text-sm text-red-600">
                {{ errors.confirm_password }}
              </p>
            </div>
          </div>

          <div>
            <button
              type="submit"
              :disabled="isLoading"
              class="w-full btn-primary disabled:opacity-50"
            >
              {{ isLoading ? 'Creating account...' : 'Create account' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const form = reactive({
  first_name: '',
  last_name: '',
  username: '',
  email: '',
  password: '',
  confirm_password: '',
})

const errors = ref({})
const isLoading = ref(false)

const handleSubmit = async () => {
  errors.value = {}

  // Validate passwords match
  if (form.password !== form.confirm_password) {
    errors.value.confirm_password = 'Passwords do not match'
    return
  }

  isLoading.value = true

  const result = await authStore.signup({
    first_name: form.first_name,
    last_name: form.last_name,
    username: form.username,
    email: form.email,
    password: form.password,
  })

  console.log(result, 'Signup result')

  if (result.success) {
    router.push('/')
  } else {
    errors.value = { general: result.error }
  }

  isLoading.value = false
}
</script>
