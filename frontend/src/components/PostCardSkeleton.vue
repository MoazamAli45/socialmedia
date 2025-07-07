<template>
  <div class="card p-6 mb-4 animate-pulse">
    <!-- Post Header -->
    <div class="flex items-center justify-between mb-4">
      <div class="flex items-center space-x-3">
        <div class="h-10 w-10 rounded-full bg-gray-200"></div>
        <div>
          <div class="h-4 w-24 bg-gray-200 rounded mb-2"></div>
          <div class="h-3 w-16 bg-gray-200 rounded"></div>
        </div>
      </div>
      <div class="h-3 w-20 bg-gray-200 rounded"></div>
    </div>

    <!-- Post Content -->
    <div class="mb-4">
      <div class="h-4 w-full bg-gray-200 rounded mb-2"></div>
      <div class="h-4 w-3/4 bg-gray-200 rounded"></div>
    </div>

    <!-- Post Image Placeholder (optional, shown 50% of the time) -->
    <div class="mb-4" v-if="Math.random() > 0.5">
      <div class="w-full h-64 bg-gray-200 rounded-lg"></div>
    </div>

    <!-- Post Actions -->
    <div class="flex items-center justify-between pt-4 border-t border-gray-200">
      <div class="flex items-center space-x-6">
        <div class="h-4 w-12 bg-gray-200 rounded"></div>
        <div class="h-4 w-12 bg-gray-200 rounded"></div>
        <div class="h-4 w-12 bg-gray-200 rounded"></div>
      </div>
    </div>
  </div>
</template>

<script setup>
// No script needed for a static skeleton component
</script>

<style scoped>
.animate-pulse {
  animation: pulse 1.5s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}

@keyframes pulse {
  0%,
  100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}
</style>
