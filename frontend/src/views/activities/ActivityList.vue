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
          <el-input v-model="filters.search" placeholder="活动主题" clearable @clear="fetchActivities" @keyup.enter="fetchActivities" />
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
        <el-table-column label="封面" width="100">
          <template #default="{ row }">
            <div v-if="row.cover_image" class="cover-image-container">
              <el-image
                :src="getCoverImageUrl(row.cover_image)"
                fit="cover"
                class="cover-image"
                :preview-src-list="[getCoverImageUrl(row.cover_image)]"
                preview-teleported
              />
            </div>
            <span v-else class="no-cover">暂无封面</span>
          </template>
        </el-table-column>
        <el-table-column prop="title" label="活动主题" min-width="200" />
        <el-table-column label="类型" width="120">
          <template #default="{ row }">
            <el-tag :style="{ backgroundColor: row.activity_type_color, color: '#fff', border: 'none' }">
              {{ row.activity_type_name }}
            </el-tag>
          </template>
        </el-table-column>
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
                    <el-dropdown-item command="edit" v-if="isAdmin">
                      <el-icon><Edit /></el-icon>
                      <span>编辑</span>
                    </el-dropdown-item>
                    <el-dropdown-item command="register" v-if="!row.is_finished" :divided="isAdmin">
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
        <el-form-item label="活动封面">
          <el-upload
            class="cover-uploader"
            :action="uploadUrl"
            :headers="uploadHeaders"
            :show-file-list="false"
            :on-success="handleUploadSuccess"
            :before-upload="beforeUpload"
            accept="image/jpeg,image/jpg,image/png,image/gif,image/webp"
          >
            <img v-if="form.cover_image" :src="getCoverImageUrl(form.cover_image)" class="cover-preview" />
            <el-icon v-else class="cover-uploader-icon"><Plus /></el-icon>
          </el-upload>
          <div class="upload-tip">支持 jpg、jpeg、png、gif、webp 格式，建议尺寸 800x600，大小不超过 5MB</div>
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
      <div v-if="currentActivity">
        <!-- 封面图片 -->
        <div v-if="currentActivity.cover_image" class="detail-cover">
          <el-image
            :src="getCoverImageUrl(currentActivity.cover_image)"
            fit="contain"
            class="detail-cover-image"
            :preview-src-list="[getCoverImageUrl(currentActivity.cover_image)]"
            preview-teleported
          />
        </div>
        <el-descriptions :column="2" border>
          <el-descriptions-item label="活动主题">{{ currentActivity.title }}</el-descriptions-item>
          <el-descriptions-item label="活动类型">{{ currentActivity.activity_type_display }}</el-descriptions-item>
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
      </div>

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
        <el-form-item label="选择会员" prop="member_ids">
          <el-select
            v-model="registerForm.member_ids"
            placeholder="请选择会员（可多选）"
            style="width: 100%"
            filterable
            multiple
            collapse-tags
            collapse-tags-tooltip
          >
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
import { Plus, View, ArrowDown, Delete, Edit } from '@element-plus/icons-vue'
import { activityApi } from '@/api/activities'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()
const isAdmin = computed(() => authStore.user?.role === 'admin')

// API 基础 URL
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
const uploadUrl = `${API_BASE_URL}/api/activities/upload_cover/`
const uploadHeaders = computed(() => ({
  'Authorization': `Bearer ${authStore.token}`
}))

const loading = ref(false)
const submitting = ref(false)
const activities = ref([])
const dialogVisible = ref(false)
const detailVisible = ref(false)
const registerDialogVisible = ref(false)
const formRef = ref(null)
const registerFormRef = ref(null)
const isEdit = ref(false)
const currentEditId = ref(null)
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
  cover_image: null,
  start_time: '',
  end_time: '',
  fee: 0,
  description: ''
})

const registerForm = reactive({
  member_ids: [],
  note: ''
})

const registerRules = {
  member_ids: [
    { required: true, message: '请选择会员', trigger: 'change', validator: (rule, value, callback) => {
      if (!value || value.length === 0) {
        callback(new Error('请选择至少一个会员'))
      } else {
        callback()
      }
    }}
  ]
}

const rules = {
  title: [{ required: true, message: '请输入活动主题', trigger: 'blur' }],
  activity_type: [{ required: true, message: '请选择活动类型', trigger: 'change' }],
  start_time: [{ required: true, message: '请选择开始时间', trigger: 'change' }],
  fee: [{ required: true, message: '请输入费用', trigger: 'change' }]
}

const dialogTitle = computed(() => isEdit.value ? '编辑活动' : '新增活动')

