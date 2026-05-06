<template>
  <div class="activity-summary">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>会员活动统计</span>
          <div class="header-actions">
            <el-select v-model="selectedYear" placeholder="全部年份" clearable @change="fetchSummary" style="width: 150px; margin-right: 10px">
              <el-option v-for="year in availableYears" :key="year" :label="year" :value="year" />
            </el-select>
            <el-button type="primary" @click="fetchSummary">刷新</el-button>
          </div>
        </div>
      </template>

      <!-- 统计概览 -->
      <el-row :gutter="20" class="summary-stats">
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-icon" style="background: #409eff">
                <el-icon :size="28"><User /></el-icon>
              </div>
              <div class="stat-info">
                <div class="stat-value">{{ summaryStats.totalMembers }}</div>
                <div class="stat-label">参与会员数</div>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-icon" style="background: #67c23a">
                <el-icon :size="28"><TrendCharts /></el-icon>
              </div>
              <div class="stat-info">
                <div class="stat-value">{{ summaryStats.totalActivities }}</div>
                <div class="stat-label">总参与次数</div>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-icon" style="background: #e6a23c">
                <el-icon :size="28"><Money /></el-icon>
              </div>
              <div class="stat-info">
                <div class="stat-value">¥{{ summaryStats.totalRevenue }}</div>
                <div class="stat-label">总费用</div>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-icon" style="background: #f56c6c">
                <el-icon :size="28"><Trophy /></el-icon>
              </div>
              <div class="stat-info">
                <div class="stat-value">{{ summaryStats.avgActivities }}</div>
                <div class="stat-label">人均参与</div>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>

      <!-- 会员活动统计表格 -->
      <el-table
        :data="memberSummary"
        v-loading="loading"
        border
        style="width: 100%; margin-top: 20px"
        :expand-row-keys="expandedRows"
        @expand-change="handleExpandChange"
        row-key="member_id"
      >
        <el-table-column type="expand" width="50">
          <template #default="{ row }">
            <div class="expand-content">
              <!-- 头部信息 -->
              <div class="expand-header">
                <div class="expand-title">
                  <el-icon :size="20"><User /></el-icon>
                  <span>{{ row.member_name }} - 年度活动明细</span>
                </div>
                <el-tag size="small" type="info">共 {{ row.yearly_breakdown.length }} 个年度</el-tag>
              </div>

              <!-- 年度卡片 -->
              <div class="yearly-cards">
                <div
                  v-for="item in row.yearly_breakdown"
                  :key="item.year"
                  class="yearly-card"
                  @click="showMemberActivities(row.member_id, item.year)"
                >
                  <div class="yearly-card-header">
                    <div class="year-badge">
                      <span class="year-number">{{ item.year }}</span>
                      <span class="year-label">年</span>
                    </div>
                    <el-button
                      size="small"
                      type="primary"
                      :icon="ArrowRight"
                      circle
                      class="view-btn"
                    />
                  </div>

                  <div class="yearly-stats">
                    <div class="stat-item">
                      <div class="stat-icon" style="background: #409eff">
                        <el-icon><TrendCharts /></el-icon>
                      </div>
                      <div class="stat-content">
                        <span class="stat-value">{{ item.count }}</span>
                        <span class="stat-label">参与次数</span>
                      </div>
                    </div>

                    <div class="stat-item">
                      <div class="stat-icon" style="background: #67c23a">
                        <el-icon><Money /></el-icon>
                      </div>
                      <div class="stat-content">
                        <span class="stat-value">¥{{ item.total_fee }}</span>
                        <span class="stat-label">总费用</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="member_code" label="会员号" width="120" />
        <el-table-column prop="member_name" label="会员姓名" width="120" />
        <el-table-column prop="total_count" label="总参与次数" width="120" align="center" sortable />
        <el-table-column prop="total_fee" label="总费用" width="120" sortable>
          <template #default="{ row }">
            ¥{{ row.total_fee }}
          </template>
        </el-table-column>
        <el-table-column label="年度概览" min-width="300">
          <template #default="{ row }">
            <div class="yearly-overview">
              <el-tag
                v-for="item in row.yearly_breakdown.slice(0, 3)"
                :key="item.year"
                size="small"
                style="margin-right: 5px; margin-bottom: 5px"
              >
                {{ item.year }}年: {{ item.count }}次
              </el-tag>
              <el-tag v-if="row.yearly_breakdown.length > 3" type="info" size="small">
                +{{ row.yearly_breakdown.length - 3 }}
              </el-tag>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="120" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="showMemberActivities(row.member_id)">
              查看活动
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 会员活动详情对话框 -->
    <el-dialog
      v-model="activitiesVisible"
      :title="`${currentMember.name} - 参与的活动列表`"
      width="1100px"
      class="activities-dialog"
    >
      <div v-loading="activitiesLoading" class="activities-container">
        <div v-if="memberActivities.length === 0" class="empty-state">
          <el-empty description="暂无活动记录" />
        </div>
        <div v-else class="activities-grid">
          <div
            v-for="activity in memberActivities"
            :key="activity.id"
            class="activity-card"
          >
            <!-- 活动封面 -->
            <div class="activity-cover">
              <!-- 调试信息 -->
              <div style="position: absolute; top: 0; left: 0; background: rgba(255,0,0,0.8); color: white; font-size: 10px; padding: 2px; z-index: 999;">
                封面: {{ activity.activity_cover_image ? '有' : '无' }} | URL: {{ getCoverImage(activity.activity_cover_image) }}
              </div>

              <el-image
                v-if="activity.activity_cover_image"
                :src="getCoverImage(activity.activity_cover_image)"
                fit="cover"
                class="cover-image"
                :preview-src-list="[getCoverImage(activity.activity_cover_image)]"
                preview-teleported
              >
                <template #error>
                  <div class="image-error">
                    <el-icon><Picture /></el-icon>
                    <span>加载失败</span>
                  </div>
                </template>
                <template #placeholder>
                  <div class="image-placeholder">
                    加载中...
                  </div>
                </template>
              </el-image>
              <div v-else class="no-cover">
                <el-icon :size="40"><Picture /></el-icon>
                <span>暂无封面</span>
              </div>
              <!-- 活动类型标签 -->
              <div class="activity-type-badge">
                <el-tag
                  :style="{
                    backgroundColor: activity.activity_type_color,
                    color: '#fff',
                    border: 'none'
                  }"
                  size="small"
                >
                  {{ activity.activity_type_name }}
                </el-tag>
              </div>
            </div>

            <!-- 活动信息 -->
            <div class="activity-info">
              <h3 class="activity-title">{{ activity.activity_title }}</h3>

              <!-- 活动描述 -->
              <div v-if="activity.activity_description" class="activity-description">
                <el-icon class="description-icon"><Document /></el-icon>
                <p class="description-text">{{ activity.activity_description }}</p>
              </div>

              <!-- 活动类型描述 -->
              <div v-if="activity.activity_type_description" class="activity-type-description">
                <el-icon class="type-icon"><InfoFilled /></el-icon>
                <span class="type-text">{{ activity.activity_type_description }}</span>
              </div>

              <div class="activity-details">
                <div class="detail-item">
                  <el-icon class="detail-icon"><Clock /></el-icon>
                  <span>{{ formatDateTime(activity.activity_start_time) }}</span>
                </div>

                <div class="detail-item">
                  <el-icon class="detail-icon"><Money /></el-icon>
                  <span>费用: ¥{{ activity.activity_fee }}</span>
                </div>

                <div class="detail-item">
                  <el-icon class="detail-icon"><Calendar /></el-icon>
                  <span>报名时间: {{ formatDateTime(activity.registered_at) }}</span>
                </div>

                <div class="detail-item">
                  <el-icon class="detail-icon"><Wallet /></el-icon>
                  <span>实付: ¥{{ activity.paid_amount }}</span>
                </div>
              </div>

              <div v-if="activity.note" class="activity-note">
                <el-icon><Document /></el-icon>
                <span>{{ activity.note }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { User, TrendCharts, Money, Trophy, ArrowRight, Clock, Calendar, Wallet, Document, Picture, InfoFilled } from '@element-plus/icons-vue'
import { activityApi } from '@/api/activities'

// API 基础 URL
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

const loading = ref(false)
const activitiesLoading = ref(false)
const memberSummary = ref([])
const expandedRows = ref([])
const selectedYear = ref(null)
const availableYears = ref([])

const summaryStats = reactive({
  totalMembers: 0,
  totalActivities: 0,
  totalRevenue: 0,
  avgActivities: 0
})

const activitiesVisible = ref(false)
const memberActivities = ref([])
const currentMember = ref({})

const getActivityTypeDisplay = (type) => {
  const types = {
    reading_club: '读书会',
    english_corner: '英语角',
    lecture: '讲座'
  }
  return types[type] || type
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

// 获取封面图片URL
const getCoverImage = (imagePath) => {
  if (!imagePath) return ''
  // 如果是完整 URL，直接返回
  if (imagePath.startsWith('http://') || imagePath.startsWith('https://')) {
    return imagePath
  }
  // 否则直接返回相对路径（通过Vite代理访问）
  return imagePath
}

const fetchSummary = async () => {
  loading.value = true
  try {
    const params = selectedYear.value ? { year: selectedYear.value } : {}
    const res = await activityApi.getMemberActivitySummary(params)

    // 确保返回的是数组
    if (!Array.isArray(res)) {
      console.error('API返回的数据格式不正确，期望是数组，实际是：', typeof res, res)
      ElMessage.error('获取统计数据失败：数据格式错误')
      return
    }

    memberSummary.value = res

    // 计算统计概览
    summaryStats.totalMembers = res.length
    summaryStats.totalActivities = res.reduce((sum, item) => sum + item.total_count, 0)
    summaryStats.totalRevenue = res.reduce((sum, item) => sum + Number(item.total_fee), 0).toFixed(2)
    summaryStats.avgActivities = res.length > 0
      ? (summaryStats.totalActivities / res.length).toFixed(1)
      : 0

    // 提取可用年份
    const years = new Set()
    res.forEach(member => {
      if (member.yearly_breakdown && Array.isArray(member.yearly_breakdown)) {
        member.yearly_breakdown.forEach(item => {
          years.add(item.year)
        })
      }
    })
    availableYears.value = Array.from(years).sort((a, b) => b - a)
  } catch (error) {
    console.error('获取统计数据失败：', error)
    ElMessage.error('获取统计数据失败：' + (error.message || '未知错误'))
  } finally {
    loading.value = false
  }
}

const handleExpandChange = (row, expandedRows) => {
  expandedRows.value = expandedRows.map(r => r.member_id)
}

const showMemberActivities = async (memberId, year = null) => {
  activitiesLoading.value = true
  activitiesVisible.value = true
  try {
    const res = await activityApi.getMemberActivities(memberId)
    currentMember.value = {
      id: res.member_id,
      name: res.member_name
    }

    let activities = res.activities
    if (year) {
      activities = activities.filter(item => {
        const activityYear = new Date(item.activity_start_time).getFullYear()
        return activityYear === year
      })
    }

    // 调试：检查封面图片数据
    console.log('[DEBUG] 活动数据：', activities)
    activities.forEach((act, index) => {
      console.log(`[DEBUG] 活动${index + 1}:`, {
        title: act.activity_title,
        cover_image: act.activity_cover_image,
        cover_image_type: typeof act.activity_cover_image,
        cover_image_empty: !act.activity_cover_image,
        generated_url: act.activity_cover_image ? getCoverImage(act.activity_cover_image) : 'N/A'
      })
    })

    memberActivities.value = activities
  } catch (error) {
    console.error('[ERROR] 获取活动列表失败：', error)
    ElMessage.error('获取活动列表失败')
  } finally {
    activitiesLoading.value = false
  }
}

onMounted(() => {
  fetchSummary()
})
</script>

<style scoped>
.activity-summary {
  height: 100%;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header span {
  font-size: var(--font-size-lg);
  font-weight: 600;
}

.header-actions {
  display: flex;
  align-items: center;
}

.summary-stats {
  margin-bottom: 20px;
}

.stat-card {
  cursor: pointer;
  transition: all 0.3s;
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.12);
}

.stat-content {
  display: flex;
  align-items: center;
  gap: 15px;
}

.stat-icon {
  width: 56px;
  height: 56px;
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 28px;
  font-weight: bold;
  color: #303133;
}

.stat-label {
  font-size: var(--font-size-sm);
  color: #909399;
  margin-top: 5px;
}

.yearly-overview {
  display: flex;
  flex-wrap: wrap;
}

/* 展开内容样式 */
.expand-content {
  padding: 20px;
  background: #f5f7fa;
  border-radius: 8px;
}

.expand-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 1px solid #e4e7ed;
}

.expand-title {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

/* 年度卡片布局 */
.yearly-cards {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 15px;
}

.yearly-card {
  background: #fff;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  cursor: pointer;
  transition: all 0.3s;
  border: 2px solid transparent;
}

.yearly-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12);
  border-color: #409eff;
}

