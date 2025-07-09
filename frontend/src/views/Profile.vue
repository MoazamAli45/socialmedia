<template>
  <div class="min-h-screen bg-gray-50">
    <div class="max-w-4xl mx-auto py-8 px-4">
      <!-- Loading State -->
      <div v-if="isLoading">
        <ProfileSkeleton />
        <PostCardSkeleton v-for="i in 3" :key="i" />
      </div>

      <!-- Loaded State -->
      <div v-else>
        <!-- Profile Header -->
        <div class="card p-8 mb-8">
          <div
            class="flex flex-col md:flex-row items-center md:items-start space-y-4 md:space-y-0 md:space-x-8"
          >
            <div class="relative">
              <img
                class="h-32 w-32 rounded-full object-cover"
                :src="profileData?.profile?.profile_picture_url || '/placeholder.png'"
                :alt="profileData?.username"
                onerror="this.src='/placeholder.png'"
              />
            </div>

            <div class="flex-1 text-center md:text-left">
              <h1 class="text-3xl font-bold text-gray-900">
                {{ profileData?.first_name }} {{ profileData?.last_name }}
              </h1>
              <p class="text-gray-600">@{{ profileData?.username }}</p>

              <div class="mt-4 flex justify-center md:justify-start space-x-8">
                <div class="text-center">
                  <div class="text-2xl font-bold text-gray-900">{{ postCount }}</div>
                  <div class="text-sm text-gray-600">Posts</div>
                </div>
                <div class="text-center">
                  <div class="text-2xl font-bold text-gray-900">{{ followerCount }}</div>
                  <div class="text-sm text-gray-600">Followers</div>
                </div>
                <div class="text-center">
                  <div class="text-2xl font-bold text-gray-900">{{ followingCount }}</div>
                  <div class="text-sm text-gray-600">Following</div>
                </div>
              </div>

              <div class="mt-4">
                <p class="text-gray-700">{{ profileData?.profile?.bio }}</p>
                <div
                  class="mt-2 flex flex-wrap gap-4 text-sm text-gray-600 justify-center md:justify-start"
                >
                  <div v-if="profileData?.profile?.location" class="flex items-center">
                    <MapPinIcon class="h-4 w-4 mr-1" />
                    {{ profileData.profile.location }}
                  </div>
                  <div v-if="profileData?.profile?.website" class="flex items-center">
                    <LinkIcon class="h-4 w-4 mr-1" />
                    <a
                      :href="profileData.profile.website"
                      target="_blank"
                      class="text-blue-600 hover:underline"
                    >
                      {{ profileData.profile.website }}
                    </a>
                  </div>
                  <div v-if="profileData?.profile?.birth_date" class="flex items-center">
                    <CalendarIcon class="h-4 w-4 mr-1" />
                    Born {{ formatDate(profileData.profile.birth_date) }}
                  </div>
                </div>
              </div>

              <div class="mt-6 flex justify-center md:justify-start space-x-4">
                <button
                  v-if="isOwnProfile"
                  @click="$router.push('/settings')"
                  class="btn-secondary"
                >
                  Edit Profile
                </button>
                <button
                  v-else
                  @click="toggleFollow"
                  :disabled="isFollowLoading"
                  :class="[
                    'px-6 py-2 rounded-lg font-medium transition-colors disabled:opacity-50',
                    isFollowing
                      ? 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                      : 'bg-blue-600 text-white hover:bg-blue-700',
                  ]"
                >
                  <span v-if="isFollowLoading">
                    <svg
                      class="animate-spin -ml-1 mr-3 h-5 w-5 text-current inline"
                      xmlns="http://www.w3.org/2000/svg"
                      fill="none"
                      viewBox="0 0 24 24"
                    >
                      <circle
                        class="opacity-25"
                        cx="12"
                        cy="12"
                        r="10"
                        stroke="currentColor"
                        stroke-width="4"
                      ></circle>
                      <path
                        class="opacity-75"
                        fill="currentColor"
                        d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                      ></path>
                    </svg>
                  </span>
                  {{ isFollowing ? 'Unfollow' : 'Follow' }}
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- Profile Posts -->
        <div class="space-y-4">
          <h2 class="text-xl font-bold text-gray-900">Posts</h2>

          <!-- Posts Loaded State -->
          <div v-if="userPosts.length > 0" class="space-y-4">
            <PostCard v-for="post in userPosts" :key="post.id" :post="post" />
          </div>

          <!-- No Posts State -->
          <div v-else class="text-center py-12">
            <div class="text-gray-500">
              <h3 class="text-lg font-medium mb-2">No posts yet</h3>
              <p v-if="isOwnProfile">Share your first post!</p>
              <p v-else>This user hasn't posted anything yet.</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { CameraIcon, MapPinIcon, LinkIcon, CalendarIcon } from '@heroicons/vue/24/outline'
