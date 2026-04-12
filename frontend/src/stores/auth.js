import { defineStore } from 'pinia'
import { ref } from 'vue'
import { authApi } from '@/api/auth'

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('access_token') || '')
  const user = ref(JSON.parse(localStorage.getItem('user') || 'null'))

  // 登录
  const login = async (credentials) => {
    const res = await authApi.login(credentials)
    token.value = res.access
    user.value = res.user
    localStorage.setItem('access_token', res.access)
    localStorage.setItem('refresh_token', res.refresh)
    localStorage.setItem('user', JSON.stringify(res.user))
  }

  // 登出
  const logout = () => {
    token.value = ''
    user.value = null
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    localStorage.removeItem('user')
  }

  // 获取用户信息
  const fetchUser = async () => {
    if (!token.value) return
    const res = await authApi.getMe()
    user.value = res
    localStorage.setItem('user', JSON.stringify(res))
  }

  // 是否为管理员
  const isAdmin = () => {
    return user.value?.role === 'admin'
  }

  return {
    token,
    user,
    login,
    logout,
    fetchUser,
    isAdmin
  }
})
