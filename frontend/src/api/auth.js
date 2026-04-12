import api from './index'

export const authApi = {
  // 登录
  login(data) {
    return api.post('/auth/login/', data)
  },

  // 获取当前用户信息
  getMe() {
    return api.get('/auth/me/')
  },

  // 登出
  logout() {
    return api.post('/auth/logout/')
  },

  // 注册
  register(data) {
    return api.post('/auth/register/', data)
  }
}
