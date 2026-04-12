import api from './index'

export const memberApi = {
  // 获取会员列表
  getList(params) {
    return api.get('/members/', { params })
  },

  // 获取会员详情
  getDetail(id) {
    return api.get(`/members/${id}/`)
  },

  // 创建会员
  create(data) {
    return api.post('/members/', data)
  },

  // 更新会员
  update(id, data) {
    return api.put(`/members/${id}/`, data)
  },

  // 删除会员
  delete(id) {
    return api.delete(`/members/${id}/`)
  },

  // 续费
  renew(id, data) {
    return api.post(`/members/${id}/renew/`, data)
  },

  // 获取缴费流水
  getPayments(id) {
    return api.get(`/members/${id}/payments/`)
  }
}
