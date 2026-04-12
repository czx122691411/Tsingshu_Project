<template>
  <div class="dashboard">
    <el-row :gutter="20">
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon" style="background: #409eff">
              <el-icon :size="32"><User /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.members?.total || 0 }}</div>
              <div class="stat-label">会员总数</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon" style="background: #67c23a">
              <el-icon :size="32"><SuccessFilled /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.members?.active || 0 }}</div>
              <div class="stat-label">有效会员</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon" style="background: #e6a23c">
              <el-icon :size="32"><WarningFilled /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.members?.expiring || 0 }}</div>
              <div class="stat-label">即将到期</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon" style="background: #f56c6c">
              <el-icon :size="32"><Reading /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.borrows?.borrowing || 0 }}</div>
              <div class="stat-label">借出中</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px">
      <el-col :span="12">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>会员状态分布</span>
            </div>
          </template>
          <div class="status-list">
            <div class="status-item">
              <span class="status-label">有效会员</span>
              <el-tag type="success">{{ stats.members?.active || 0 }}</el-tag>
            </div>
            <div class="status-item">
              <span class="status-label">即将到期</span>
              <el-tag type="warning">{{ stats.members?.expiring || 0 }}</el-tag>
            </div>
            <div class="status-item">
              <span class="status-label">已到期</span>
              <el-tag type="danger">{{ stats.members?.expired || 0 }}</el-tag>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>借阅统计</span>
            </div>
          </template>
          <div class="status-list">
            <div class="status-item">
              <span class="status-label">借出中</span>
              <el-tag type="warning">{{ stats.borrows?.borrowing || 0 }}</el-tag>
            </div>
            <div class="status-item">
              <span class="status-label">逾期未还</span>
              <el-tag type="danger">{{ stats.borrows?.overdue || 0 }}</el-tag>
            </div>
            <div class="status-item">
              <span class="status-label">书籍总数</span>
              <el-tag type="info">{{ stats.books?.total || 0 }}</el-tag>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { User, SuccessFilled, WarningFilled, Reading } from '@element-plus/icons-vue'
import { statsApi } from '@/api/borrow'

const stats = ref({})

const fetchStats = async () => {
  try {
    stats.value = await statsApi.getDashboard()
  } catch (error) {
    console.error('获取统计数据失败', error)
  }
}

onMounted(() => {
  fetchStats()
})
</script>

<style scoped>
.dashboard {
  padding: 0;
}

.stat-card {
  cursor: pointer;
  transition: all 0.3s;
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.12);
}

.stat-content {
  display: flex;
  align-items: center;
  gap: 20px;
}

.stat-icon {
  width: 64px;
  height: 64px;
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 32px;
  font-weight: bold;
  color: #303133;
}

.stat-label {
  font-size: var(--font-size-sm);
  color: #909399;
  margin-top: 8px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 500;
  font-size: var(--font-size-lg);
}

.status-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.status-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  background: #f5f7fa;
  border-radius: var(--radius-md);
}

.status-label {
  font-size: var(--font-size-base);
  color: #606266;
}
</style>
