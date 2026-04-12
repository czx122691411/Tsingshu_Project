<template>
  <div class="member-login-container">
    <div class="login-card">
      <div class="logo-section">
        <h1 class="store-name">三味书屋</h1>
        <p class="subtitle">会员中心</p>
      </div>

      <el-form :model="loginForm" :rules="rules" ref="formRef" @submit.prevent="handleLogin">
        <el-form-item prop="code">
          <el-input
            v-model="loginForm.code"
            placeholder="请输入会员号"
            prefix-icon="User"
            size="large"
            clearable
          />
        </el-form-item>

        <el-form-item prop="phoneLast4">
          <el-input
            v-model="loginForm.phoneLast4"
            placeholder="请输入手机号后4位"
            prefix-icon="Iphone"
            size="large"
            maxlength="4"
            clearable
          />
        </el-form-item>

        <el-form-item>
          <el-button
            type="primary"
            size="large"
            :loading="loading"
            @click="handleLogin"
            class="login-btn"
          >
            登录
          </el-button>
        </el-form-item>
      </el-form>

      <div class="tips">
        <p>💡 登录提示：</p>
        <p>• 会员号：例如 M-0001</p>
        <p>• 手机号后4位：用于验证身份</p>
      </div>

      <div class="staff-login-link">
        <router-link to="/login">员工登录</router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { memberAuthApi } from '@/api/member-auth'

const router = useRouter()
const loading = ref(false)
const formRef = ref(null)

const loginForm = reactive({
  code: '',
  phoneLast4: ''
})

const rules = {
  code: [
    { required: true, message: '请输入会员号', trigger: 'blur' },
    { pattern: /^M-\d+$/, message: '会员号格式不正确（如：M-0001）', trigger: 'blur' }
  ],
  phoneLast4: [
    { required: true, message: '请输入手机号后4位', trigger: 'blur' },
    { pattern: /^\d{4}$/, message: '请输入4位数字', trigger: 'blur' }
  ]
}

const handleLogin = async () => {
  // 去除前后空格
  loginForm.code = loginForm.code.trim()
  loginForm.phoneLast4 = loginForm.phoneLast4.trim()

  const valid = await formRef.value?.validate()
  if (!valid) return

  loading.value = true
  try {
    const res = await memberAuthApi.login(loginForm.code, loginForm.phoneLast4)

    // 保存token和会员信息
    localStorage.setItem('memberToken', res.access)
    localStorage.setItem('memberRefresh', res.refresh)
    localStorage.setItem('memberInfo', JSON.stringify(res.member))

    ElMessage.success('登录成功')

    // 跳转到会员中心
    router.push('/member')
  } catch (error) {
    ElMessage.error(error.response?.data?.error || '登录失败')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.member-login-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}

.login-card {
  width: 100%;
  max-width: 400px;
  background: #fff;
  border-radius: 16px;
  padding: 40px 30px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}

.logo-section {
  text-align: center;
  margin-bottom: 40px;
}

.store-name {
  font-size: 32px;
  font-weight: bold;
  color: #333;
  margin: 0 0 10px 0;
}

.subtitle {
  font-size: 16px;
  color: #666;
  margin: 0;
}

.el-form-item {
  margin-bottom: 24px;
}

.login-btn {
  width: 100%;
  height: 50px;
  font-size: 18px;
  font-weight: 600;
}

.tips {
  margin-top: 30px;
  padding: 15px;
  background: #f5f7fa;
  border-radius: 8px;
  font-size: 14px;
  color: #606266;
  line-height: 1.8;
}

.tips p {
  margin: 0;
}

.staff-login-link {
  text-align: center;
  margin-top: 20px;
}

.staff-login-link a {
  color: #409eff;
  text-decoration: none;
  font-size: 14px;
}

.staff-login-link a:hover {
  text-decoration: underline;
}
</style>
