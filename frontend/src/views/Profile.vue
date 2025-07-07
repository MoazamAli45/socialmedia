<template>
  <div class="min-h-screen bg-gray-50">
    <div class="max-w-4xl mx-auto py-8 px-4">
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
            <button
              v-if="isOwnProfile"
              class="absolute bottom-0 right-0 bg-blue-600 text-white rounded-full p-2 hover:bg-blue-700"
              @click="showImageUpload = true"
            >
              <CameraIcon class="h-4 w-4" />
            </button>
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
              <div class="mt-2 flex flex-wrap gap-4 text-sm text-gray-600">
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
              <button v-if="isOwnProfile" @click="$router.push('/settings')" class="btn-secondary">
                Edit Profile
              </button>
              <button
                v-else
                @click="toggleFollow"
                :class="[
                  'px-6 py-2 rounded-lg font-medium transition-colors',
                  isFollowing
                    ? 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                    : 'bg-blue-600 text-white hover:bg-blue-700',
                ]"
              >
                {{ isFollowing ? 'Unfollow' : 'Follow' }}
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Profile Posts -->
      <div class="space-y-4">
        <h2 class="text-xl font-bold text-gray-900">Posts</h2>
        <div v-if="isLoading" class="flex justify-center py-12">
          <Loading />
        </div>
        <div v-else-if="userPosts.length > 0" class="space-y-4">
          <PostCard v-for="post in userPosts" :key="post.id" :post="post" />
        </div>

        <div v-else class="text-center py-12">
          <div class="text-gray-500">
            <h3 class="text-lg font-medium mb-2">No posts yet</h3>
            <p v-if="isOwnProfile">Share your first post!</p>
            <p v-else>This user hasn't posted anything yet.</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Image Upload Modal -->
    <div
      v-if="showImageUpload"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
    >
      <div class="bg-white rounded-lg p-6 max-w-md w-full mx-4">
        <h3 class="text-lg font-semibold mb-4">Update Profile Picture</h3>
        <input type="file" accept="image/*" @change="handleImageUpload" class="mb-4" />
        <div class="flex justify-end space-x-4">
          <button @click="showImageUpload = false" class="btn-secondary">Cancel</button>
          <button @click="uploadImage" class="btn-primary">Upload</button>
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
import api from '@/services/api'
import { format } from 'date-fns'
import Loading from '@/components/Loading.vue'

const route = useRoute()
const authStore = useAuthStore()

const profileData = ref(null)
const userPosts = ref([])
const postCount = ref(0)
const followerCount = ref(0)
const followingCount = ref(0)
const isFollowing = ref(false)
const showImageUpload = ref(false)
const selectedImage = ref(null)
const isLoading = ref(false)

const isOwnProfile = computed(() => {
  const profileId = route.params.id
  return !profileId || profileId == authStore.user?.id
})
const fetchProfileData = async () => {
  try {
    isLoading.value = true

    const userId = route.params.id || authStore.user?.id
    console.log('Fetching profile for user ID:', userId)
    const [profileRes, postsRes, followersRes, followingRes] = await Promise.all([
      api.get(`/users/profile?user=${userId}`),
      api.get(`/users/my_posts`),
      api.get('/follows/followers'),
      api.get('/follows/following'),
    ])
    profileData.value = profileRes.data
    userPosts.value = postsRes.data
    postCount.value = postsRes.data.length
    followerCount.value = followersRes.data.length
    followingCount.value = followingRes.data.length

    console.log(
      'Profile data:',
      profileData.value,
      'User posts:',
      userPosts.value,
      'Follower count:',
      followerCount.value,
      'Following count:',
      followingCount.value,
    )
    if (!isOwnProfile.value) {
      isFollowing.value = followingRes.data.some((follow) => follow.followed === Number(userId))
    }
  } catch (error) {
    console.error('Failed to fetch profile data:', error)
  } finally {
    isLoading.value = false
  }
}
const toggleFollow = async () => {
  try {
    if (isFollowing.value) {
      // Unfollow
      const followingResponse = await api.get('/follows/following')
      const followRecord = followingResponse.data.find(
        (follow) => follow.followed === Number(route.params.id),
      )
      if (followRecord) {
        await api.delete(`/follows/${followRecord.id}`)
        isFollowing.value = false
        followerCount.value--
      }
    } else {
      // Follow
      await api.post('/follows', { followed: route.params.id })
      isFollowing.value = true
      followerCount.value++
    }
  } catch (error) {
    console.error('Failed to toggle follow:', error)
  }
}

const handleImageUpload = (event) => {
  selectedImage.value = event.target.files[0]
}

const uploadImage = async () => {
  if (!selectedImage.value) return

  try {
    const formData = new FormData()
    formData.append('profile_picture', selectedImage.value)

    await api.patch(`/users/profile`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })

    showImageUpload.value = false
    selectedImage.value = null
    await fetchProfileData()
  } catch (error) {
    console.error('Failed to upload image:', error)
  }
}

const formatDate = (date) => {
  return format(new Date(date), 'MMMM d, yyyy')
}

onMounted(fetchProfileData)
</script>
