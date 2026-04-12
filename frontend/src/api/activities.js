import api from './index'

export const activityApi = {
  // 获取活动列表
  getList(params) {
    return api.get('/activities/', { params })
  },

  // 获取活动详情
  getDetail(id) {
    return api.get(`/activities/${id}/`)
  },

  // 创建活动（仅管理员）
  create(data) {
    return api.post('/activities/', data)
  },

  // 更新活动（仅管理员）
  update(id, data) {
    return api.put(`/activities/${id}/`, data)
  },

  // 删除活动（仅管理员）
  delete(id) {
    return api.delete(`/activities/${id}/`)
  },

  // 报名活动
  register(id, data) {
    return api.post(`/activities/${id}/register/`, data)
  },

  // 取消报名
  unregister(id) {
    return api.post(`/activities/${id}/unregister/`)
  },

  // 获取活动日历数据
  getCalendar(params) {
    return api.get('/activities/calendar/', { params })
  },

  // 获取活动统计摘要
  getSummary() {
    return api.get('/activities/summary/')
  },

  // 获取会员活动统计汇总
  getMemberActivitySummary(params) {
    return api.get('/activity-stats/', { params })
  },

  // 获取指定会员参与的活动列表
  getMemberActivities(memberId) {
    return api.get(`/members/${memberId}/activities/`)
  },

  // ========== 活动类型管理 ==========

  // 获取活动类型列表
  getTypes(params) {
    return api.get('/activity-types/', { params })
  },

  // 获取活动类型详情
  getTypeDetail(id) {
    return api.get(`/activity-types/${id}/`)
  },

  // 创建活动类型（仅管理员）
  createType(data) {
    return api.post('/activity-types/', data)
  },

  // 更新活动类型（仅管理员）
  updateType(id, data) {
    return api.put(`/activity-types/${id}/`, data)
  },

  // 删除活动类型（仅管理员）
  deleteType(id) {
    return api.delete(`/activity-types/${id}/`)
  }
}
