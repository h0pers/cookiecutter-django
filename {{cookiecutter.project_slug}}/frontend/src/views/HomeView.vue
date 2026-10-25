<script setup lang="ts">
import { Button } from '@/components/ui/button'
import { useCounterStore } from '@/stores/counter'

const counter = useCounterStore()
</script>

<template>
  <main class="flex min-h-screen items-center justify-center">
    <div class="space-y-4 text-center">
      <h1 class="text-4xl font-bold">Vue app</h1>
      <p class="text-muted-foreground">Count: {{ counter.count }}</p>
      <Button @click="counter.increment">Increment</Button>
    </div>
  </main>
</template>
