<template>
  <div class="activity-calendar">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>活动日历</span>
          <div class="header-actions">
            <el-button @click="goToPrevMonth" :icon="ArrowLeft">上个月</el-button>
            <el-date-picker
              v-model="currentMonth"
              type="month"
              placeholder="选择月份"
              format="YYYY年MM月"
              value-format="YYYY-MM"
              @change="handleMonthChange"
              style="width: 150px; margin: 0 10px"
            />
            <el-button @click="goToNextMonth">下个月</el-button>
            <el-button type="primary" @click="fetchCalendarData" style="margin-left: 10px">
              <el-icon><Refresh /></el-icon>
              刷新
            </el-button>
          </div>
        </div>
      </template>

      <!-- 日历网格视图 -->
      <div class="calendar-grid">
        <!-- 星期标题 -->
        <div class="weekday-header">
          <div v-for="weekday in weekdays" :key="weekday" class="weekday-item">
            {{ weekday }}
          </div>
        </div>

        <!-- 日期网格 -->
        <div class="days-grid">
          <div
            v-for="(day, index) in calendarDays"
            :key="index"
            :class="['day-cell', {
              'other-month': day.isOtherMonth,
              'today': day.isToday,
              'has-activity': day.activities.length > 0
            }]"
            @click="handleDayClick(day)"
          >
            <div class="day-number">{{ day.date }}</div>
            <div class="activity-list">
              <div
                v-for="(activity, idx) in day.activities.slice(0, 3)"
                :key="idx"
                class="activity-item"
                :style="{
                  backgroundColor: getActivityTypeColor(activity),
                  color: getTextColor(getActivityTypeColor(activity))
                }"
                :title="activity.title"
              >
                <span class="activity-type-text">{{ getActivityTypeDisplay(activity) }}</span>
              </div>
              <div v-if="day.activities.length > 3" class="more-indicator">
                +{{ day.activities.length - 3 }}个活动
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 活动图例 -->
      <div class="legend">
        <span>活动类型：</span>
        <span class="legend-item">
          <span class="legend-dot" style="background: #67c23a"></span>
          读书会
        </span>
        <span class="legend-item">
          <span class="legend-dot" style="background: #e6a23c"></span>
          英语角
        </span>
        <span class="legend-item">
          <span class="legend-dot" style="background: #f56c6c"></span>
          讲座
        </span>
      </div>
    </el-card>

    <!-- 日期活动详情对话框 -->
    <el-dialog
      v-model="dayDialogVisible"
      :title="`${selectedDate} 的活动`"
      width="700px"
    >
      <el-table :data="selectedDayActivities" v-loading="loading" border>
        <el-table-column prop="title" label="活动主题" min-width="180" />
        <el-table-column label="类型" width="120">
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
        <el-table-column prop="location" label="地点" width="120" />
        <el-table-column label="时间" width="180">
          <template #default="{ row }">
            {{ formatTime(row.start_time) }}
          </template>
        </el-table-column>
        <el-table-column prop="fee" label="费用" width="80">
          <template #default="{ row }">
            ¥{{ row.fee }}
          </template>
        </el-table-column>
        <el-table-column prop="registered_count" label="已报名" width="80" align="center" />
        <el-table-column label="操作" width="80">
          <template #default="{ row }">
            <el-button size="small" type="primary" @click="goToActivityDetail(row.id)">
              详情
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { ArrowLeft, Refresh } from '@element-plus/icons-vue'
import { activityApi } from '@/api/activities'

const loading = ref(false)
const currentMonth = ref('')
const calendarData = ref({})
const dayDialogVisible = ref(false)
const selectedDate = ref('')
const selectedDayActivities = ref([])

const weekdays = ['日', '一', '二', '三', '四', '五', '六']

// 计算日历网格
const calendarDays = computed(() => {
  if (!currentMonth.value) return []

  const [year, month] = currentMonth.value.split('-').map(Number)
  const today = new Date()
  const todayStr = `${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, '0')}-${String(today.getDate()).padStart(2, '0')}`

  // 获取当月第一天和最后一天
  const firstDay = new Date(year, month - 1, 1)
  const lastDay = new Date(year, month, 0)

  // 获取当月第一天是星期几（0-6）
  const firstDayWeek = firstDay.getDay()

  // 生成日历数组
  const days = []

  // 填充上个月的日期
  const prevMonthLastDay = new Date(year, month - 1, 0).getDate()
  for (let i = firstDayWeek - 1; i >= 0; i--) {
    const date = prevMonthLastDay - i
    // 正确处理上个月的年月
    const prevMonthDate = new Date(year, month - 1, date)
    const prevYear = prevMonthDate.getFullYear()
    const prevMonth = prevMonthDate.getMonth() + 1
    const dateStr = `${prevYear}-${String(prevMonth).padStart(2, '0')}-${String(date).padStart(2, '0')}`
    days.push({
      date,
      dateStr,
      isOtherMonth: true,
      isToday: dateStr === todayStr,
      activities: getActivitiesForDate(dateStr)
    })
  }

  // 填充当月的日期
  for (let i = 1; i <= lastDay.getDate(); i++) {
    const date = i
    const dateStr = `${year}-${String(month).padStart(2, '0')}-${String(date).padStart(2, '0')}`
    days.push({
      date,
      dateStr,
      isOtherMonth: false,
      isToday: dateStr === todayStr,
      activities: getActivitiesForDate(dateStr)
    })
  }

  // 填充下个月的日期
  const remainingDays = 42 - days.length
  for (let i = 1; i <= remainingDays; i++) {
    const date = i
    // 正确处理下个月的年月
    const nextMonthDate = new Date(year, month, i)
    const nextYear = nextMonthDate.getFullYear()
    const nextMonth = nextMonthDate.getMonth() + 1
    const dateStr = `${nextYear}-${String(nextMonth).padStart(2, '0')}-${String(date).padStart(2, '0')}`
    days.push({
      date,
      dateStr,
      isOtherMonth: true,
      isToday: dateStr === todayStr,
      activities: getActivitiesForDate(dateStr)
    })
  }

  return days
})

