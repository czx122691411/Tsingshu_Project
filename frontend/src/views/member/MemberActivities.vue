<template>
  <div class="member-activities">
    <!-- 顶部导航 -->
    <div class="header">
      <button @click="goBack" class="back-btn">
        <el-icon><ArrowLeft /></el-icon>
      </button>
      <h1 class="title">活动报名</h1>
      <div class="placeholder"></div>
    </div>

    <!-- 活动列表 -->
    <div class="activities-container">
      <div
        v-for="activity in activities"
        :key="activity.id"
        class="activity-card"
        @click="showActivityDetail(activity)"
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
          <el-tag :type="getStatusType(activity.status)" size="small">
            {{ activity.status_display }}
          </el-tag>
        </div>

        <h3 class="activity-title">{{ activity.title }}</h3>

        <div class="activity-info">
          <div class="info-item">
            <el-icon><Location /></el-icon>
            <span>{{ activity.location }}</span>
          </div>
          <div class="info-item">
            <el-icon><Clock /></el-icon>
            <span>{{ formatDateTime(activity.start_time) }}</span>
          </div>
          <div class="info-item">
            <el-icon><Money /></el-icon>
            <span>¥{{ activity.fee }}</span>
          </div>
        </div>

        <div class="activity-footer">
          <span class="registered-count">已报名 {{ activity.registered_count }}人</span>
          <el-button
            v-if="!activity.is_finished && !isRegistered(activity.id)"
            type="primary"
            size="small"
            @click.stop="handleRegister(activity)"
          >
            立即报名
          </el-button>
          <el-button
            v-else-if="isRegistered(activity.id)"
            type="success"
            size="small"
            disabled
          >
            已报名
          </el-button>
        </div>
      </div>
    </div>

    <!-- 活动详情对话框 -->
    <el-dialog
      v-model="detailVisible"
      :title="currentActivity.title"
      width="90%"
      :style="{ maxWidth: '500px' }"
    >
      <div class="detail-content">
        <div class="detail-row">
          <span class="label">活动类型：</span>
          <el-tag
            :style="{
              backgroundColor: currentActivity.activity_type_color,
              color: '#fff',
              border: 'none'
            }"
          >
            {{ currentActivity.activity_type_name }}
          </el-tag>
        </div>

        <div class="detail-row">
          <span class="label">活动时间：</span>
          <span>{{ formatDateTime(currentActivity.start_time) }}</span>
        </div>

        <div class="detail-row">
          <span class="label">活动地点：</span>
          <span>{{ currentActivity.location }}</span>
        </div>

        <div class="detail-row">
          <span class="label">活动费用：</span>
          <span class="fee">¥{{ currentActivity.fee }}</span>
        </div>

        <div class="detail-row" v-if="currentActivity.description">
          <span class="label">活动描述：</span>
        </div>
        <p class="description">{{ currentActivity.description }}</p>

        <div class="detail-row">
          <span class="label">已报名人数：</span>
          <span>{{ currentActivity.registered_count }}人</span>
        </div>
      </div>

      <template #footer>
        <el-button @click="detailVisible = false">关闭</el-button>
        <el-button
          v-if="!currentActivity.is_finished && !isRegistered(currentActivity.id)"
          type="primary"
          @click="handleRegister(currentActivity)"
          :loading="registering"
        >
          确认报名
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { ArrowLeft, Location, Clock, Money } from '@element-plus/icons-vue'
import { activityApi } from '@/api/activities'
import { memberAuthApi } from '@/api/member-auth'

const router = useRouter()
const activities = ref([])
const registeredActivityIds = ref([])
const detailVisible = ref(false)
const currentActivity = ref({})
const registering = ref(false)

const memberInfo = ref(null)

const loadActivities = async () => {
  try {
    const info = localStorage.getItem('memberInfo')
    if (info) {
      memberInfo.value = JSON.parse(info)
      // 加载活动列表
      const res = await activityApi.getList()
      activities.value = res.results || res

      // 加载已报名的活动
      const myActivities = await activityApi.getMemberActivities(memberInfo.value.id)
      registeredActivityIds.value = (myActivities.activities || []).map(a => a.activity)
    }
  } catch (error) {
    ElMessage.error('加载活动失败')
  }
}

const isRegistered = (activityId) => {
  return registeredActivityIds.value.includes(activityId)
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

const getStatusType = (status) => {
  const types = { upcoming: 'info', ongoing: 'warning', finished: 'info' }
  return types[status] || 'info'
}

const showActivityDetail = (activity) => {
  currentActivity.value = activity
  detailVisible.value = true
}

const handleRegister = async (activity) => {
  try {
    await ElMessageBox.confirm(
      `确认报名《${activity.title}》吗？费用：¥${activity.fee}`,
      '报名确认',
      {
        confirmButtonText: '确认报名',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    registering.value = true
    try {
      // 使用会员自己的ID进行报名
      await memberAuthApi.registerActivity(activity.id, {
        member_id: memberInfo.value.id,
        note: ''
      })

      ElMessage.success('报名成功')
      detailVisible.value = false
      registeredActivityIds.value.push(activity.id)
      loadActivities() // 重新加载数据
    } catch (error) {
      ElMessage.error(error.response?.data?.error || '报名失败')
    } finally {
      registering.value = false
    }
  } catch {
    // 用户取消
  }
}

const goBack = () => {
  router.back()
}

onMounted(() => {
  loadActivities()
})
</script>

<style scoped>
.member-activities {
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

.activity-card {
  background: #fff;
  border-radius: 12px;
  padding: 15px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  cursor: pointer;
  transition: all 0.3s;
}

.activity-card:active {
  transform: scale(0.98);
}

.activity-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
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

.info-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 14px;
  color: #666;
}

.activity-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 12px;
  border-top: 1px solid #eee;
}

.registered-count {
  font-size: 12px;
  color: #909399;
}

/* 详情对话框 */
.detail-content {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.detail-row {
  display: flex;
  align-items: center;
  gap: 8px;
}

.detail-row .label {
  font-weight: 600;
  color: #333;
  min-width: 80px;
}

.fee {
  font-size: 20px;
  font-weight: 600;
  color: #f56c6c;
}

.description {
  margin: 0;
  padding: 10px;
  background: #f5f7fa;
  border-radius: 8px;
  font-size: 14px;
  color: #666;
  line-height: 1.6;
}
</style>
