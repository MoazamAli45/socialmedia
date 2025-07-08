<template>
  <nav
    v-if="isAuthenticated"
    class="fixed top-0 left-0 right-0 bg-white border-b border-gray-200 z-50"
  >
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="flex justify-between items-center h-16">
        <!-- Logo -->
        <div class="flex items-center">
          <router-link to="/" class="text-2xl font-bold text-blue-600"> SocialApp </router-link>
        </div>

        <!-- Search Bar (Hidden on mobile) -->
        <div class="hidden md:flex flex-1 max-w-2xl mx-8">
          <div class="relative w-full">
            <input
              type="text"
              placeholder="Search..."
              class="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-full focus:outline-none focus:ring-2 focus:ring-blue-500"
              v-model="searchQuery"
            />
            <MagnifyingGlassIcon class="absolute left-3 top-2.5 h-5 w-5 text-gray-400" />
          </div>
        </div>

        <!-- Desktop User Menu -->
        <div v-if="!isLoading" class="hidden md:flex items-center space-x-4">
          <button class="p-2 text-gray-400 hover:text-gray-600">
            <BellIcon class="h-6 w-6" />
          </button>

          <div class="relative">
            <Menu as="div" class="relative">
              <MenuButton
                class="flex items-center space-x-2 text-sm rounded-full focus:outline-none"
              >
                <img
                  class="h-8 w-8 rounded-full"
                  :src="user?.profile?.profile_picture_url || '/placeholder.png'"
                  :alt="user?.username || 'User'"
                  onerror="this.src='/placeholder.png'"
                />
                <span class="font-medium text-gray-700">{{ user?.username || 'Guest' }}</span>
              </MenuButton>

              <transition
                enter-active-class="transition ease-out duration-100"
                enter-from-class="transform opacity-0 scale-95"
                enter-to-class="transform opacity-100 scale-100"
                leave-active-class="transition ease-in duration-75"
                leave-from-class="transform opacity-100 scale-100"
                leave-to-class="transform opacity-0 scale-95"
              >
                <MenuItems
                  class="absolute right-0 mt-2 w-48 bg-white rounded-md shadow-lg py-1 focus:outline-none"
                >
                  <MenuItem v-slot="{ active }">
                    <router-link
                      :to="`/profile/${user?.id || ''}`"
                      :class="[
                        active ? 'bg-gray-100' : '',
                        'block px-4 py-2 text-sm text-gray-700',
                      ]"
                    >
                      Your Profile
                    </router-link>
                  </MenuItem>
                  <MenuItem v-slot="{ active }">
                    <router-link
                      to="/settings"
                      :class="[
                        active ? 'bg-gray-100' : '',
                        'block px-4 py-2 text-sm text-gray-700',
                      ]"
                    >
                      Settings
                    </router-link>
                  </MenuItem>
                  <MenuItem v-slot="{ active }">
                    <button
                      @click="handleLogout"
                      :class="[
                        active ? 'bg-gray-100' : '',
                        'block w-full text-left px-4 py-2 text-sm text-gray-700',
                      ]"
                    >
                      Sign out
                    </button>
                  </MenuItem>
                </MenuItems>
              </transition>
            </Menu>
          </div>
        </div>

        <!-- Mobile Menu Button -->
        <div class="md:hidden flex items-center">
          <button
            @click="toggleMobileMenu"
            class="p-2 text-gray-400 hover:text-gray-600 focus:outline-none"
          >
            <Bars3Icon v-if="!isMobileMenuOpen" class="h-6 w-6" />
            <XMarkIcon v-else class="h-6 w-6" />
          </button>
        </div>

        <!-- Loading State -->
        <div v-if="isLoading" class="hidden md:flex items-center space-x-4">
          <div class="h-8 w-8 rounded-full bg-gray-200 animate-pulse"></div>
          <div class="h-5 w-20 bg-gray-200 animate-pulse"></div>
        </div>
      </div>
    </div>

    <!-- Mobile Menu -->
    <transition
      enter-active-class="transition ease-out duration-200"
      enter-from-class="transform opacity-0 -translate-y-2"
      enter-to-class="transform opacity-100 translate-y-0"
      leave-active-class="transition ease-in duration-150"
      leave-from-class="transform opacity-100 translate-y-0"
      leave-to-class="transform opacity-0 -translate-y-2"
    >
      <div v-if="isMobileMenuOpen" class="md:hidden bg-white border-b border-gray-200">
        <div class="px-4 py-2">
          <!-- Mobile Search Bar -->
          <div class="relative mb-4">
            <input
              type="text"
              placeholder="Search..."
              class="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-full focus:outline-none focus:ring-2 focus:ring-blue-500"
              v-model="searchQuery"
            />
            <MagnifyingGlassIcon class="absolute left-3 top-2.5 h-5 w-5 text-gray-400" />
          </div>

          <!-- Mobile Menu Items -->
          <div class="space-y-1">
            <router-link
              :to="`/profile/${user?.id || ''}`"
              class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 rounded-md"
              @click="toggleMobileMenu"
            >
              Your Profile
            </router-link>
            <router-link
              to="/settings"
              class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 rounded-md"
              @click="toggleMobileMenu"
            >
              Settings
            </router-link>
            <button
              @click="handleLogout"
              class="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 rounded-md"
            >
              Sign out
            </button>
          </div>
        </div>
      </div>
    </transition>
  </nav>
  <!-- Redirect or hide nav if not authenticated -->
  <div v-else class="hidden"></div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Menu, MenuButton, MenuItems, MenuItem } from '@headlessui/vue'
import { MagnifyingGlassIcon, BellIcon, Bars3Icon, XMarkIcon } from '@heroicons/vue/24/outline'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const searchQuery = ref('')
const isMobileMenuOpen = ref(false)
const user = computed(() => authStore.user)
const isAuthenticated = computed(() => authStore.isAuthenticated)
const isLoading = computed(() => authStore.isLoading)

const toggleMobileMenu = () => {
  isMobileMenuOpen.value = !isMobileMenuOpen.value
}

console.log('Auth Store:', authStore, 'USER', user.value)

// Fetch user data on mount if authenticated
onMounted(async () => {
  if (isAuthenticated.value && !user.value) {
    const storedUserId = localStorage.getItem('userId')
    if (storedUserId) {
      await authStore.fetchUser(storedUserId)
    } else {
      console.warn('No userId found in localStorage, logging out')
      authStore.logout()
      router.push('/login')
    }
  }
})

const handleLogout = () => {
  authStore.logout()
  router.push('/login')
  isMobileMenuOpen.value = false
}
</script>
