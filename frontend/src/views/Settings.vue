<template>
  <div class="min-h-screen bg-gray-50">
    <div class="max-w-2xl mx-auto py-8 px-4">
      <div class="card p-8">
        <h1 class="text-2xl font-bold text-gray-900 mb-8">Settings</h1>

        <form @submit.prevent="handleSubmit" class="space-y-6">
          <!-- Profile Picture -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2"> Profile Picture </label>
            <div class="flex items-center space-x-4">
              <img
                class="h-16 w-16 rounded-full object-cover"
                :src="form.profile_picture_url || '/placeholder.png'"
                :alt="user?.username"
                onerror="this.src='/placeholder.png'"
              />
              <div>
                <input
                  type="file"
                  accept="image/*"
                  @change="handleImageSelect"
                  class="hidden"
                  ref="imageInput"
                />
                <button type="button" @click="$refs.imageInput.click()" class="btn-secondary">
                  Change Picture
                </button>
              </div>
            </div>
          </div>

          <!-- Personal Information -->
          <div v-if="authStore.isLoading" class="flex justify-center py-12">
            <Loading />
          </div>
          <div v-else class="grid grid-cols-2 gap-4">
            <div>
              <label for="first_name" class="block text-sm font-medium text-gray-700">
                First Name
              </label>
              <input
                id="first_name"
                v-model="form.first_name"
                type="text"
                class="mt-1 input-field"
              />
            </div>
            <div>
              <label for="last_name" class="block text-sm font-medium text-gray-700">
                Last Name
              </label>
              <input id="last_name" v-model="form.last_name" type="text" class="mt-1 input-field" />
            </div>
          </div>

          <div>
            <label for="email" class="block text-sm font-medium text-gray-700"> Email </label>
            <input id="email" v-model="form.email" type="email" class="mt-1 input-field" />
          </div>

          <div>
            <label for="bio" class="block text-sm font-medium text-gray-700"> Bio </label>
            <textarea
              id="bio"
              v-model="form.bio"
              rows="3"
              class="mt-1 input-field"
              placeholder="Tell us about yourself..."
            ></textarea>
          </div>

          <div>
            <label for="location" class="block text-sm font-medium text-gray-700"> Location </label>
            <input
              id="location"
              v-model="form.location"
              type="text"
              class="mt-1 input-field"
              placeholder="City, Country"
            />
          </div>

          <div>
            <label for="website" class="block text-sm font-medium text-gray-700"> Website </label>
            <input
              id="website"
              v-model="form.website"
              type="url"
              class="mt-1 input-field"
              placeholder="https://yourwebsite.com"
            />
          </div>

          <div>
            <label for="birth_date" class="block text-sm font-medium text-gray-700">
              Birth Date
            </label>
            <input id="birth_date" v-model="form.birth_date" type="date" class="mt-1 input-field" />
          </div>

          <div class="flex justify-end space-x-4">
            <button type="button" @click="$router.push('/')" class="btn-secondary">Cancel</button>
            <button type="submit" :disabled="isLoading" class="btn-primary disabled:opacity-50">
              {{ isLoading ? 'Saving...' : 'Save Changes' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import api from '@/services/api'

const router = useRouter()
const authStore = useAuthStore()

console.log('Auth Store:', authStore)

const user = computed(() => authStore.user)
const isLoading = ref(false)
const selectedImage = ref(null)

const form = reactive({
  first_name: '',
  last_name: '',
  email: '',
  bio: '',
  location: '',
  website: '',
  birth_date: '',
  profile_picture_url: '',
})

const handleImageSelect = (event) => {
  const file = event.target.files[0]
  if (file) {
    selectedImage.value = file
    // Create preview URL
    const reader = new FileReader()
    reader.onload = (e) => {
      form.profile_picture_url = e.target.result
    }
    reader.readAsDataURL(file)
  }
}

const handleSubmit = async () => {
  isLoading.value = true

  try {
    const formData = new FormData()

    // Add basic fields
    formData.append('first_name', form.first_name)
    formData.append('last_name', form.last_name)
    formData.append('email', form.email)
    formData.append('bio', form.bio)
    formData.append('location', form.location)
    formData.append('website', form.website)
    formData.append('birth_date', form.birth_date)

    // Add image if selected
    if (selectedImage.value) {
      formData.append('profile_picture', selectedImage.value)
    }

    await api.patch(`/users/update_profile`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })

    // Refresh user data
    await authStore.fetchUser(user?.value.id)

    // Redirect to profile page
    router.push(`/profile/${user.value.id}`)
    console.log('Profile updated successfully')
  } catch (error) {
    console.error('Failed to update profile:', error)
  } finally {
    isLoading.value = false
  }
}

onMounted(() => {
  if (user.value) {
    form.first_name = user.value.first_name || ''
    form.last_name = user.value.last_name || ''
    form.email = user.value.email || ''
    form.bio = user.value.profile?.bio || ''
    form.location = user.value.profile?.location || ''
    form.website = user.value.profile?.website || ''
    form.birth_date = user.value.profile?.birth_date || ''
    form.profile_picture_url = user.value.profile?.profile_picture_url || ''
  }
})
</script>
