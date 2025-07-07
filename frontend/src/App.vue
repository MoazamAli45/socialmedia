<script setup>
import { RouterLink, RouterView } from 'vue-router'
import { computed } from 'vue'
import { useAuthStore } from '@/stores/auth'
import Navbar from '@/components/Navbar.vue'
import { Toaster } from 'vue-sonner'
import 'vue-sonner/style.css'

const authStore = useAuthStore()
const isAuthenticated = computed(() => authStore.isAuthenticated)
</script>

<template>
  <div id="app">
    <Navbar v-if="isAuthenticated" />
    <main :class="{ 'pt-16': isAuthenticated }">
      <Toaster richColors />
      <RouterView />
    </main>
  </div>
</template>
