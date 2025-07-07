<template>
  <div class="card p-6 mb-4">
    <!-- Post Header -->
    <div class="flex items-center justify-between mb-4">
      <router-link :to="'/profile/' + post.user.id" class="flex items-center space-x-3">
        <img
          class="h-10 w-10 rounded-full"
          :src="post.user.profile?.profile_picture_url || '/placeholder.png'"
          :alt="post.user.username"
          onerror="this.src='/placeholder.png'"
        />
        <div>
          <h3 class="font-semibold text-gray-900">
            {{ post.user.first_name }} {{ post.user.last_name }}
          </h3>
          <p class="text-sm text-gray-500">@{{ post.user.username }}</p>
        </div>
      </router-link>
      <span class="text-sm text-gray-500">{{ formatDate(post.created_at) }}</span>
    </div>

    <!-- Post Content -->
    <div class="mb-4">
      <p class="text-gray-800 whitespace-pre-wrap">{{ post.content }}</p>
    </div>

    <!-- Post Image -->
    <div v-if="post.image_url" class="mb-4">
      <img
        :src="post.image_url"
        :alt="'Post by ' + post.user.username"
        class="w-full rounded-lg max-h-96 object-cover"
      />
    </div>

    <!-- Post Actions -->
    <div class="flex items-center justify-between pt-4 border-t border-gray-200">
      <div class="flex items-center space-x-6">
        <button
          @click="toggleLike"
          :disabled="isLiking"
          :class="[
            'flex items-center space-x-2 text-sm font-medium transition-colors',
            post.is_liked ? 'text-red-600' : 'text-gray-500 hover:text-red-600',
            isLiking ? 'opacity-50 cursor-not-allowed' : '',
          ]"
        >
          <HeartIcon :class="['h-5 w-5', post.is_liked ? 'fill-current' : '']" />
          <span>{{ post.like_count }}</span>
        </button>

        <button
          class="flex items-center space-x-2 text-sm font-medium text-gray-500 hover:text-blue-600 transition-colors"
        >
          <ChatBubbleLeftIcon class="h-5 w-5" />
          <span>Comment</span>
        </button>

        <button
          class="flex items-center space-x-2 text-sm font-medium text-gray-500 hover:text-green-600 transition-colors"
        >
          <ShareIcon class="h-5 w-5" />
          <span>Share</span>
        </button>
      </div>
    </div>

    <!-- Error Message (Fallback if no toast library) -->
    <p v-if="error" class="text-red-500 text-sm mt-2">{{ error }}</p>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { HeartIcon, ChatBubbleLeftIcon, ShareIcon } from '@heroicons/vue/24/outline'
import { usePostsStore } from '@/stores/posts'
import { formatDistanceToNow } from 'date-fns'
import { toast } from 'vue-sonner'

const props = defineProps({
  post: {
    type: Object,
    required: true,
  },
})

const postsStore = usePostsStore()
const isLiking = ref(false)
const error = ref(null)

const toggleLike = async () => {
  // Store original state for rollback
  const wasLiked = props.post.is_liked
  const originalCount = props.post.like_count

  // Optimistic update
  isLiking.value = true
  error.value = null
  props.post.is_liked = !wasLiked
  props.post.like_count += wasLiked ? -1 : 1

  try {
    const result = wasLiked
      ? await postsStore.unlikePost(props.post.id)
      : await postsStore.likePost(props.post.id)

    if (!result.success) {
      // Revert optimistic update on failure
      props.post.is_liked = wasLiked
      props.post.like_count = originalCount
      error.value = result.error || 'Failed to update like'
      toast.error(error.value) // Remove if not using vue-toastification
    }
  } catch (error) {
    // Revert optimistic update on error
    props.post.is_liked = wasLiked
    props.post.like_count = originalCount
    error.value = 'An unexpected error occurred'
    toast.error(error.value)
    console.error('Toggle like error:', error)
  } finally {
    isLiking.value = false
  }
}

const formatDate = (date) => {
  return formatDistanceToNow(new Date(date), { addSuffix: true })
}
</script>
