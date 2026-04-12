<template>
  <div class="member-center">
    <!-- 顶部导航 -->
    <div class="header">
      <h1 class="title">三味书屋</h1>
      <button @click="logout" class="logout-btn">退出</button>
    </div>

    <!-- 会员信息卡片 -->
    <div class="member-card">
      <div class="member-info">
        <div class="avatar">
          <el-icon :size="40"><User /></el-icon>
        </div>
        <div class="info">
          <h2 class="name">{{ memberInfo.name }}</h2>
          <p class="code">{{ memberInfo.code }}</p>
          <p class="status" :class="memberInfo.status">
            {{ statusText }}
          </p>
        </div>
      </div>
      <div class="member-stats">
        <div class="stat-item">
          <p class="label">到期时间</p>
          <p class="value">{{ formatDate(memberInfo.end_date) }}</p>
        </div>
        <div class="stat-item">
          <p class="label">参与活动</p>
          <p class="value">{{ activityCount }}次</p>
        </div>
      </div>
    </div>

    <!-- 功能菜单 -->
    <div class="menu-grid">
      <div class="menu-item" @click="goToActivities">
        <div class="menu-icon" style="background: #67c23a">
          <el-icon :size="24"><Calendar /></el-icon>
        </div>
        <span class="menu-title">活动报名</span>
        <span class="menu-desc">浏览并报名活动</span>
      </div>

      <div class="menu-item" @click="goToMyActivities">
        <div class="menu-icon" style="background: #409eff">
          <el-icon :size="24"><List /></el-icon>
        </div>
        <span class="menu-title">我的活动</span>
        <span class="menu-desc">已报名的活动</span>
      </div>
    </div>

    <!-- 最近活动 -->
    <div class="recent-activities" v-if="recentActivities.length > 0">
      <h3 class="section-title">最近参与</h3>
      <div class="activity-list">
        <div
          v-for="activity in recentActivities.slice(0, 3)"
          :key="activity.id"
          class="activity-item"
        >
          <div class="activity-info">
            <p class="activity-title">{{ activity.activity_title }}</p>
            <p class="activity-time">{{ formatDateTime(activity.activity_start_time) }}</p>
          </div>
          <el-tag size="small" type="success">已参加</el-tag>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { User, Calendar, List } from '@element-plus/icons-vue'
import { memberAuthApi } from '@/api/member-auth'

const router = useRouter()
const memberInfo = ref({})
const recentActivities = ref([])

const activityCount = computed(() => recentActivities.value.length)

const statusText = computed(() => {
  const statusMap = {
    active: '正常',
    inactive: '已过期',
    suspended: '已停用'
  }
  return statusMap[memberInfo.value.status] || '未知'
})

const loadMemberInfo = async () => {
  try {
    const info = localStorage.getItem('memberInfo')
    if (info) {
      memberInfo.value = JSON.parse(info)
      // 加载会员活动
      const activities = await memberAuthApi.getMemberActivities(memberInfo.value.id)
      recentActivities.value = activities.activities || []
    }
  } catch (error) {
    ElMessage.error('加载会员信息失败')
  }
}

const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return date.toLocaleDateString('zh-CN')
}

const formatDateTime = (dateTime) => {
  if (!dateTime) return '-'
  const date = new Date(dateTime)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const goToActivities = () => {
  router.push('/member/activities')
}

const goToMyActivities = () => {
  router.push('/member/my-activities')
}

const logout = () => {
  localStorage.removeItem('memberToken')
  localStorage.removeItem('memberRefresh')
  localStorage.removeItem('memberInfo')
  router.push('/member/login')
}

onMounted(() => {
  loadMemberInfo()
})
</script>

<style scoped>
.member-center {
  min-height: 100vh;
  background: #f5f7fa;
  padding-bottom: 20px;
}

.header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #fff;
  padding: 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.title {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
}

.logout-btn {
  background: rgba(255, 255, 255, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.3);
  color: #fff;
  padding: 8px 16px;
  border-radius: 20px;
  font-size: 14px;
  cursor: pointer;
}

.member-card {
  background: #fff;
  margin: -20px 20px 20px;
  border-radius: 16px;
  padding: 20px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.member-info {
  display: flex;
  align-items: center;
  margin-bottom: 20px;
}

.avatar {
  width: 60px;
  height: 60px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  margin-right: 15px;
}

.info {
  flex: 1;
}

.name {
  margin: 0 0 5px 0;
  font-size: 20px;
  font-weight: 600;
  color: #333;
}

.code {
  margin: 0 0 5px 0;
  font-size: 14px;
  color: #666;
}

.status {
  margin: 0;
  font-size: 12px;
  padding: 2px 8px;
  border-radius: 10px;
  display: inline-block;
}

.status.active {
  background: #67c23a;
  color: #fff;
}

.status.inactive {
  background: #909399;
  color: #fff;
}

.status.suspended {
  background: #f56c6c;
  color: #fff;
}

.member-stats {
  display: flex;
  justify-content: space-around;
  padding-top: 20px;
  border-top: 1px solid #eee;
}

.stat-item {
  text-align: center;
}

.stat-item .label {
  margin: 0 0 5px 0;
  font-size: 12px;
  color: #909399;
}

.stat-item .value {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #333;
}

.menu-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 15px;
  padding: 0 20px;
  margin-bottom: 20px;
}

.menu-item {
  background: #fff;
  border-radius: 12px;
  padding: 20px;
  text-align: center;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  cursor: pointer;
  transition: all 0.3s;
}

.menu-item:active {
  transform: scale(0.98);
}

.menu-icon {
  width: 50px;
  height: 50px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 10px;
  color: #fff;
}

.menu-title {
  display: block;
  font-size: 16px;
  font-weight: 600;
  color: #333;
  margin-bottom: 5px;
}

.menu-desc {
  display: block;
  font-size: 12px;
  color: #909399;
}

.recent-activities {
  background: #fff;
  margin: 0 20px;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.section-title {
  margin: 0 0 15px 0;
  font-size: 16px;
  font-weight: 600;
  color: #333;
}

.activity-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.activity-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px;
  background: #f5f7fa;
  border-radius: 8px;
}

.activity-info {
  flex: 1;
}

.activity-title {
  margin: 0 0 5px 0;
  font-size: 14px;
  font-weight: 500;
  color: #333;
}

.activity-time {
  margin: 0;
  font-size: 12px;
  color: #909399;
}

/* 移动端优化 */
@media (max-width: 768px) {
  .member-card {
    margin: -10px 10px 10px;
    padding: 15px;
  }

  .menu-grid {
    padding: 0 10px;
    gap: 10px;
  }

  .recent-activities {
    margin: 0 10px;
  }
}
</style>
