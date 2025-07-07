<template>
  <div class="min-h-screen bg-gray-50">
    <div class="max-w-2xl mx-auto py-8 px-4">
      <!-- Create Post -->
      <CreatePost />

      <!-- Posts Feed -->
      <div class="space-y-4">
        <!-- Show skeleton cards during initial loading -->
        <PostCardSkeleton v-if="isLoading && posts.length === 0" v-for="n in 3" :key="n" />

        <!-- Show posts -->
        <PostCard v-for="post in posts" :key="post.id" :post="post" />

        <!-- Show skeleton cards during load more -->
        <PostCardSkeleton v-if="isLoading && posts.length > 0" v-for="n in 2" :key="'more-' + n" />

        <!-- Sentinel for infinite loading -->
        <div v-if="hasMore" ref="sentinel" class="h-1"></div>

        <!-- No more posts -->
        <div v-if="!hasMore && posts.length > 0" class="text-center py-8 text-gray-500">
          No more posts to show
        </div>

        <!-- Empty state -->
        <div v-if="!isLoading && posts.length === 0" class="text-center py-12">
          <div class="text-gray-500">
            <h3 class="text-lg font-medium mb-2">No posts yet</h3>
            <p>Be the first to share something!</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, onUnmounted, ref, computed } from 'vue'
import { usePostsStore } from '@/stores/posts'
import PostCard from '@/components/PostCard.vue'
import CreatePost from '@/components/CreatePost.vue'
import PostCardSkeleton from '@/components/PostCardSkeleton.vue'

const postsStore = usePostsStore()

const posts = computed(() => postsStore.posts)
const isLoading = computed(() => postsStore.isLoading)
const hasMore = computed(() => postsStore.hasMore)

const sentinel = ref(null)
let observer = null

const loadMore = () => {
  if (hasMore.value && !isLoading.value) {
    postsStore.loadMore()
  }
}

onMounted(() => {
  // Fetch initial posts
  postsStore.fetchPosts()

  // Set up Intersection Observer for infinite loading
  observer = new IntersectionObserver(
    (entries) => {
      if (entries[0].isIntersecting && hasMore.value && !isLoading.value) {
        loadMore()
      }
    },
    { threshold: 0.1 },
  )

  if (sentinel.value) {
    observer.observe(sentinel.value)
  }
})

onUnmounted(() => {
  // Clean up observer
  if (observer && sentinel.value) {
    observer.unobserve(sentinel.value)
  }
})
</script>
