import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const routes = [
  // 员工登录
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    meta: { requiresAuth: false }
  },
  // 会员登录
  {
    path: '/member/login',
    name: 'MemberLogin',
    component: () => import('@/views/member/MemberLogin.vue'),
    meta: { requiresAuth: false, isMember: true }
  },
  // 会员中心
  {
    path: '/member',
    name: 'MemberCenter',
    component: () => import('@/views/member/MemberCenter.vue'),
    meta: { requiresAuth: false, isMember: true }
  },
  // 会员活动浏览
  {
    path: '/member/activities',
    name: 'MemberActivities',
    component: () => import('@/views/member/MemberActivities.vue'),
    meta: { requiresAuth: false, isMember: true }
  },
  // 我的活动
  {
    path: '/member/my-activities',
    name: 'MyActivities',
    component: () => import('@/views/member/MyActivities.vue'),
    meta: { requiresAuth: false, isMember: true }
  },
  // 员工管理系统
  {
    path: '/',
    component: () => import('@/views/Layout.vue'),
    meta: { requiresAuth: true, isStaff: true },
    redirect: '/dashboard',
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('@/views/Dashboard.vue')
      },
      {
        path: 'members',
        name: 'Members',
        component: () => import('@/views/Members.vue')
      },
      {
        path: 'borrows',
        name: 'Borrows',
        component: () => import('@/views/Borrows.vue')
      },
      {
        path: 'books',
        name: 'Books',
        component: () => import('@/views/Books.vue')
      },
      // 活动管理模块路由
      {
        path: 'activities',
        name: 'Activities',
        component: () => import('@/views/activities/ActivityList.vue')
      },
      {
        path: 'activities/summary',
        name: 'ActivitySummary',
        component: () => import('@/views/activities/MemberActivitySummary.vue')
      },
      {
        path: 'activities/calendar',
        name: 'ActivityCalendar',
        component: () => import('@/views/activities/ActivityCalendar.vue')
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()
  const memberToken = localStorage.getItem('memberToken')

  // 员工系统路由守卫
  if (to.meta.isStaff) {
    if (to.meta.requiresAuth && !authStore.token) {
      next('/login')
    } else if (to.path === '/login' && authStore.token) {
      next('/')
    } else {
      next()
    }
  }
  // 会员系统路由守卫
  else if (to.meta.isMember) {
    if (to.path !== '/member/login' && !memberToken) {
      next('/member/login')
    } else if (to.path === '/member/login' && memberToken) {
      next('/member')
    } else {
      next()
    }
  }
  // 默认处理
  else {
    next()
  }
})

export default router
