<template>
  <div class="card p-6 mb-4">
    <!-- Post Header -->
    <div class="flex items-center justify-between mb-4">
      <router-link :to="'/profile/' + postData.user.id" class="flex items-center space-x-3">
        <img
          class="h-10 w-10 rounded-full"
          :src="postData.user.profile?.profile_picture_url || '/placeholder.png'"
          :alt="postData.user.username"
          onerror="this.src='/placeholder.png'"
        />
        <div>
          <h3 class="font-semibold text-gray-900">
            {{ postData.user.first_name }} {{ postData.user.last_name }}
          </h3>
          <p class="text-sm text-gray-500">@{{ postData.user.username }}</p>
        </div>
      </router-link>
      <div class="flex items-center space-x-2">
        <span class="text-sm text-gray-500">{{ formatDate(postData.created_at) }}</span>
        <!-- Show edit/delete buttons only if user owns the post -->
        <div v-if="isOwnPost" class="flex space-x-2">
          <button
            v-if="!isEditing"
            @click="startEditing"
            class="text-sm text-gray-500 hover:text-blue-600 transition-colors"
            title="Edit post"
          >
            <PencilIcon class="h-5 w-5" />
          </button>
          <button
            @click="deletePost"
            :disabled="isDeleting"
            class="text-sm text-gray-500 hover:text-red-600 transition-colors"
            :class="{ 'opacity-50 cursor-not-allowed': isDeleting }"
            title="Delete post"
          >
            <TrashIcon class="h-5 w-5" />
          </button>
        </div>
      </div>
    </div>

    <!-- Post Content -->
    <div class="mb-4">
      <div v-if="isEditing">
        <textarea
          v-model="editedContent"
          class="w-full p-3 border border-gray-300 rounded-lg resize-none focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          rows="4"
          placeholder="Edit your post..."
        />
        <div class="flex items-center justify-between mt-2">
          <p class="text-sm text-gray-500">Press Enter to save, Escape to cancel</p>
          <div class="flex space-x-2">
            <button
              @click="cancelEditing"
              class="px-4 py-2 text-sm font-medium text-gray-600 bg-gray-200 rounded-lg hover:bg-gray-300 transition-colors"
            >
              Cancel
            </button>
            <button
              @click="updatePost"
              :disabled="!editedContent.trim() || isUpdating"
              class="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {{ isUpdating ? 'Saving...' : 'Save' }}
            </button>
          </div>
        </div>
      </div>
      <p v-else class="text-gray-800 whitespace-pre-wrap">{{ postData.content }}</p>
    </div>

    <!-- Post Image -->
    <div v-if="postData.image_url" class="mb-4">
      <img
        :src="postData.image_url"
        :alt="'Post by ' + postData.user.username"
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
          <span>{{ safeNumber(postData.like_count) }}</span>
        </button>

        <button
          @click="toggleComments"
          class="flex items-center space-x-2 text-sm font-medium text-gray-500 hover:text-blue-600 transition-colors"
        >
          <ChatBubbleLeftIcon class="h-5 w-5" />
          <span>{{ safeNumber(postData.comment_count) }}</span>
        </button>
      </div>
    </div>

    <!-- Comments Section -->
    <div v-if="showComments" class="mt-4 border-t border-gray-200">
      <!-- Comment Form -->
      <div class="pt-4">
        <div class="flex space-x-3">
          <img
            class="h-8 w-8 rounded-full"
            :src="authStore.user?.profile?.profile_picture_url || '/placeholder.png'"
            :alt="authStore.user?.username"
            onerror="this.src='/placeholder.png'"
          />
          <div class="flex-1">
            <textarea
              v-model="newComment"
              placeholder="Write a comment..."
              class="w-full p-3 border border-gray-300 rounded-lg resize-none focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              rows="2"
              @keydown.enter.exact.prevent="addComment"
              @keydown.escape="newComment = ''"
            />
            <div class="flex items-center justify-between mt-2">
              <p class="text-sm text-gray-500">Press Enter to post, Escape to cancel</p>
              <button
                @click="addComment"
                :disabled="!newComment.trim() || isCommenting"
                class="bg-blue-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                {{ isCommenting ? 'Posting...' : 'Post' }}
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Comments List -->
      <div class="mt-4">
        <div v-if="commentsStore.isLoading" class="flex justify-center py-4">
          <div class="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"></div>
        </div>

        <div v-else-if="commentsStore.comments.length > 0" class="space-y-1">
          <CommentItem
            v-for="comment in commentsStore.comments"
            :key="comment.id"
            :comment="comment"
            :post-id="post.id"
          />
        </div>

        <div v-else class="text-center py-6 text-gray-500">
          <p>No comments yet. Be the first to comment!</p>
        </div>
      </div>
    </div>

    <!-- Error Message -->
    <div v-if="error" class="mt-2 p-3 bg-red-50 border border-red-200 rounded-md">
      <p class="text-red-600 text-sm">{{ error }}</p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { HeartIcon, ChatBubbleLeftIcon, PencilIcon, TrashIcon } from '@heroicons/vue/24/outline'