import { useAuthStore } from '@/stores/auth'
import PostCard from '@/components/PostCard.vue'
import ProfileSkeleton from '@/components/ProfileSkeleton.vue'
import api from '@/services/api'
import { format } from 'date-fns'
import { toast } from 'vue-sonner'
import PostCardSkeleton from '@/components/PostCardSkeleton.vue'
import { usePostsStore } from '@/stores/posts'

const route = useRoute()
const authStore = useAuthStore()

const profileData = ref(null)
const postCount = ref(0)
const followerCount = ref(0)
const followingCount = ref(0)
const isFollowing = ref(false)
const isLoading = ref(false)
const isFollowLoading = ref(false)

// FOR POSTS
const postsStore = usePostsStore()

// Use computed for userPosts to reactively get posts from store
const userPosts = computed(() => postsStore.posts || [])

const isOwnProfile = computed(() => {
  const profileId = route.params.id
  return !profileId || profileId == authStore.user?.id
})

const fetchProfileData = async () => {
  try {
    isLoading.value = true
    const userId = route.params.id || authStore.user?.id
    console.log('Fetching profile for user ID:', userId)

    const [profileRes, followersRes, followingRes] = await Promise.all([
      api.get(`/users/profile?user=${userId}`),
      api.get(`/follows/followers?user=${userId}`),
      api.get(`/follows/following?user=${userId}`),
    ])

    profileData.value = profileRes.data
    followerCount.value = followersRes.data.length || 0
    followingCount.value = followingRes.data.length || 0

    // Fetch user posts using postsStore
    await postsStore.fetchUserPosts(userId)
    postCount.value = userPosts.value.length

    if (!isOwnProfile.value) {
      const myFollowingRes = await api.get('/follows/following')
      isFollowing.value = myFollowingRes.data.some(
        (follow) => follow.followed.id === Number(userId),
      )
    }
  } catch (error) {
    console.error('Failed to fetch profile data:', error)
    toast.error('Failed to load profile')
  } finally {
    isLoading.value = false
  }
}

const toggleFollow = async () => {
  try {
    isFollowLoading.value = true
    const userId = route.params.id

    if (isFollowing.value) {
      // Unfollow
      await api.delete('/follows/unfollow', { data: { followed: userId } })
      isFollowing.value = false

      await fetchProfileData() // Refresh profile data to update counts
    } else {
      // Follow
      await api.post('/follows', { followed_id: userId })
      isFollowing.value = true

      await fetchProfileData() // Refresh profile data to update counts
    }

    toast.success(isFollowing.value ? 'Followed user successfully' : 'Unfollowed user successfully')
  } catch (error) {
    console.error('Failed to toggle follow:', error)
    toast.error(isFollowing.value ? 'Failed to unfollow user' : 'Failed to follow user')
  } finally {
    isFollowLoading.value = false
  }
}

const formatDate = (date) => {
  return format(new Date(date), 'MMMM d, yyyy')
}

onMounted(fetchProfileData)
</script>

<style scoped>
@reference "tailwindcss";
.card {
  @apply bg-white rounded-lg shadow-sm border border-gray-200;
}

.btn-primary {
  @apply bg-blue-600 text-white px-6 py-2 rounded-lg font-medium hover:bg-blue-700 transition-colors disabled:opacity-50;
}

.btn-secondary {
  @apply bg-gray-200 text-gray-700 px-6 py-2 rounded-lg font-medium hover:bg-gray-300 transition-colors;
}
</style>
