<template>
  <el-container class="layout-container">
    <el-aside width="240px">
      <div class="logo">
        <h3>会员管理</h3>
      </div>
      <el-menu
        :default-active="activeMenu"
        router
        background-color="#304156"
        text-color="#bfcbd9"
        active-text-color="#409eff"
      >
        <el-menu-item index="/dashboard">
          <el-icon><DataAnalysis /></el-icon>
          <span>仪表盘</span>
        </el-menu-item>
        <el-menu-item index="/members">
          <el-icon><User /></el-icon>
          <span>会员管理</span>
        </el-menu-item>
        <el-menu-item index="/borrows">
          <el-icon><Reading /></el-icon>
          <span>借阅管理</span>
        </el-menu-item>
        <el-menu-item index="/books">
          <el-icon><Collection /></el-icon>
          <span>书籍管理</span>
        </el-menu-item>
        <!-- 新增：活动管理菜单 -->
        <el-sub-menu index="activities">
          <template #title>
            <el-icon><Calendar /></el-icon>
            <span>活动管理</span>
          </template>
          <el-menu-item index="/activities">
            <el-icon><List /></el-icon>
            <span>活动列表</span>
          </el-menu-item>
          <el-menu-item index="/activities/summary">
            <el-icon><DataLine /></el-icon>
            <span>会员统计</span>
          </el-menu-item>
          <el-menu-item index="/activities/calendar">
            <el-icon><Calendar /></el-icon>
            <span>活动日历</span>
          </el-menu-item>
        <el-menu-item index="/activities/types">
         <el-icon><PriceTag /></el-icon>
           <span>活动类型</span>
        </el-menu-item>
        </el-sub-menu>
      </el-menu>
    </el-aside>
    <el-container>
      <el-header>
        <div class="header-content">
          <span class="title">{{ pageTitle }}</span>
          <div class="user-info">
            <el-dropdown>
              <span class="el-dropdown-link">
                <el-icon><UserFilled /></el-icon>
                {{ authStore.user?.username }}
                <el-icon><ArrowDown /></el-icon>
              </span>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item @click="handleLogout">
                    <el-icon><SwitchButton /></el-icon>
                    退出登录
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
        </div>
      </el-header>
      <el-main>
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessageBox, ElMessage } from 'element-plus'
import {
  DataAnalysis, User, Reading, Collection,
  UserFilled, ArrowDown, SwitchButton,
  Calendar, List, DataLine,PriceTag
} from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const titles = {
  '/dashboard': '仪表盘',
  '/members': '会员管理',
  '/borrows': '借阅管理',
  '/books': '书籍管理',
  '/activities': '活动列表',
  '/activities/summary': '会员活动统计',
  '/activities/calendar': '活动日历',
  '/activities/types': '活动类型管理'
}

const activeMenu = computed(() => route.path)
const pageTitle = computed(() => titles[route.path] || '会员管理系统')

const handleLogout = async () => {
  try {
    await ElMessageBox.confirm('确定要退出登录吗？', '提示', {
      type: 'warning'
    })
    authStore.logout()
    ElMessage.success('已退出登录')
    router.push('/login')
  } catch {
    // 取消操作
  }
}
</script>

<style scoped>
.layout-container {
  height: 100vh;
}

.el-aside {
  background-color: #304156;
  color: #fff;
}

.logo {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #2b3a4a;
}

.logo h3 {
  margin: 0;
  color: #fff;
  font-size: 20px;
}

.el-header {
  background-color: #fff;
  border-bottom: 1px solid #e6e6e6;
  display: flex;
  align-items: center;
  padding: 0 24px;
}

.header-content {
  width: 100%;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.title {
  font-size: 20px;
  font-weight: 500;
  color: #303133;
}

.el-dropdown-link {
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  color: #606266;
  font-size: 16px;
}

.el-main {
  background-color: #f0f2f5;
  padding: 24px;
}
</style>
