  import axios from 'axios'
  import { ElMessage } from 'element-plus'
  import { useAuthStore } from '@/stores/auth'

  const api = axios.create({
    baseURL: '/api',
    timeout: 10000
  })

  // 请求拦截器
  api.interceptors.request.use(
    config => {
      const authStore = useAuthStore()
      if (authStore.token) {
        config.headers.Authorization = `Bearer ${authStore.token}`
      }
      return config
    },
    error => {
      return Promise.reject(error)
    }
  )

  // 响应拦截器
  api.interceptors.response.use(
    response => {
      return response.data
    },
    error => {
      if (error.response) {
        switch (error.response.status) {
          case 401:
            const authStore = useAuthStore()
            authStore.logout()
            ElMessage.error('登录已过期，请重新登录')
            window.location.href = '/login'
            break
          case 403:
            ElMessage.error('没有权限')
            break
          case 404:
            ElMessage.error('请求的资源不存在')
            break
          case 500:
            ElMessage.error('服务器错误')
            break
          // 400 错误不在此处处理，由组件自己处理
          default:
            if (error.response.status !== 400) {
              ElMessage.error(error.response.data?.detail || '请求失败')
            }
        }
      } else {
        ElMessage.error('网络错误')
      }
      return Promise.reject(error)
    }
  )

  export default api