.yearly-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.year-badge {
  display: flex;
  align-items: baseline;
  gap: 4px;
}

.year-number {
  font-size: 32px;
  font-weight: bold;
  color: #409eff;
  line-height: 1;
}

.year-label {
  font-size: 14px;
  color: #909399;
}

.view-btn {
  opacity: 0;
  transition: opacity 0.3s;
}

.yearly-card:hover .view-btn {
  opacity: 1;
}

.yearly-stats {
  display: flex;
  gap: 20px;
}

.yearly-stats .stat-item {
  display: flex;
  align-items: center;
  gap: 12px;
  flex: 1;
}

.yearly-stats .stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  flex-shrink: 0;
}

.yearly-stats .stat-content {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.yearly-stats .stat-value {
  font-size: 20px;
  font-weight: bold;
  color: #303133;
  line-height: 1;
}

.yearly-stats .stat-label {
  font-size: 12px;
  color: #909399;
}

/* 活动详情对话框样式 */
.activities-dialog .el-dialog__body {
  padding: 0 20px 20px;
}

.activities-container {
  min-height: 300px;
}

.empty-state {
  padding: 40px 0;
}

/* 活动卡片网格 */
.activities-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 20px;
  padding: 10px 0;
}

.activity-card {
  background: #fff;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  transition: all 0.3s;
  border: 1px solid #e4e7ed;
}

