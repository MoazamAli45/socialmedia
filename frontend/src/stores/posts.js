import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '@/services/api'

export const usePostsStore = defineStore('posts', () => {
  const posts = ref([])
  const isLoading = ref(false)
  const currentPage = ref(1)
  const hasMore = ref(true)

  const fetchPosts = async (page = 1) => {
    try {
      isLoading.value = true
      const response = await api.get(`/posts?page=${page}`)

      console.log('Fetched posts:', response.data)
      if (page === 1) {
        posts.value = response.data.results
      } else {
        posts.value.push(...response.data.results)
      }

      hasMore.value = !!response.data.next
      currentPage.value = page
    } catch (error) {
      console.error('Failed to fetch posts:', error)
    } finally {
      isLoading.value = false
    }
  }

  const createPost = async (postData) => {
    try {
      const formData = new FormData()
      formData.append('content', postData.content)
      if (postData.image) {
        formData.append('image', postData.image)
      }

      const response = await api.post('/posts', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      })

      posts.value.unshift(response.data)
      return { success: true }
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.message || 'Failed to create post',
      }
    }
  }

  const likePost = async (postId) => {
    try {
      const response = await api.post(`/posts/${postId}/like`)
      const post = posts.value.find((p) => p.id === postId)
      if (post) {
        post.like_count = response.data.like_count
        post.is_liked = true
      }
      return { success: true }
    } catch (error) {
      console.error('Failed to like post:', error)
      return {
        success: false,
        error: error.response?.data?.message || 'Failed to like post',
      }
    }
  }

  const unlikePost = async (postId) => {
    try {
      const response = await api.delete(`/posts/${postId}/unlike`)
      const post = posts.value.find((p) => p.id === postId)
      if (post) {
        post.like_count = response.data.like_count
        post.is_liked = false
      }
      return { success: true }
    } catch (error) {
      console.error('Failed to unlike post:', error)
      return {
        success: false,
        error: error.response?.data?.message || 'Failed to unlike post',
      }
    }
  }

  const loadMore = async () => {
    if (!hasMore.value || isLoading.value) return
    await fetchPosts(currentPage.value + 1)
  }

  return {
    posts,
    isLoading,
    hasMore,
    fetchPosts,
    createPost,
    likePost,
    unlikePost,
    loadMore,
  }
})
