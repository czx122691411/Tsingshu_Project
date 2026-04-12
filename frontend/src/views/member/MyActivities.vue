<template>
  <div class="my-activities">
    <!-- 顶部导航 -->
    <div class="header">
      <button @click="goBack" class="back-btn">
        <el-icon><ArrowLeft /></el-icon>
      </button>
      <h1 class="title">我的活动</h1>
      <div class="placeholder"></div>
    </div>

    <!-- 活动列表 -->
    <div class="activities-container" v-loading="loading">
      <div v-if="activities.length === 0" class="empty-state">
        <el-icon :size="60" color="#ccc"><Document /></el-icon>
        <p>暂无参与活动</p>
        <el-button type="primary" @click="goToActivities">去报名</el-button>
      </div>

      <div
        v-for="activity in activities"
        :key="activity.id"
        class="activity-card"
      >
        <div class="activity-header">
          <el-tag
            :style="{
              backgroundColor: activity.activity_type_color,
              color: '#fff',
              border: 'none'
            }"
          >
            {{ activity.activity_type_name }}
          </el-tag>
        </div>

        <h3 class="activity-title">{{ activity.activity_title }}</h3>

        <div class="activity-info">
          <div class="info-row">
            <span class="label">时间：</span>
            <span>{{ formatDateTime(activity.activity_start_time) }}</span>
          </div>
          <div class="info-row">
            <span class="label">地点：</span>
            <span>{{ activity.activity_location }}</span>
          </div>
          <div class="info-row">
            <span class="label">费用：</span>
            <span class="fee">¥{{ activity.paid_amount }}</span>
          </div>
          <div class="info-row">
            <span class="label">报名时间：</span>
            <span>{{ formatDateTime(activity.registered_at) }}</span>
          </div>
        </div>

        <div class="activity-footer">
          <el-tag type="success" size="small">已报名</el-tag>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { ArrowLeft, Document } from '@element-plus/icons-vue'
import { activityApi } from '@/api/activities'

const router = useRouter()
const activities = ref([])
const loading = ref(false)

const memberInfo = ref(null)

const loadActivities = async () => {
  loading.value = true
  try {
    const info = localStorage.getItem('memberInfo')
    if (info) {
      memberInfo.value = JSON.parse(info)
      const res = await activityApi.getMemberActivities(memberInfo.value.id)
      activities.value = res.activities || []
    }
  } catch (error) {
    ElMessage.error('加载活动失败')
  } finally {
    loading.value = false
  }
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

const goBack = () => {
  router.back()
}

onMounted(() => {
  loadActivities()
})
</script>

<style scoped>
.my-activities {
  min-height: 100vh;
  background: #f5f7fa;
}

.header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #fff;
  padding: 15px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.back-btn {
  background: none;
  border: none;
  color: #fff;
  font-size: 20px;
  padding: 5px;
  cursor: pointer;
}

.title {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
}

.placeholder {
  width: 30px;
}

.activities-container {
  padding: 15px;
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.empty-state {
  background: #fff;
  border-radius: 12px;
  padding: 60px 20px;
  text-align: center;
}

.empty-state p {
  margin: 20px 0;
  color: #909399;
}

.activity-card {
  background: #fff;
  border-radius: 12px;
  padding: 15px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.activity-header {
  margin-bottom: 10px;
}

.activity-title {
  margin: 0 0 12px 0;
  font-size: 18px;
  font-weight: 600;
  color: #333;
  line-height: 1.4;
}

.activity-info {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 12px;
}

.info-row {
  display: flex;
  font-size: 14px;
}

.info-row .label {
  color: #909399;
  min-width: 70px;
}

.info-row span:not(.label) {
  color: #333;
}

.fee {
  font-weight: 600;
  color: #f56c6c;
}

.activity-footer {
  padding-top: 12px;
  border-top: 1px solid #eee;
}
</style>
