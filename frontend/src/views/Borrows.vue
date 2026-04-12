<template>
  <div class="borrows">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>借阅管理</span>
          <el-button type="primary" @click="showAddDialog">
            <el-icon><Plus /></el-icon>
            新增借阅
          </el-button>
        </div>
      </template>

      <!-- 筛选 -->
      <el-form :inline="true" :model="filters" class="filter-form">
        <el-form-item label="会员">
          <el-select v-model="filters.member" placeholder="全部" clearable filterable @change="fetchBorrows">
            <el-option
              v-for="m in memberOptions"
              :key="m.id"
              :label="`${m.code} - ${m.name}`"
              :value="m.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="filters.status" placeholder="全部" clearable @change="fetchBorrows">
            <el-option label="借出中" value="borrowing" />
            <el-option label="逾期" value="overdue" />
            <el-option label="已归还" value="returned" />
          </el-select>
        </el-form-item>
        <el-form-item label="搜索书名">
          <el-input v-model="filters.search" placeholder="书名" clearable @clear="fetchBorrows" @keyup.enter="fetchBorrows" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="fetchBorrows">查询</el-button>
          <el-button @click="resetFilters">重置</el-button>
        </el-form-item>
      </el-form>

      <!-- 表格 -->
      <el-table :data="borrows" v-loading="loading" border style="width: 100%">
        <el-table-column prop="id" label="记录ID" width="80" />
        <el-table-column label="书名 / 会员" min-width="250">
          <template #default="{ row }">
            <div><b>{{ row.book_title }}</b></div>
            <div class="muted">{{ row.member_code }} - {{ row.member_name }}</div>
          </template>
        </el-table-column>
        <el-table-column prop="borrow_date" label="借出日期" width="110" />
        <el-table-column prop="due_date" label="应还日期" width="110" />
        <el-table-column prop="return_date" label="归还日期" width="110">
          <template #default="{ row }">
            {{ row.return_date || '-' }}
          </template>
        </el-table-column>
        <el-table-column label="状态" width="90">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">
              {{ row.status_display }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="220" fixed="right">
          <template #default="{ row }">
            <el-button
              v-if="!row.return_date"
              size="small"
              type="success"
              @click="handleReturn(row)"
            >
              <el-icon><Check /></el-icon>
              归还
            </el-button>
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
        @current-change="fetchBorrows"
        @size-change="fetchBorrows"
        style="margin-top: 20px; justify-content: flex-end"
      />
    </el-card>

    <!-- 新增借阅对话框 -->
    <el-dialog
      v-model="dialogVisible"
      title="新增借阅"
      width="600px"
      @close="resetForm"
    >
      <el-form :model="form" :rules="rules" ref="formRef" label-width="100px">
        <el-form-item label="会员" prop="member">
          <el-select v-model="form.member" placeholder="请选择会员" filterable style="width: 100%">
            <el-option
              v-for="m in memberOptions"
              :key="m.id"
              :label="`${m.code} - ${m.name}`"
              :value="m.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="书籍" prop="book">
          <el-select v-model="form.book" placeholder="请选择书籍" filterable style="width: 100%">
            <el-option
              v-for="b in bookOptions"
              :key="b.id"
              :label="`${b.title} (可借:${b.available})`"
              :value="b.id"
              :disabled="b.available <= 0"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="借出日期" prop="borrow_date">
          <el-date-picker v-model="form.borrow_date" type="date" value-format="YYYY-MM-DD" style="width: 100%" />
        </el-form-item>
        <el-form-item label="应还日期" prop="due_date">
          <el-date-picker v-model="form.due_date" type="date" value-format="YYYY-MM-DD" style="width: 100%" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="form.note" type="textarea" :rows="2" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitting">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Check } from '@element-plus/icons-vue'
import { borrowApi, bookApi } from '@/api/borrow'
import { memberApi } from '@/api/member'

const loading = ref(false)
const submitting = ref(false)
const borrows = ref([])
const memberOptions = ref([])
const bookOptions = ref([])
const dialogVisible = ref(false)
const formRef = ref(null)

const filters = reactive({
  member: '',
  status: '',
  search: ''
})

const pagination = reactive({
  page: 1,
  size: 20,
  total: 0
})

const form = reactive({
  member: '',
  book: '',
  borrow_date: new Date().toISOString().split('T')[0],
  due_date: '',
  note: ''
})

const rules = {
  member: [{ required: true, message: '请选择会员', trigger: 'change' }],
  book: [{ required: true, message: '请选择书籍', trigger: 'change' }],
  borrow_date: [{ required: true, message: '请选择借出日期', trigger: 'change' }],
  due_date: [{ required: true, message: '请选择应还日期', trigger: 'change' }]
}

const getStatusType = (status) => {
  const types = { borrowing: 'warning', overdue: 'danger', returned: 'success' }
  return types[status] || 'info'
}

const fetchBorrows = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      page_size: pagination.size,
      member: filters.member || undefined,
      status: filters.status || undefined,
      search: filters.search || undefined
    }
    const res = await borrowApi.getList(params)
    borrows.value = res.results || res
    pagination.total = res.count || res.length
  } catch (error) {
    ElMessage.error('获取借阅列表失败')
  } finally {
    loading.value = false
  }
}

const fetchMembers = async () => {
  try {
    const res = await memberApi.getList({ page_size: 1000 })
    memberOptions.value = res.results || res
  } catch (error) {
    console.error('获取会员列表失败', error)
  }
}

const fetchBooks = async () => {
  try {
    const res = await bookApi.getList({ page_size: 1000 })
    bookOptions.value = res.results || res
  } catch (error) {
    console.error('获取书籍列表失败', error)
  }
}

const resetFilters = () => {
  filters.member = ''
  filters.status = ''
  filters.search = ''
  fetchBorrows()
}

const showAddDialog = () => {
  const today = new Date()
  const dueDate = new Date(today)
  dueDate.setDate(dueDate.getDate() + 30)

  form.member = ''
  form.book = ''
  form.borrow_date = today.toISOString().split('T')[0]
  form.due_date = dueDate.toISOString().split('T')[0]
  form.note = ''
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
    await borrowApi.create(form)
    ElMessage.success('借阅创建成功')
    dialogVisible.value = false
    fetchBorrows()
    fetchBooks() // 更新库存
  } catch (error) {
    ElMessage.error('创建失败')
  } finally {
    submitting.value = false
  }
}

const handleReturn = async (row) => {
  try {
    await ElMessageBox.confirm(`确认归还《${row.book_title}》吗？`, '提示', {
      type: 'info'
    })
    await borrowApi.returnBook(row.id, { note: '' })
    ElMessage.success('归还成功')
    fetchBorrows()
    fetchBooks()
  } catch {
    // 取消操作
  }
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm(`确定删除该借阅记录吗？`, '警告', {
      type: 'warning'
    })
    await borrowApi.delete(row.id)
    ElMessage.success('删除成功')
    fetchBorrows()
  } catch {
    // 取消操作
  }
}

onMounted(() => {
  fetchBorrows()
  fetchMembers()
  fetchBooks()
})
</script>

<style scoped>
.borrows {
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

.muted {
  color: #909399;
  font-size: var(--font-size-sm);
}
</style>
