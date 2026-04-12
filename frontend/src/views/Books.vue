<template>
  <div class="books">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>书籍管理</span>
          <el-button type="primary" @click="showAddDialog">
            <el-icon><Plus /></el-icon>
            新增书籍
          </el-button>
        </div>
      </template>

      <!-- 筛选 -->
      <el-form :inline="true" :model="filters" class="filter-form">
        <el-form-item label="搜索">
          <el-input v-model="filters.search" placeholder="书名/作者/ISBN" clearable @clear="fetchBooks" @keyup.enter="fetchBooks" />
        </el-form-item>
        <el-form-item label="库存状态">
          <el-select v-model="filters.available" placeholder="全部" clearable @change="fetchBooks">
            <el-option label="有库存" value="yes" />
            <el-option label="无库存" value="no" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="fetchBooks">查询</el-button>
          <el-button @click="resetFilters">重置</el-button>
        </el-form-item>
      </el-form>

      <!-- 表格 -->
      <el-table :data="books" v-loading="loading" border style="width: 100%">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column label="书籍信息" min-width="300">
          <template #default="{ row }">
            <div><b>{{ row.title }}</b></div>
            <div class="muted">作者: {{ row.author || '-' }}</div>
            <div class="muted" v-if="row.isbn">ISBN: {{ row.isbn }}</div>
          </template>
        </el-table-column>
        <el-table-column prop="total" label="总库存" width="100" align="center" />
        <el-table-column label="可借" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="row.available > 0 ? 'success' : 'danger'">
              {{ row.available }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
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
        @current-change="fetchBooks"
        @size-change="fetchBooks"
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
        <el-form-item label="书名" prop="title">
          <el-input v-model="form.title" />
        </el-form-item>
        <el-form-item label="作者">
          <el-input v-model="form.author" />
        </el-form-item>
        <el-form-item label="ISBN">
          <el-input v-model="form.isbn" />
        </el-form-item>
        <el-form-item label="总库存" prop="total">
          <el-input-number v-model="form.total" :min="0" />
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
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { bookApi } from '@/api/borrow'

const loading = ref(false)
const submitting = ref(false)
const books = ref([])
const dialogVisible = ref(false)
const formRef = ref(null)
const isEdit = ref(false)

const filters = reactive({
  search: '',
  available: ''
})

const pagination = reactive({
  page: 1,
  size: 20,
  total: 0
})

const form = reactive({
  id: null,
  title: '',
  author: '',
  isbn: '',
  total: 1,
  note: ''
})

const rules = {
  title: [{ required: true, message: '请输入书名', trigger: 'blur' }],
  total: [{ required: true, message: '请输入库存数量', trigger: 'change' }]
}

const dialogTitle = computed(() => isEdit.value ? '编辑书籍' : '新增书籍')

const fetchBooks = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      page_size: pagination.size,
      search: filters.search || undefined
    }
    const res = await bookApi.getList(params)
    let booksData = res.results || res

    // 前端过滤库存状态
    if (filters.available === 'yes') {
      booksData = booksData.filter(b => b.available > 0)
    } else if (filters.available === 'no') {
      booksData = booksData.filter(b => b.available <= 0)
    }

    books.value = booksData
    pagination.total = res.count || res.length
  } catch (error) {
    ElMessage.error('获取书籍列表失败')
  } finally {
    loading.value = false
  }
}

const resetFilters = () => {
  filters.search = ''
  filters.available = ''
  fetchBooks()
}

const showAddDialog = () => {
  isEdit.value = false
  Object.assign(form, {
    id: null,
    title: '',
    author: '',
    isbn: '',
    total: 1,
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
    if (isEdit.value) {
      await bookApi.update(form.id, form)
      ElMessage.success('更新成功')
    } else {
      await bookApi.create(form)
      ElMessage.success('创建成功')
    }
    dialogVisible.value = false
    fetchBooks()
  } catch (error) {
    ElMessage.error(isEdit.value ? '更新失败' : '创建失败')
  } finally {
    submitting.value = false
  }
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm(`确定删除《${row.title}》吗？`, '警告', {
      type: 'warning'
    })
    await bookApi.delete(row.id)
    ElMessage.success('删除成功')
    fetchBooks()
  } catch {
    // 取消操作
  }
}

onMounted(() => {
  fetchBooks()
})
</script>

<style scoped>
.books {
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