// 获取封面图片 URL
const getCoverImageUrl = (imagePath) => {
  if (!imagePath) return ''
  // 如果是完整 URL，直接返回
  if (imagePath.startsWith('http://') || imagePath.startsWith('https://')) {
    return imagePath
  }
  // 否则拼接 API 基础 URL
  return `${API_BASE_URL}${imagePath}`
}

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

// 上传前校验
const beforeUpload = (file) => {
  const isImage = file.type.startsWith('image/')
  const isLt5M = file.size / 1024 / 1024 < 5

  if (!isImage) {
    ElMessage.error('只能上传图片文件!')
    return false
  }
  if (!isLt5M) {
    ElMessage.error('图片大小不能超过 5MB!')
    return false
  }
  return true
}

// 上传成功回调
const handleUploadSuccess = (response) => {
  if (response.url) {
    form.cover_image = response.url
    ElMessage.success('封面上传成功')
  } else {
    ElMessage.error('封面上传失败')
  }
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
  currentEditId.value = null
  Object.assign(form, {
    title: '',
    activity_type: activityTypes.value[0]?.id || null,
    cover_image: null,
    start_time: '',
    end_time: '',
    fee: 0,
    description: ''
  })
  dialogVisible.value = true
}

const showEditDialog = async (row) => {
  try {
    const res = await activityApi.getDetail(row.id)
    isEdit.value = true
    currentEditId.value = row.id
    Object.assign(form, {
      title: res.title,
      activity_type: res.activity_type,
      cover_image: res.cover_image,
      start_time: res.start_time,
      end_time: res.end_time || '',
      fee: res.fee,
      description: res.description || ''
    })
    dialogVisible.value = true
  } catch (error) {
    ElMessage.error('获取活动信息失败')
  }
}

const resetForm = () => {
  formRef.value?.resetFields()
  currentEditId.value = null
}

const handleSubmit = async () => {
  const valid = await formRef.value?.validate()
  if (!valid) return

  submitting.value = true
  try {
    if (isEdit.value && currentEditId.value) {
      await activityApi.update(currentEditId.value, form)
      ElMessage.success('更新成功')
    } else {
      await activityApi.create(form)
      ElMessage.success('创建成功')
    }
    dialogVisible.value = false
    fetchActivities()
  } catch (error) {
    ElMessage.error(isEdit.value ? '更新失败' : '创建失败')
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
  registerForm.member_ids = []
  registerForm.note = ''
  registerDialogVisible.value = true

  // 确保会员列表已加载
  if (memberOptions.value.length === 0) {
    await fetchMembers()
  }
}

const resetRegisterForm = () => {
  registerForm.member_ids = []
  registerForm.note = ''
}

const handleSubmitRegister = async () => {
  const valid = await registerFormRef.value?.validate()
  if (!valid) return

  submitting.value = true
  try {
    const result = await activityApi.register(currentActivity.value.id, {
      member_ids: registerForm.member_ids,
      note: registerForm.note
    })

    // 根据返回结果显示不同的消息
    const message = result.message || '报名完成'
    ElMessage.success(message)

    registerDialogVisible.value = false
    fetchActivities()
  } catch (error) {
    const errorMsg = error.response?.data?.error || error.response?.data?.detail || '报名失败'
    ElMessage.error(errorMsg)
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
  if (command === 'edit') {
    showEditDialog(row)
  } else if (command === 'register') {
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

/* 封面图片样式 */
.cover-image-container {
  display: flex;
  justify-content: center;
  align-items: center;
}

.cover-image {
  width: 80px;
  height: 80px;
  border-radius: 4px;
  object-fit: cover;
}

.no-cover {
  color: var(--el-text-color-secondary);
  font-size: 12px;
}

/* 上传组件样式 */
.cover-uploader {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.cover-uploader :deep(.el-upload) {
  border: 1px dashed var(--el-border-color);
  border-radius: 6px;
  cursor: pointer;
  position: relative;
  overflow: hidden;
  transition: var(--el-transition-duration-fast);
}

.cover-uploader :deep(.el-upload:hover) {
  border-color: var(--el-color-primary);
}

.cover-uploader-icon {
  font-size: 28px;
  color: #8c939d;
  width: 178px;
  height: 178px;
  text-align: center;
  line-height: 178px;
}

.cover-preview {
  width: 178px;
  height: 178px;
  display: block;
  object-fit: cover;
}

.upload-tip {
  margin-top: 8px;
  font-size: 12px;
  color: var(--el-text-color-secondary);
  text-align: center;
}

/* 详情页封面样式 */
.detail-cover {
  margin-bottom: 20px;
  text-align: center;
}

.detail-cover-image {
  max-width: 100%;
  max-height: 400px;
  border-radius: 8px;
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
