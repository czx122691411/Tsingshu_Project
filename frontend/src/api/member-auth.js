import memberApi from './member-api'

export const memberAuthApi = {
  // 会员登录
  login(code, phoneLast4) {
    return memberApi.post('/members/auth/login/', {
      code,
      phone_last4: phoneLast4
    })
  },

  // 获取会员信息
  getMemberInfo(memberId) {
    return memberApi.get(`/members/${memberId}/`)
  },

  // 获取会员参与的活动
  getMemberActivities(memberId) {
    return memberApi.get(`/members/${memberId}/activities/`)
  },

  // 报名活动
  registerActivity(activityId, data) {
    return memberApi.post(`/activities/${activityId}/register/`, data)
  }
}
