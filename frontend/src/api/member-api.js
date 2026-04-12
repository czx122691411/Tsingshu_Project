import axios from 'axios'
import { ElMessage } from 'element-plus'

// 会员端专用的API实例
const memberApi = axios.create({
  baseURL: '/api',
  timeout: 10000
})

// 请求拦截器
memberApi.interceptors.request.use(
  config => {
    const memberToken = localStorage.getItem('memberToken')
    if (memberToken) {
      config.headers.Authorization = `Bearer ${memberToken}`
    }
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// 响应拦截器
memberApi.interceptors.response.use(
  response => {
    return response.data
  },
  error => {
    if (error.response?.status === 401) {
      // Token过期，清除会员信息并跳转到登录页
      localStorage.removeItem('memberToken')
      localStorage.removeItem('memberRefresh')
      localStorage.removeItem('memberInfo')
      window.location.href = '/member/login'
    } else if (error.response?.data?.error) {
      ElMessage.error(error.response.data.error)
    }
    return Promise.reject(error)
  }
)

export default memberApi
