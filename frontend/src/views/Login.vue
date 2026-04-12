<template>
  <div class="login-container">
    <el-card class="login-card">
      <template #header>
        <h2>会员管理系统</h2>
      </template>
      <el-form :model="form" :rules="rules" ref="formRef" label-width="80px">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="form.username" placeholder="请输入用户名" />
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input v-model="form.password" type="password" placeholder="请输入密码" @keyup.enter="handleLogin" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleLogin" :loading="loading" style="width: 100%">
            登录
          </el-button>
        </el-form-item>
      </el-form>
      <div class="tips">
        <p>默认账号:</p>
        <p>管理员: admin / admin123</p>
        <p>工作人员: staff / staff123</p>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const formRef = ref(null)
const loading = ref(false)
const form = ref({
  username: '',
  password: ''
})

const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }]
}

const handleLogin = async () => {
  const valid = await formRef.value?.validate()
  if (!valid) return

  loading.value = true
  try {
    await authStore.login(form.value)
    ElMessage.success('登录成功')
    router.push('/')
  } catch (error) {
    ElMessage.error('登录失败，请检查用户名和密码')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.login-card {
  width: 480px;
}

.login-card :deep(.el-card__header) {
  text-align: center;
  background: #f5f7fa;
  padding: 24px;
}

.login-card h2 {
  margin: 0;
  color: #303133;
  font-size: 24px;
}

.tips {
  margin-top: 24px;
  padding: 20px;
  background: #f5f7fa;
  border-radius: var(--radius-md);
  font-size: var(--font-size-sm);
  color: #909399;
  text-align: center;
  line-height: 2;
}

.tips p {
  margin: 8px 0;
}
</style>
