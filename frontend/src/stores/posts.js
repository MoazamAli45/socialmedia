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

  const fetchUserPosts = async (userId) => {
    isLoading.value = true
    try {
      const response = await api.get(`/users/my_posts?user=${userId}`)
      posts.value = response.data // Replace or append based on your needs
      hasMore.value = false // Adjust if pagination is needed
      return { success: true, data: response.data }
    } catch (error) {
      console.error('Error fetching user posts:', error)
      return { success: false, error: 'Failed to fetch user posts' }
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

  const updatePost = async (postId, updatedContent) => {
    try {
      const res = await api.patch(`/posts/${postId}`, { content: updatedContent })
      const post = posts.value.find((p) => p.id === postId)
      if (post) {
        post.content = res.data.content
      }
      return { success: true }
    } catch (error) {
      console.error('Failed to update Post', error)
      return {
        success: false,
        error: error.response?.data?.message || 'Failed to update post',
      }
    }
  }

  const deletePost = async (postId) => {
    try {
      await api.delete(`/posts/${postId}`)
      posts.value = posts.value.filter((p) => p.id !== postId)
      return { success: true }
    } catch (error) {
      console.error('Failed to delete Post', error)
      return {
        success: false,
        error: error.response?.data?.message || 'Failed to delete post',
      }
    }
  }
  const likePost = async (postId) => {
    try {
      const response = await api.post(`/posts/${postId}/like`)
      const post = posts.value.find((p) => p.id === postId)
      if (post) {
        // Only update the server response data, don't increment count
        // since optimistic UI already handled it
        const serverLikeCount = Number(response.data.like_count)
        if (!isNaN(serverLikeCount)) {
          post.like_count = serverLikeCount
        }
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
        // Only update the server response data, don't decrement count
        // since optimistic UI already handled it
        const serverLikeCount = Number(response.data.like_count)
        if (!isNaN(serverLikeCount)) {
          post.like_count = serverLikeCount
        }
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
  const updatePostCommentCount = (postId, increment = 1) => {
    const post = posts.value.find((p) => p.id === postId)
    if (post) {
      // Ensure comment_count is a number and handle potential NaN
      const currentCount = Number(post.comment_count) || 0
      post.comment_count = Math.max(currentCount + increment, 0)
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
    fetchUserPosts,
    createPost,
    likePost,
    unlikePost,
    updatePostCommentCount,
    updatePost,
    loadMore,
    deletePost,
  }
})
