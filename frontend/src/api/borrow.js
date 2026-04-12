import api from './index'

export const borrowApi = {
  // 获取借阅列表
  getList(params) {
    return api.get('/borrows/', { params })
  },

  // 获取借阅详情
  getDetail(id) {
    return api.get(`/borrows/${id}/`)
  },

  // 创建借阅
  create(data) {
    return api.post('/borrows/', data)
  },

  // 更新借阅
  update(id, data) {
    return api.put(`/borrows/${id}/`, data)
  },

  // 删除借阅
  delete(id) {
    return api.delete(`/borrows/${id}/`)
  },

  // 归还
  returnBook(id, data) {
    return api.post(`/borrows/${id}/return_book/`, data)
  }
}

export const bookApi = {
  // 获取书籍列表
  getList(params) {
    return api.get('/books/', { params })
  },

  // 获取书籍详情
  getDetail(id) {
    return api.get(`/books/${id}/`)
  },

  // 创建书籍
  create(data) {
    return api.post('/books/', data)
  },

  // 更新书籍
  update(id, data) {
    return api.put(`/books/${id}/`, data)
  },

  // 删除书籍
  delete(id) {
    return api.delete(`/books/${id}/`)
  }
}

export const statsApi = {
  // 获取统计数据
  getDashboard() {
    return api.get('/stats/')
  }
}
