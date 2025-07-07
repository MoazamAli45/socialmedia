<template>
  <div class="card p-6 mb-6">
    <div class="flex items-start space-x-4">
      <img
        class="h-10 w-10 rounded-full"
        :src="user?.profile?.profile_picture_url || '/placeholder.png'"
        :alt="user?.username"
        onerror="this.src='/placeholder.png'"
      />
      <div class="flex-1">
        <textarea
          v-model="content"
          placeholder="What's on your mind?"
          class="w-full p-3 border border-gray-300 rounded-lg resize-none focus:outline-none focus:ring-2 focus:ring-blue-500"
          rows="3"
        ></textarea>

        <div v-if="selectedImage" class="mt-4 relative">
          <img
            :src="imagePreview"
            alt="Selected image"
            class="w-full max-h-64 object-cover rounded-lg"
          />
          <button
            @click="removeImage"
            class="absolute top-2 right-2 bg-red-500 text-white rounded-full p-1 hover:bg-red-600"
          >
            <XMarkIcon class="h-4 w-4" />
          </button>
        </div>

        <div class="flex items-center justify-between mt-4">
          <div class="flex items-center space-x-4">
            <label
              class="flex items-center space-x-2 text-gray-500 hover:text-blue-600 cursor-pointer"
            >
              <PhotoIcon class="h-5 w-5" />
              <span>Photo</span>
              <input type="file" accept="image/*" @change="handleImageSelect" class="hidden" />
            </label>
          </div>

          <button
            @click="handleSubmit"
            :disabled="!content.trim() || isLoading"
            class="btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {{ isLoading ? 'Posting...' : 'Post' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { PhotoIcon, XMarkIcon } from '@heroicons/vue/24/outline'
import { useAuthStore } from '@/stores/auth'
import { usePostsStore } from '@/stores/posts'

const authStore = useAuthStore()
const postsStore = usePostsStore()

const content = ref('')
const selectedImage = ref(null)
const imagePreview = ref(null)
const isLoading = ref(false)

const user = computed(() => authStore.user)

const handleImageSelect = (event) => {
  const file = event.target.files[0]
  if (file) {
    selectedImage.value = file
    const reader = new FileReader()
    reader.onload = (e) => {
      imagePreview.value = e.target.result
    }
    reader.readAsDataURL(file)
  }
}

const removeImage = () => {
  selectedImage.value = null
  imagePreview.value = null
}

const handleSubmit = async () => {
  if (!content.value.trim()) return

  isLoading.value = true

  const result = await postsStore.createPost({
    content: content.value,
    image: selectedImage.value,
  })

  if (result.success) {
    content.value = ''
    selectedImage.value = null
    imagePreview.value = null
  }

  isLoading.value = false
}
</script>