// 获取指定日期的活动
const getActivitiesForDate = (dateStr) => {
  if (!calendarData.value[dateStr]) return []
  return calendarData.value[dateStr]
}

// 获取活动类型显示名称（现在直接使用后端返回的名称）
const getActivityTypeDisplay = (activity) => {
  return activity.activity_type_name || '未知类型'
}

// 获取活动类型标签类型（现在使用后端返回的颜色）
const getActivityTypeColor = (activity) => {
  return activity.activity_type_color || '#409eff'
}

// 判断文字颜色（根据背景色亮度）
const getTextColor = (backgroundColor) => {
  // 简单判断：黄色系使用深色文字，其他使用白色文字
  const color = backgroundColor.toLowerCase()
  if (color.includes('e6a23c') || color.includes('f0a020') || color.includes('ffcc00')) {
    return '#303133'
  }
  return '#fff'
}

// 获取活动类型样式类（保留用于向后兼容，但现在基于颜色动态生成）
const getActivityTypeClass = (activity) => {
  // 返回一个基于颜色值的类名，用于动态样式
  return 'activity-type-' + (activity.activity_type_code || 'default')
}

// 格式化时间
const formatTime = (dateTime) => {
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

// 获取日历数据
const fetchCalendarData = async () => {
  loading.value = true
  try {
    const [year, month] = currentMonth.value.split('-').map(Number)
    const res = await activityApi.getCalendar({ year, month })

    // 将数据转换为以日期为键的对象
    const data = {}
    res.forEach(item => {
      const dateStr = item.date
      data[dateStr] = item.activities
    })

    calendarData.value = data
  } catch (error) {
    ElMessage.error('获取日历数据失败')
  } finally {
    loading.value = false
  }
}

// 处理月份变化
const handleMonthChange = () => {
  fetchCalendarData()
}

// 上个月
const goToPrevMonth = () => {
  const [year, month] = currentMonth.value.split('-').map(Number)
  const date = new Date(year, month - 2, 1)
  currentMonth.value = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}`
  fetchCalendarData()
}

// 下个月
const goToNextMonth = () => {
  const [year, month] = currentMonth.value.split('-').map(Number)
  const date = new Date(year, month, 1)
  currentMonth.value = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}`
  fetchCalendarData()
}

// 点击日期
const handleDayClick = (day) => {
  if (day.activities.length > 0) {
    selectedDate.value = day.dateStr
    selectedDayActivities.value = day.activities
    dayDialogVisible.value = true
  }
}

// 跳转到活动详情
const goToActivityDetail = (activityId) => {
  // 这里可以跳转到活动详情页面或打开详情对话框
  dayDialogVisible.value = false
  // 可以通过路由跳转或打开详情对话框
  ElMessage.info(`查看活动详情: ID ${activityId}`)
}

// 初始化
onMounted(() => {
  const now = new Date()
  currentMonth.value = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}`
  fetchCalendarData()
})
</script>

<style scoped>
.activity-calendar {
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

.calendar-grid {
  margin-top: 20px;
}

.weekday-header {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 1px;
  background: #dcdfe6;
  border: 1px solid #dcdfe6;
}

.weekday-item {
  background: #f5f7fa;
  padding: 10px;
  text-align: center;
  font-weight: 600;
  color: #606266;
}

.days-grid {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 1px;
  background: #dcdfe6;
  border: 1px solid #dcdfe6;
  border-top: none;
}

.day-cell {
  background: #fff;
  min-height: 100px;
  padding: 8px;
  cursor: pointer;
  transition: all 0.2s;
  position: relative;
}

.day-cell:hover {
  background: #f5f7fa;
}

.day-cell.other-month {
  background: #fafafa;
  color: #c0c4cc;
}

.day-cell.today {
  background: #ecf5ff;
}

.day-cell.has-activity {
  cursor: pointer;
}

.day-number {
  font-size: 14px;
  font-weight: 500;
  margin-bottom: 8px;
}

.day-cell.today .day-number {
  color: #409eff;
  font-weight: bold;
}

.activity-list {
  display: flex;
  flex-direction: column;
  gap: 3px;
  margin-top: 4px;
}

.activity-item {
  padding: 2px 6px;
  border-radius: 3px;
  font-size: 11px;
  line-height: 1.4;
  text-align: center;
  font-weight: 500;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.activity-type-text {
  display: block;
}

.more-indicator {
  font-size: 11px;
  color: #909399;
  text-align: center;
  padding: 2px 0;
}

.legend {
  display: flex;
  align-items: center;
  margin-top: 20px;
  padding: 15px;
  background: #f5f7fa;
  border-radius: var(--radius-md);
}

.legend-item {
  display: flex;
  align-items: center;
  margin-left: 20px;
  font-size: 14px;
  color: #606266;
}

.legend-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  margin-right: 5px;
}
</style>
