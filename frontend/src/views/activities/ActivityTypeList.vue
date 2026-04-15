  <template>
    <div class="activity-types">
      <el-card>
        <template #header>
          <div class="card-header">
            <span>活动类型管理</span>
            <el-button type="primary" @click="showAddDialog" v-if="isAdmin">
              <el-icon><Plus /></el-icon>
              新增类型
            </el-button>
          </div>
        </template>

        <!-- 筛选 -->
        <el-form :inline="true" :model="filters" class="filter-form">
          <el-form-item label="状态">
            <el-select v-model="filters.is_active" placeholder="全部" clearable @change="fetchTypes">
              <el-option label="启用" :value="true" />
              <el-option label="禁用" :value="false" />
            </el-select>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="fetchTypes">查询</el-button>
            <el-button @click="resetFilters">重置</el-button>
          </el-form-item>
        </el-form>

        <!-- 表格 -->
        <el-table :data="types" v-loading="loading" border style="width: 100%">
          <el-table-column prop="name" label="类型名称" min-width="120" />
          <el-table-column prop="code" label="代码" width="150" />
          <el-table-column label="颜色" width="100">
            <template #default="{ row }">
              <div class="color-preview">
                <span :style="{ backgroundColor: row.color }" class="color-block"></span>
                <span>{{ row.color }}</span>
              </div>
            </template>
          </el-table-column>
          <el-table-column prop="description" label="描述" min-width="200" show-overflow-tooltip />
          <el-table-column label="状态" width="80" align="center">
            <template #default="{ row }">
              <el-tag :type="row.is_active ? 'success' : 'info'">
                {{ row.is_active ? '启用' : '禁用' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="活动数量" width="100" align="center">
            <template #default="{ row }">
              {{ row.activity_count || 0 }}
            </template>
          </el-table-column>
          <el-table-column label="操作" width="150" align="center" fixed="right">
            <template #default="{ row }">
              <el-button size="small" type="primary" @click="showEditDialog(row)" v-if="isAdmin">
                <el-icon><Edit /></el-icon>
                <span>编辑</span>
              </el-button>
              <el-button size="small" type="danger" @click="handleDelete(row)" v-if="isAdmin">
                <el-icon><Delete /></el-icon>
                <span>删除</span>
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-card>

      <!-- 新增/编辑对话框 -->
      <el-dialog
        v-model="dialogVisible"
        :title="dialogTitle"
        width="500px"
        @close="resetForm"
      >
        <el-form :model="form" :rules="rules" ref="formRef" label-width="100px">
          <el-form-item label="类型名称" prop="name">
            <el-input v-model="form.name" placeholder="请输入类型名称" />
          </el-form-item>
          <el-form-item label="代码" prop="code">
            <el-input v-model="form.code" placeholder="请输入英文代码" />
          </el-form-item>
          <el-form-item label="颜色" prop="color">
            <el-color-picker v-model="form.color" />
            <el-input v-model="form.color" placeholder="选择或输入颜色值" style="width: 200px; margin-left: 10px" />
          </el-form-item>
          <el-form-item label="描述">
            <el-input v-model="form.description" type="textarea" :rows="3" placeholder="请输入描述" />
          </el-form-item>
          <el-form-item label="状态">
            <el-switch v-model="form.is_active" active-text="启用" inactive-text="禁用" />
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
  import { Plus, Edit, Delete } from '@element-plus/icons-vue'
  import { activityApi } from '@/api/activities'
  import { useAuthStore } from '@/stores/auth'

  const authStore = useAuthStore()
  const isAdmin = computed(() => authStore.user?.role === 'admin')

  const loading = ref(false)
  const submitting = ref(false)
  const types = ref([])
  const dialogVisible = ref(false)
  const formRef = ref(null)
  const isEdit = ref(false)

  const filters = reactive({
    is_active: ''
  })

  const form = reactive({
    name: '',
    code: '',
    color: '#409eff',
    description: '',
    is_active: true
  })

  const rules = {
    name: [{ required: true, message: '请输入类型名称', trigger: 'blur' }],
    code: [{ required: true, message: '请输入代码', trigger: 'blur' }],
    color: [{ required: true, message: '请选择颜色', trigger: 'change' }]
  }

  const dialogTitle = computed(() => isEdit.value ? '编辑活动类型' : '新增活动类型')

  const fetchTypes = async () => {
    loading.value = true
    try {
      const params = {}
      if (filters.is_active !== '') {
        params.is_active = filters.is_active
      }
      const res = await activityApi.getTypes(params)
      types.value = res.results || res
    } catch (error) {
      ElMessage.error('获取活动类型失败')
    } finally {
      loading.value = false
    }
  }

  const resetFilters = () => {
    filters.is_active = ''
    fetchTypes()
  }

  const showAddDialog = () => {
    isEdit.value = false
    Object.assign(form, {
      name: '',
      code: '',
      color: '#409eff',
      description: '',
      is_active: true
    })
    dialogVisible.value = true
  }

  const showEditDialog = (row) => {
    isEdit.value = true
    Object.assign(form, {
      id: row.id,
      name: row.name,
      code: row.code,
      color: row.color,
      description: row.description,
      is_active: row.is_active
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
      if (isEdit.value) {
        await activityApi.updateType(form.id, form)
        ElMessage.success('更新成功')
      } else {
        await activityApi.createType(form)
        ElMessage.success('创建成功')
      }
      dialogVisible.value = false
      fetchTypes()
    } catch (error) {
      ElMessage.error(isEdit.value ? '更新失败' : '创建失败')
    } finally {
      submitting.value = false
    }
  }

  const handleDelete = async (row) => {
    try {
      await ElMessageBox.confirm(`确定删除活动类型"${row.name}"吗？`, '警告', {
        type: 'warning'
      })
      await activityApi.deleteType(row.id)
      ElMessage.success('删除成功')
      fetchTypes()
    } catch {
      // 取消删除
    }
  }

  onMounted(() => {
    fetchTypes()
  })
  </script>

  <style scoped>
  .activity-types {
    height: 100%;
  }

  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .card-header span {
    font-size: 18px;
    font-weight: 600;
  }

  .filter-form {
    margin-bottom: 20px;
  }

  .filter-form :deep(.el-form-item) {
    margin-bottom: 0;
  }

  .color-preview {
    display: flex;
    align-items: center;
    gap: 10px;
  }

  .color-block {
    width: 30px;
    height: 20px;
    border: 1px solid #dcdfe6;
    border-radius: 4px;
  }
  </style>
