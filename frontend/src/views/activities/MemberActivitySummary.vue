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
      width="900px"
    >
      <el-table :data="memberActivities" v-loading="activitiesLoading" border>
        <el-table-column prop="activity_title" label="活动主题" min-width="200" />
        <el-table-column label="活动类型" width="120">
          <template #default="{ row }">
            <el-tag :style="{
              backgroundColor: row.activity_type_color,
              color: '#fff',
              border: 'none'
            }" size="small">
              {{ row.activity_type_name }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="activity_location" label="地点" width="150" />
        <el-table-column label="活动时间" width="180">
          <template #default="{ row }">
            {{ formatDateTime(row.activity_start_time) }}
          </template>
        </el-table-column>
        <el-table-column prop="activity_fee" label="费用" width="80">
          <template #default="{ row }">
            ¥{{ row.activity_fee }}
          </template>
        </el-table-column>
        <el-table-column label="报名时间" width="180">
          <template #default="{ row }">
            {{ formatDateTime(row.registered_at) }}
          </template>
        </el-table-column>
        <el-table-column prop="paid_amount" label="实付金额" width="100">
          <template #default="{ row }">
            ¥{{ row.paid_amount }}
          </template>
        </el-table-column>
      </el-table>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { User, TrendCharts, Money, Trophy, ArrowRight } from '@element-plus/icons-vue'
import { activityApi } from '@/api/activities'

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

    memberActivities.value = activities
  } catch (error) {
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
</style>