.activity-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
  border-color: #409eff;
}

/* 活动封面 */
.activity-cover {
  position: relative;
  width: 100%;
  height: 180px;
  overflow: hidden;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.activity-cover .cover-image {
  width: 100%;
  height: 100%;
}

.activity-cover :deep(.el-image) {
  width: 100%;
  height: 100%;
}

.activity-cover :deep(.el-image__inner) {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.activity-cover .no-cover {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #fff;
  gap: 10px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.activity-cover .no-cover span {
  font-size: 14px;
  opacity: 0.8;
}

.activity-type-badge {
  position: absolute;
  top: 12px;
  left: 12px;
}

/* 图片加载状态 */
.image-error,
.image-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 8px;
  background: linear-gradient(135deg, #f56c6c 0%, #ff8b8b 100%);
  color: #fff;
  font-size: 14px;
}

.image-placeholder {
  background: linear-gradient(135deg, #909399 0%, #b1b3b8 100%);
}

/* 活动信息 */
.activity-info {
  padding: 16px;
}

.activity-title {
  margin: 0 0 12px 0;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  line-height: 1.4;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

/* 活动描述 */
.activity-description {
  display: flex;
  gap: 8px;
  padding: 10px;
  background: linear-gradient(135deg, #e8f5e9 0%, #f1f8e9 100%);
  border-radius: 8px;
  border-left: 3px solid #67c23a;
  margin-bottom: 10px;
}

.description-icon {
  font-size: 18px;
  color: #67c23a;
  flex-shrink: 0;
  margin-top: 2px;
}

.description-text {
  margin: 0;
  font-size: 13px;
  color: #606266;
  line-height: 1.6;
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
}

/* 活动类型描述 */
.activity-type-description {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  background: linear-gradient(135deg, #e3f2fd 0%, #e8eaf6 100%);
  border-radius: 6px;
  border-left: 3px solid #409eff;
  margin-bottom: 10px;
}

.type-icon {
  font-size: 16px;
  color: #409eff;
  flex-shrink: 0;
}

.type-text {
  font-size: 12px;
  color: #606266;
  line-height: 1.5;
  flex: 1;
}

.activity-details {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
  margin-bottom: 12px;
}

.detail-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: #606266;
}

.detail-icon {
  font-size: 16px;
  color: #909399;
  flex-shrink: 0;
}

.activity-note {
  display: flex;
  align-items: flex-start;
  gap: 6px;
  padding: 10px;
  background: #f5f7fa;
  border-radius: 6px;
  font-size: 12px;
  color: #909399;
  line-height: 1.5;
  margin-top: 8px;
}

.activity-note .el-icon {
  flex-shrink: 0;
  margin-top: 2px;
}
</style>
