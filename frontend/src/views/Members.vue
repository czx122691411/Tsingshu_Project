<template>
  <div class="members">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>会员管理</span>
          <el-button type="primary" @click="showAddDialog">
            <el-icon><Plus /></el-icon>
            新增会员
          </el-button>
        </div>
      </template>

      <!-- 筛选 -->
      <el-form :inline="true" :model="filters" class="filter-form">
        <el-form-item label="搜索">
          <el-input v-model="filters.search" placeholder="姓名/电话/会员号" clearable @clear="fetchMembers" @keyup.enter="fetchMembers" />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="filters.status" placeholder="全部" clearable @change="fetchMembers">
            <el-option label="有效" value="active" />
            <el-option label="即将到期" value="expiring" />
            <el-option label="已到期" value="expired" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="fetchMembers">查询</el-button>
          <el-button @click="resetFilters">重置</el-button>
        </el-form-item>
      </el-form>

      <!-- 表格 -->
      <el-table :data="members" v-loading="loading" border style="width: 100%">
        <el-table-column prop="code" label="会员号" width="120" />
        <el-table-column prop="name" label="姓名" width="120" />
        <el-table-column prop="phone" label="电话" width="140" />
        <el-table-column label="期限" min-width="200">
          <template #default="{ row }">
            {{ row.start_date }} → {{ row.end_date }}
          </template>
        </el-table-column>
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">
              {{ row.status_display }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="280" fixed="right">
          <template #default="{ row }">
            <el-button size="small" type="success" @click="handleRenew(row)">
              <el-icon><RefreshRight /></el-icon>
              续费
            </el-button>
            <el-button size="small" @click="showEditDialog(row)">编辑</el-button>
            <el-button size="small" type="danger" @click="handleDelete(row)">删除</el-button>
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
        @current-change="fetchMembers"
        @size-change="fetchMembers"
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
        <el-form-item label="姓名" prop="name">
          <el-input v-model="form.name" />
        </el-form-item>
        <el-form-item label="电话">
          <el-input v-model="form.phone" />
        </el-form-item>
        <el-form-item label="会员号">
          <el-input v-model="form.code" placeholder="留空自动生成" />
        </el-form-item>
        <el-form-item label="开始日期" prop="start_date">
          <el-date-picker v-model="form.start_date" type="date" value-format="YYYY-MM-DD" style="width: 100%" />
        </el-form-item>
        <el-form-item label="到期日期" prop="end_date">
          <el-date-picker v-model="form.end_date" type="date" value-format="YYYY-MM-DD" style="width: 100%" />
        </el-form-item>
        <el-form-item label="缴费日期" prop="pay_date">
          <el-date-picker v-model="form.pay_date" type="date" value-format="YYYY-MM-DD" style="width: 100%" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="form.note" type="textarea" :rows="3" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitting">保存</el-button>
      </template>
    </el-dialog>

    <!-- 续费对话框 -->
    <el-dialog v-model="renewDialogVisible" title="会员续费" width="480px">
      <el-form :model="renewForm" label-width="100px">
        <el-form-item label="会员">
          <span>{{ currentMember?.code }} - {{ currentMember?.name }}</span>
        </el-form-item>
        <el-form-item label="当前到期">
          <span>{{ currentMember?.end_date }}</span>
        </el-form-item>
        <el-form-item label="续费金额">
          <el-input-number v-model="renewForm.amount" :min="1" :max="10000" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="renewForm.note" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="renewDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleRenewSubmit" :loading="renewing">确认续费</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, RefreshRight } from '@element-plus/icons-vue'
import { memberApi } from '@/api/member'

const loading = ref(false)
const submitting = ref(false)
const renewing = ref(false)
const members = ref([])
const dialogVisible = ref(false)
const renewDialogVisible = ref(false)
const formRef = ref(null)
const currentMember = ref(null)
const isEdit = ref(false)

const filters = reactive({
  search: '',
  status: ''
})

const pagination = reactive({
  page: 1,
  size: 20,
  total: 0
})

const form = reactive({
  id: null,
  code: '',
  name: '',
  phone: '',
  start_date: '',
  end_date: '',
  pay_date: '',
  note: ''
})

const renewForm = reactive({
  amount: 365,
  note: '续费'
})

const rules = {
  name: [{ required: true, message: '请输入姓名', trigger: 'blur' }],
  start_date: [{ required: true, message: '请选择开始日期', trigger: 'change' }],
  end_date: [{ required: true, message: '请选择到期日期', trigger: 'change' }],
  pay_date: [{ required: true, message: '请选择缴费日期', trigger: 'change' }]
}

const dialogTitle = computed(() => isEdit.value ? '编辑会员' : '新增会员')

const getStatusType = (status) => {
  const types = { active: 'success', expiring: 'warning', expired: 'danger' }
  return types[status] || 'info'
}

const fetchMembers = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      page_size: pagination.size,
      search: filters.search || undefined,
      status: filters.status || undefined
    }
    const res = await memberApi.getList(params)
    members.value = res.results || res
    pagination.total = res.count || res.length
  } catch (error) {
    ElMessage.error('获取会员列表失败')
  } finally {
    loading.value = false
  }
}

const resetFilters = () => {
  filters.search = ''
  filters.status = ''
  fetchMembers()
}

const showAddDialog = () => {
  isEdit.value = false
  const today = new Date().toISOString().split('T')[0]
  Object.assign(form, {
    id: null,
    code: '',
    name: '',
    phone: '',
    start_date: today,
    end_date: '',
    pay_date: today,
    note: ''
  })
  dialogVisible.value = true
}

const showEditDialog = (row) => {
  isEdit.value = true
  Object.assign(form, row)
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
    console.log('提交表单数据:', form)
    if (isEdit.value) {
      await memberApi.update(form.id, form)
      ElMessage.success('更新成功')
    } else {
      // Only send fields expected by the backend
      const { id, ...memberData } = form
      console.log('发送会员数据:', memberData)
      await memberApi.create(memberData)
      ElMessage.success('创建成功')
    }
    dialogVisible.value = false
    fetchMembers()
  } catch (error) {
    console.error('创建/更新会员失败:', error)
    console.error('错误响应:', error.response?.data)
    ElMessage.error(isEdit.value ? '更新失败' : '创建失败')
  } finally {
    submitting.value = false
  }
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm(`确定删除会员 ${row.name} 吗？`, '警告', {
      type: 'warning'
    })
    await memberApi.delete(row.id)
    ElMessage.success('删除成功')
    fetchMembers()
  } catch {
    // 取消删除
  }
}

const handleRenew = (row) => {
  currentMember.value = row
  renewForm.amount = 365
  renewForm.note = '续费'
  renewDialogVisible.value = true
}

const handleRenewSubmit = async () => {
  renewing.value = true
  try {
    await memberApi.renew(currentMember.value.id, renewForm)
    ElMessage.success('续费成功')
    renewDialogVisible.value = false
    fetchMembers()
  } catch (error) {
    ElMessage.error('续费失败')
  } finally {
    renewing.value = false
  }
}

onMounted(() => {
  fetchMembers()
})
</script>

<style scoped>
.members {
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
</style>
