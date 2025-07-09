<template>
  <div class="card p-6 mb-4 animate-pulse">
    <div
      class="flex flex-col md:flex-row items-center md:items-start space-y-4 md:space-y-0 md:space-x-8"
    >
      <!-- Profile Picture Skeleton -->
      <div class="relative">
        <div class="h-32 w-32 rounded-full bg-gray-200 animate-pulse"></div>
      </div>

      <div class="flex-1 text-center md:text-left">
        <!-- Name Skeleton -->
        <div class="h-8 bg-gray-200 rounded animate-pulse w-48 mx-auto md:mx-0 mb-2"></div>
        <div class="h-5 bg-gray-200 rounded animate-pulse w-32 mx-auto md:mx-0 mb-4"></div>

        <!-- Stats Skeleton -->
        <div class="mt-4 flex justify-center md:justify-start space-x-8">
          <div class="text-center">
            <div class="h-8 w-12 bg-gray-200 rounded animate-pulse mb-1"></div>
            <div class="h-4 w-10 bg-gray-200 rounded animate-pulse"></div>
          </div>
          <div class="text-center">
            <div class="h-8 w-12 bg-gray-200 rounded animate-pulse mb-1"></div>
            <div class="h-4 w-16 bg-gray-200 rounded animate-pulse"></div>
          </div>
          <div class="text-center">
            <div class="h-8 w-12 bg-gray-200 rounded animate-pulse mb-1"></div>
            <div class="h-4 w-16 bg-gray-200 rounded animate-pulse"></div>
          </div>
        </div>

        <!-- Bio Skeleton -->
        <div class="mt-4 space-y-2">
          <div class="h-4 bg-gray-200 rounded animate-pulse w-full"></div>
          <div class="h-4 bg-gray-200 rounded animate-pulse w-3/4"></div>
        </div>

        <!-- Additional Info Skeleton -->
        <div class="mt-4 flex flex-wrap gap-4 justify-center md:justify-start">
          <div class="h-4 bg-gray-200 rounded animate-pulse w-24"></div>
          <div class="h-4 bg-gray-200 rounded animate-pulse w-32"></div>
          <div class="h-4 bg-gray-200 rounded animate-pulse w-28"></div>
        </div>

        <!-- Button Skeleton -->
        <div class="mt-6 flex justify-center md:justify-start">
          <div class="h-10 bg-gray-200 rounded-lg animate-pulse w-32"></div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* Custom animation for smoother skeleton effect */
@keyframes pulse {
  0%,
  100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}

.animate-pulse {
  animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}
</style>
