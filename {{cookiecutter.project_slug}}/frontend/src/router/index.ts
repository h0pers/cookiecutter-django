import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  // Django serves the app shell for every URL under /app/
  history: createWebHistory('/app/'),
  routes: [
    {
      path: '/',
      name: 'home',
      component: () => import('@/views/HomeView.vue'),
    },
  ],
})

export default router
