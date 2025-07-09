import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '@/services/api'
import { usePostsStore } from './posts'

export const useCommentsStore = defineStore('comments', () => {
  const comments = ref({}) // Store comments per postId
  const isLoading = ref({}) // Store loading state per postId
  const isCreating = ref(false)
  const isDeleting = ref(false)

  const fetchComments = async (postId) => {
    try {
      isLoading.value[postId] = true
      const response = await api.get(`/comments/post/${postId}`)
      comments.value[postId] = response.data || []
      return { success: true, data: response.data }
    } catch (error) {
      console.error('Failed to fetch comments:', error.response?.data)
      return {
        success: false,
        error: error.response?.data?.message || 'Failed to fetch comments',
      }
    } finally {
      isLoading.value[postId] = false
    }
  }

  const createComment = async (postId, content) => {
    try {
      isCreating.value = true
      const response = await api.post('/comments', {
        content,
        post: postId,
      })

      if (!comments.value[postId]) {
        comments.value[postId] = []
      }
      comments.value[postId].unshift(response?.data?.comment)

      // Update comment count in postsStore
      const postsStore = usePostsStore()
      const post = postsStore.posts.find((p) => p.id === postId)
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

  const updateComment = async (postId, commentId, content) => {
    try {
      console.log('Updating comment:', { postId, commentId, content })
      const response = await api.patch(`/comments/${commentId}`, { content, post: postId })

      const index = comments.value[postId]?.findIndex((c) => c.id === commentId)
      if (index !== -1) {
        comments.value[postId][index] = response.data
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

  const deleteComment = async (postId, commentId) => {
    try {
      isDeleting.value = true
      await api.delete(`/comments/${commentId}`)
      comments.value[postId] = comments.value[postId].filter((c) => c.id !== commentId)
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

  const clearComments = (postId) => {
    if (postId) {
      delete comments.value[postId]
    } else {
      comments.value = {}
    }
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