import { useAuthStore } from '@/stores/auth'
import { usePostsStore } from '@/stores/posts'
import { useCommentsStore } from '@/stores/comments'
import { formatDistanceToNow } from 'date-fns'
import { toast } from 'vue-sonner'
import CommentItem from '@/components/CommentItem.vue'
import { useRouter } from 'vue-router'

const props = defineProps({
  post: {
    type: Object,
    required: true,
  },
})

const authStore = useAuthStore()
const postsStore = usePostsStore()
const commentsStore = useCommentsStore()
const router = useRouter()

const isLiking = ref(false)
const showComments = ref(false)
const newComment = ref('')
const isCommenting = ref(false)
const error = ref(null)
const isEditing = ref(false)
const editedContent = ref('')
const isUpdating = ref(false)
const isDeleting = ref(false)

// Compute post data from PostsStore to ensure reactivity
const postData = computed(() => {
  const storePost = postsStore.posts.find((p) => p.id === props.post.id)
  return storePost || props.post // Fallback to props.post if not found in store
})

// Check if the post belongs to the logged-in user
const isOwnPost = computed(() => {
  return authStore.user && authStore.user.id === postData.value.user.id
})

// Utility function to safely convert to number and handle NaN
const safeNumber = (value) => {
  const num = Number(value)
  return isNaN(num) ? 0 : num
}

const toggleLike = async () => {
  if (!authStore.user) {
    toast.error('Please log in to like posts')
    return
  }

  // Get the current state from the store's post data
  const currentPost = postData.value
  const wasLiked = currentPost.is_liked
  const originalCount = safeNumber(currentPost.like_count)

  isLiking.value = true
  error.value = null

  // Find the post in the store and update it optimistically
  const storePost = postsStore.posts.find((p) => p.id === props.post.id)
  if (storePost) {
    storePost.is_liked = !wasLiked
    storePost.like_count = wasLiked ? originalCount - 1 : originalCount + 1
  }

  try {
    const result = wasLiked
      ? await postsStore.unlikePost(props.post.id)
      : await postsStore.likePost(props.post.id)

    if (!result.success) {
      // Revert the optimistic update if the API call failed
      if (storePost) {
        storePost.is_liked = wasLiked
        storePost.like_count = originalCount
      }
      error.value = result.error || 'Failed to update like'
      toast.error(error.value)
    }
  } catch (error) {
    // Revert the optimistic update if an error occurred
    if (storePost) {
      storePost.is_liked = wasLiked
      storePost.like_count = originalCount
    }
    error.value = 'An unexpected error occurred'
    toast.error(error.value)
    console.error('Toggle like error:', error)
  } finally {
    isLiking.value = false
  }
}

const toggleComments = async () => {
  showComments.value = !showComments.value

  if (showComments.value && commentsStore.comments.length === 0) {
    await loadComments()
  }
}

const loadComments = async () => {
  try {
    const result = await commentsStore.fetchComments(props.post.id)
    if (!result.success) {
      toast.error(result.error)
    }
  } catch (error) {
    console.error('Error loading comments:', error)
    toast.error('Failed to load comments')
  }
}

const addComment = async () => {
  if (!authStore.user) {
    toast.error('Please log in to comment')
    return
  }

  if (!newComment.value.trim()) return

  try {
    isCommenting.value = true
    const result = await commentsStore.createComment(props.post.id, newComment.value.trim())

    if (result.success) {
      newComment.value = ''
      await postsStore.fetchPosts()
      toast.success('Comment added successfully')
    } else {
      toast.error(result.error)
    }
  } catch (error) {
    console.error('Error adding comment:', error)
    toast.error('Failed to add comment')
  } finally {
    isCommenting.value = false
  }
}

const startEditing = () => {
  isEditing.value = true
  editedContent.value = postData.value.content
}

const cancelEditing = () => {
  isEditing.value = false
  editedContent.value = ''
}

const updatePost = async () => {
  if (!editedContent.value.trim()) {
    toast.error('Post content cannot be empty')
    return
  }

  try {
    isUpdating.value = true
    error.value = null
    const result = await postsStore.updatePost(props.post.id, editedContent.value.trim())

    if (result.success) {
      await postsStore.fetchPosts()
      toast.success('Post updated successfully')
      isEditing.value = false
      editedContent.value = ''
    } else {
      toast.error(result.error || 'Failed to update post')
    }
  } catch (error) {
    console.error('Error updating post:', error)
    toast.error('Failed to update post')
  } finally {
    isUpdating.value = false
  }
}

const deletePost = async () => {
  if (!confirm('Are you sure you want to delete this post?')) return

  try {
    isDeleting.value = true
    error.value = null
    const result = await postsStore.deletePost(props.post.id)

    if (result.success) {
      await postsStore.fetchPosts()
      toast.success('Post deleted successfully')
    } else {
      toast.error(result.error || 'Failed to delete post')
    }
  } catch (error) {
    console.error('Error deleting post:', error)
    toast.error('Failed to delete post')
  } finally {
    isDeleting.value = false
  }
}

const formatDate = (date) => {
  return formatDistanceToNow(new Date(date), { addSuffix: true })
}
</script>

<style scoped>
@reference "tailwindcss";

.card {
  @apply bg-white rounded-lg shadow-sm border border-gray-200;
}
</style>
