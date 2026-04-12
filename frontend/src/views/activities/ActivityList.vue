<template>
  <div class="activities">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>活动管理</span>
          <el-button type="primary" @click="showAddDialog" v-if="isAdmin">
            <el-icon><Plus /></el-icon>
            新增活动
          </el-button>
        </div>
      </template>

      <!-- 筛选 -->
      <el-form :inline="true" :model="filters" class="filter-form">
        <el-form-item label="搜索">
          <el-input v-model="filters.search" placeholder="主题/地点" clearable @clear="fetchActivities" @keyup.enter="fetchActivities" />
        </el-form-item>
        <el-form-item label="活动类型">
          <el-select v-model="filters.activity_type" placeholder="全部" clearable @change="fetchActivities">
            <el-option
              v-for="type in activityTypes"
              :key="type.id"
              :label="type.name"
              :value="type.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="filters.status" placeholder="全部" clearable @change="fetchActivities">
            <el-option label="即将开始" value="upcoming" />
            <el-option label="进行中" value="ongoing" />
            <el-option label="已结束" value="finished" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="fetchActivities">查询</el-button>
          <el-button @click="resetFilters">重置</el-button>
        </el-form-item>
      </el-form>

      <!-- 表格 -->
      <el-table :data="activities" v-loading="loading" border style="width: 100%">
        <el-table-column prop="title" label="活动主题" min-width="200" />
        <el-table-column label="类型" width="120">
          <template #default="{ row }">
            <el-tag :style="{ backgroundColor: row.activity_type_color, color: '#fff', border: 'none' }">
              {{ row.activity_type_name }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="location" label="地点" width="150" />
        <el-table-column label="开始时间" width="160">
          <template #default="{ row }">
            {{ formatDateTime(row.start_time) }}
          </template>
        </el-table-column>
        <el-table-column label="费用" width="80">
          <template #default="{ row }">
            ¥{{ row.fee }}
          </template>
        </el-table-column>
        <el-table-column label="状态" width="90">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">
              {{ row.status_display }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="已报名" width="80" align="center">
          <template #default="{ row }">
            {{ row.registered_count }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="160" align="center" fixed="right">
          <template #default="{ row }">
            <div class="action-buttons">
              <el-button size="small" type="primary" @click="showDetail(row)">
                <el-icon><View /></el-icon>
                <span>详情</span>
              </el-button>
              <el-dropdown @command="(cmd) => handleActionCommand(cmd, row)" v-if="!row.is_finished || isAdmin">
                <el-button size="small">
                  <span>更多</span>
                  <el-icon class="el-icon--right"><ArrowDown /></el-icon>
                </el-button>
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item command="register" v-if="!row.is_finished">
                      <el-icon><Plus /></el-icon>
                      <span>报名</span>
                    </el-dropdown-item>
                    <el-dropdown-item command="delete" v-if="isAdmin" divided>
                      <el-icon><Delete /></el-icon>
                      <span>删除</span>
                    </el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
            </div>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.size"
        :total="pagination.total"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next, jumper"
        style="margin-top: 20px; justify-content: flex-end"
      />
    </el-card>

    <!-- 新增/编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="600px"
      @close="resetForm"
    >
      <el-form :model="form" :rules="rules" ref="formRef" label-width="100px">
        <el-form-item label="活动主题" prop="title">
          <el-input v-model="form.title" placeholder="请输入活动主题" />
        </el-form-item>
        <el-form-item label="活动类型" prop="activity_type">
          <el-select v-model="form.activity_type" placeholder="请选择活动类型" style="width: 100%">
            <el-option
              v-for="type in activityTypes"
              :key="type.id"
              :label="type.name"
              :value="type.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="地点" prop="location">
          <el-input v-model="form.location" placeholder="请输入活动地点" />
        </el-form-item>
        <el-form-item label="开始时间" prop="start_time">
          <el-date-picker
            v-model="form.start_time"
            type="datetime"
            value-format="YYYY-MM-DD HH:mm:ss"
            placeholder="选择开始时间"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="结束时间">
          <el-date-picker
            v-model="form.end_time"
            type="datetime"
            value-format="YYYY-MM-DD HH:mm:ss"
            placeholder="选择结束时间（可选）"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="费用" prop="fee">
          <el-input-number v-model="form.fee" :min="0" :precision="2" />
        </el-form-item>
        <el-form-item label="活动描述">
          <el-input v-model="form.description" type="textarea" :rows="4" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitting">保存</el-button>
      </template>
    </el-dialog>

    <!-- 活动详情对话框 -->
    <el-dialog v-model="detailVisible" title="活动详情" width="800px">
      <el-descriptions v-if="currentActivity" :column="2" border>
        <el-descriptions-item label="活动主题">{{ currentActivity.title }}</el-descriptions-item>
        <el-descriptions-item label="活动类型">{{ currentActivity.activity_type_display }}</el-descriptions-item>
        <el-descriptions-item label="地点">{{ currentActivity.location }}</el-descriptions-item>
        <el-descriptions-item label="费用">¥{{ currentActivity.fee }}</el-descriptions-item>
        <el-descriptions-item label="开始时间">{{ formatDateTime(currentActivity.start_time) }}</el-descriptions-item>
        <el-descriptions-item label="结束时间">{{ currentActivity.end_time ? formatDateTime(currentActivity.end_time) : '-' }}</el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="getStatusType(currentActivity.status)">
            {{ currentActivity.status_display }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="已报名人数">{{ currentActivity.registered_count }}</el-descriptions-item>
        <el-descriptions-item label="活动描述" :span="2">
          {{ currentActivity.description || '-' }}
        </el-descriptions-item>
      </el-descriptions>

      <el-divider>报名名单</el-divider>
      <el-table :data="currentActivity.participations" size="small">
        <el-table-column prop="member_name" label="会员姓名" />
        <el-table-column prop="member_code" label="会员号" />
        <el-table-column label="报名时间">
          <template #default="{ row }">
            {{ formatDateTime(row.registered_at) }}
          </template>
        </el-table-column>
        <el-table-column prop="paid_amount" label="支付金额">
          <template #default="{ row }">
            ¥{{ row.paid_amount }}
          </template>
        </el-table-column>
      </el-table>
    </el-dialog>

    <!-- 报名对话框 -->
    <el-dialog
      v-model="registerDialogVisible"
      title="活动报名"
      width="500px"
      @close="resetRegisterForm"
    >
      <el-form :model="registerForm" :rules="registerRules" ref="registerFormRef" label-width="100px">
        <el-form-item label="选择会员" prop="member_id">
          <el-select v-model="registerForm.member_id" placeholder="请选择会员" style="width: 100%" filterable>
            <el-option
              v-for="member in memberOptions"
              :key="member.id"
              :label="`${member.code} - ${member.name}`"
              :value="member.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="registerForm.note" type="textarea" :rows="3" placeholder="选填" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="registerDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmitRegister" :loading="submitting">确认报名</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, View, ArrowDown, Delete } from '@element-plus/icons-vue'
import { activityApi } from '@/api/activities'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()
const isAdmin = computed(() => authStore.user?.role === 'admin')

const loading = ref(false)
const submitting = ref(false)
const activities = ref([])
const dialogVisible = ref(false)
const detailVisible = ref(false)
const registerDialogVisible = ref(false)
const formRef = ref(null)
const registerFormRef = ref(null)
const isEdit = ref(false)
const currentActivity = ref(null)
const memberOptions = ref([])
const activityTypes = ref([])

const filters = reactive({
  search: '',
  activity_type: '',
  status: ''
})

const pagination = reactive({
  page: 1,
  size: 20,
  total: 0
})

const form = reactive({
  title: '',
  activity_type: null,
  location: '',
  start_time: '',
  end_time: '',
  fee: 0,
  description: ''
})

const registerForm = reactive({
  member_id: '',
  note: ''
})

const registerRules = {
  member_id: [{ required: true, message: '请选择会员', trigger: 'change' }]
}

const rules = {
  title: [{ required: true, message: '请输入活动主题', trigger: 'blur' }],
  activity_type: [{ required: true, message: '请选择活动类型', trigger: 'change' }],
  location: [{ required: true, message: '请输入活动地点', trigger: 'blur' }],
  start_time: [{ required: true, message: '请选择开始时间', trigger: 'change' }],
  fee: [{ required: true, message: '请输入费用', trigger: 'change' }]
}

const dialogTitle = computed(() => isEdit.value ? '编辑活动' : '新增活动')

const getStatusType = (status) => {
  const types = { upcoming: 'info', ongoing: 'warning', finished: 'info' }
  return types[status] || 'info'
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

const fetchActivities = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      page_size: pagination.size,
      search: filters.search || undefined,
      activity_type: filters.activity_type || undefined,
      status: filters.status || undefined
    }
    const res = await activityApi.getList(params)
    activities.value = res.results || res
    pagination.total = res.count || res.length
  } catch (error) {
    ElMessage.error('获取活动列表失败')
  } finally {
    loading.value = false
  }
}

const fetchMembers = async () => {
  try {
    const { memberApi } = await import('@/api/member')
    const res = await memberApi.getList({ page_size: 1000 })
    memberOptions.value = res.results || res
  } catch (error) {
    console.error('获取会员列表失败', error)
  }
}

const fetchActivityTypes = async () => {
  try {
    const res = await activityApi.getTypes({ is_active: true })
    activityTypes.value = res.results || res
  } catch (error) {
    console.error('获取活动类型失败', error)
  }
}

const resetFilters = () => {
  filters.search = ''
  filters.activity_type = ''
  filters.status = ''
  fetchActivities()
}

const showAddDialog = () => {
  isEdit.value = false
  Object.assign(form, {
    title: '',
    activity_type: activityTypes.value[0]?.id || null,
    location: '',
    start_time: '',
    end_time: '',
    fee: 0,
    description: ''
  })
  dialogVisible.value = true
}

const resetForm = () => {
  formRef.value?.resetFields()
}

const handleSubmit = async () => {
  const valid = await formRef.value?.validate()
  if (!valid) return

  submitting.value = true
  try {
    await activityApi.create(form)
    ElMessage.success('创建成功')
    dialogVisible.value = false
    fetchActivities()
  } catch (error) {
    ElMessage.error('创建失败')
  } finally {
    submitting.value = false
  }
}

const showDetail = async (row) => {
  try {
    const res = await activityApi.getDetail(row.id)
    currentActivity.value = res
    detailVisible.value = true
  } catch (error) {
    ElMessage.error('获取活动详情失败')
  }
}

const handleRegister = async (row) => {
  currentActivity.value = row
  registerForm.member_id = ''
  registerForm.note = ''
  registerDialogVisible.value = true

  // 确保会员列表已加载
  if (memberOptions.value.length === 0) {
    await fetchMembers()
  }
}

const resetRegisterForm = () => {
  registerForm.member_id = ''
  registerForm.note = ''
}

const handleSubmitRegister = async () => {
  const valid = await registerFormRef.value?.validate()
  if (!valid) return

  submitting.value = true
  try {
    await activityApi.register(currentActivity.value.id, registerForm)
    ElMessage.success('报名成功')
    registerDialogVisible.value = false
    fetchActivities()
  } catch (error) {
    ElMessage.error(error.response?.data?.error || '报名失败')
  } finally {
    submitting.value = false
  }
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm(`确定删除活动《${row.title}》吗？`, '警告', {
      type: 'warning'
    })
    await activityApi.delete(row.id)
    ElMessage.success('删除成功')
    fetchActivities()
  } catch {
    // 取消删除
  }
}

const handleActionCommand = (command, row) => {
  if (command === 'register') {
    handleRegister(row)
  } else if (command === 'delete') {
    handleDelete(row)
  }
}

onMounted(() => {
  fetchActivityTypes()
  fetchActivities()
})
</script>

<style scoped>
.activities {
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

.filter-form {
  margin-bottom: 20px;
}

.filter-form :deep(.el-form-item) {
  margin-bottom: 0;
}

.filter-form :deep(.el-form-item__label) {
  font-size: var(--font-size-base);
  font-weight: 500;
}

/* 操作按钮布局优化 */
.action-buttons {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.action-buttons .el-button {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 5px 12px;
}

.action-buttons .el-button .el-icon {
  font-size: 14px;
}

.action-buttons .el-dropdown .el-button {
  padding: 5px 10px;
}

/* 下拉菜单样式优化 */
.el-dropdown-menu .el-dropdown-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
}

.el-dropdown-menu .el-dropdown-item .el-icon {
  font-size: 14px;
}

.el-dropdown-menu .el-dropdown-item span {
  font-size: 14px;
}
</style>
