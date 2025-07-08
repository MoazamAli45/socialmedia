<template>
  <div class="flex space-x-3 py-3">
    <router-link :to="'/profile/' + comment?.user?.id">
      <img
        class="h-8 w-8 rounded-full"
        :src="comment?.user?.profile?.profile_picture_url || '/placeholder.png'"
        :alt="comment?.user?.username"
        onerror="this.src='/placeholder.png'"
      />
    </router-link>

    <div class="flex-1 min-w-0">
      <div class="bg-gray-50 rounded-lg px-3 py-2">
        <div class="flex items-center space-x-2 mb-1">
          <router-link
            :to="'/profile/' + comment?.user?.id"
            class="font-medium text-gray-900 hover:underline"
          >
            {{ comment?.user?.first_name }} {{ comment?.user?.last_name }}
          </router-link>
          <span class="text-sm text-gray-500">@{{ comment.user.username }}</span>
        </div>

        <div v-if="!isEditing">
          <p class="text-gray-800 whitespace-pre-wrap">{{ comment.content }}</p>
        </div>

        <div v-else>
          <textarea
            v-model="editContent"
            class="w-full p-2 border border-gray-300 rounded-md resize-none focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            rows="2"
            placeholder="Edit your comment..."
            @keydown.enter.exact.prevent="saveEdit"
            @keydown.escape="cancelEdit"
          />
          <div class="flex items-center space-x-2 mt-2">
            <button
              @click="saveEdit"
              :disabled="!editContent.trim() || isSaving"
              class="text-sm bg-blue-600 text-white px-3 py-1 rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {{ isSaving ? 'Saving...' : 'Save' }}
            </button>
            <button
              @click="cancelEdit"
              class="text-sm bg-gray-200 text-gray-700 px-3 py-1 rounded-md hover:bg-gray-300"
            >
              Cancel
            </button>
          </div>
        </div>
      </div>

      <div class="flex items-center space-x-4 mt-1 text-sm text-gray-500">
        <span>{{ formatDate(comment.created_at) }}</span>

        <div v-if="canEdit && !isEditing" class="flex items-center space-x-3">
          <button @click="startEdit" class="hover:text-blue-600 transition-colors">Edit</button>
          <button
            @click="deleteComment"
            :disabled="isDeleting"
            class="hover:text-red-600 transition-colors disabled:opacity-50"
          >
            {{ isDeleting ? 'Deleting...' : 'Delete' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useCommentsStore } from '@/stores/comments'
import { usePostsStore } from '@/stores/posts'
import { formatDistanceToNow } from 'date-fns'
import { toast } from 'vue-sonner'

const props = defineProps({
  comment: {
    type: Object,
    required: true,
  },
  postId: {
    type: Number,
    required: true,
  },
})

const authStore = useAuthStore()
const commentsStore = useCommentsStore()
const postsStore = usePostsStore()

const isEditing = ref(false)
const editContent = ref('')
const isSaving = ref(false)
const isDeleting = ref(false)

const canEdit = computed(() => {
  return authStore.user && authStore.user.id === props.comment.user.id
})

const startEdit = () => {
  isEditing.value = true
  editContent.value = props.comment.content
}

const cancelEdit = () => {
  isEditing.value = false
  editContent.value = ''
}

const saveEdit = async () => {
  if (!editContent.value.trim()) return

  try {
    isSaving.value = true
    const result = await commentsStore.updateComment(props.comment.id, editContent.value.trim())

    if (result.success) {
      isEditing.value = false
      toast.success('Comment updated successfully')
    } else {
      toast.error(result.error)
    }
  } catch (error) {
    console.error('Error updating comment:', error)
    toast.error('Failed to update comment')
  } finally {
    isSaving.value = false
  }
}

const deleteComment = async () => {
  if (!confirm('Are you sure you want to delete this comment?')) return

  try {
    isDeleting.value = true
    const result = await commentsStore.deleteComment(props.comment.id)

    if (result.success) {
      // Update post comment count
      postsStore.updatePostCommentCount(props.postId, -1)
      toast.success('Comment deleted successfully')
    } else {
      toast.error(result.error)
    }
  } catch (error) {
    console.error('Error deleting comment:', error)
    toast.error('Failed to delete comment')
  } finally {
    isDeleting.value = false
  }
}

const formatDate = (date) => {
  return formatDistanceToNow(new Date(date), { addSuffix: true })
}
</script>
