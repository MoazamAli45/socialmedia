import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '@/services/api'
import { usePostsStore } from './posts'

export const useCommentsStore = defineStore('comments', () => {
  const comments = ref([])
  const isLoading = ref(false)
  const isCreating = ref(false)
  const isDeleting = ref(false)

  const fetchComments = async (postId) => {
    try {
      isLoading.value = true
      const response = await api.get(`/comments/post/${postId}`)
      comments.value = response.data
      return { success: true, data: response.data }
    } catch (error) {
      console.error('Failed to fetch comments:', error.response?.data)
      return {
        success: false,
        error: error.response?.data?.message || 'Failed to fetch comments',
      }
    } finally {
      isLoading.value = false
    }
  }

  const createComment = async (postId, content) => {
    try {
      isCreating.value = true
      const response = await api.post('/comments', {
        content,
        post: postId,
      })

      console.log('Comment created:', response.data)

      // Add the new comment to the beginning of the array
      if (!Array.isArray(comments.value)) {
        comments.value = []
      }
      comments.value.unshift(response?.data?.comment)
      // Update post's comment_count in PostsStore
      const postsStore = usePostsStore()
      const post = postsStore.posts.find((p) => p.id === postId)
      console.log('Post found in PostsStore:', post)
      if (post && response.data.post) {
        post.comment_count = response.data.post.comment_count
      }
      return { success: true, comment: response?.data?.comment || {} }
    } catch (error) {
      console.error('Failed to create comment:', error)
      return {
        success: false,
        error: error.response?.data?.message || 'Failed to create comment',
      }
    } finally {
      isCreating.value = false
    }
  }

  const updateComment = async (commentId, content) => {
    try {
      const response = await api.patch(`/comments/${commentId}`, { content })

      // Update the comment in the array
      const index = comments.value.findIndex((c) => c.id === commentId)
      if (index !== -1) {
        comments.value[index] = response.data
      }

      return { success: true, data: response.data }
    } catch (error) {
      console.error('Failed to update comment:', error)
      return {
        success: false,
        error: error.response?.data?.message || 'Failed to update comment',
      }
    }
  }

  const deleteComment = async (commentId) => {
    try {
      isDeleting.value = true
      await api.delete(`/comments/${commentId}`)

      // Remove the comment from the array
      comments.value = comments.value.filter((c) => c.id !== commentId)
      return { success: true }
    } catch (error) {
      console.error('Failed to delete comment:', error)
      return {
        success: false,
        error: error.response?.data?.message || 'Failed to delete comment',
      }
    } finally {
      isDeleting.value = false
    }
  }

  const clearComments = () => {
    comments.value = []
  }

  return {
    comments,
    isLoading,
    isCreating,
    isDeleting,
    fetchComments,
    createComment,
    updateComment,
    deleteComment,
    clearComments,
  }
})
