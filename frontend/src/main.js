import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import zhCn from 'element-plus/dist/locale/zh-cn.mjs'
import router from './router'
import App from './App.vue'

// 设置设计令牌系统
const style = document.createElement('style')
style.innerHTML = `
  :root {
    /* 设计令牌 - 间距系统（8px基准）*/
    --spacing-xs: 8px;
    --spacing-sm: 16px;
    --spacing-md: 24px;
    --spacing-lg: 32px;
    --spacing-xl: 40px;

    /* 设计令牌 - 字体系统 */
    --font-size-xs: 12px;
    --font-size-sm: 14px;
    --font-size-base: 16px;
    --font-size-lg: 18px;
    --font-size-xl: 20px;
    --font-size-xxl: 24px;
    --font-size-title: 28px;

    /* 设计令牌 - 圆角系统 */
    --radius-sm: 4px;
    --radius-md: 8px;
    --radius-lg: 12px;

    /* Element Plus 组件尺寸 */
    --el-font-size-base: 16px;
    --el-font-size-small: 14px;
    --el-font-size-large: 18px;
  }

  html {
    font-size: 16px;
  }

  body {
    font-size: var(--font-size-base);
    min-height: 100vh;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  }

  /* Element Plus 组件样式统一 */
  .el-button {
    height: 40px;
    padding: 0 20px;
    font-size: var(--font-size-base);
    border-radius: var(--radius-md);
  }

  .el-button--small {
    height: 36px;
    padding: 0 16px;
    font-size: var(--font-size-sm);
  }

  .el-button--large {
    height: 48px;
    padding: 0 24px;
    font-size: var(--font-size-lg);
  }

  .el-input__wrapper {
    padding: 8px 15px;
    border-radius: var(--radius-md);
  }

  .el-input__inner,
  .el-textarea__inner {
    font-size: var(--font-size-base);
    height: 40px;
  }

  .el-textarea__inner {
    height: auto;
    min-height: 100px;
  }

  .el-select .el-input__inner {
    height: 40px;
  }

  .el-date-editor .el-input__inner {
    height: 40px;
  }

  /* 表格样式 */
  .el-table {
    font-size: var(--font-size-base);
  }

  .el-table th,
  .el-table td {
    padding: 16px 0;
  }

  .el-table th {
    font-size: var(--font-size-base);
    font-weight: 600;
    text-align: left;
    background-color: #fafafa;
  }

  .el-table th .cell {
    font-size: var(--font-size-base) !important;
    font-weight: 600;
  }

  .el-table .cell {
    padding: 0 16px;
  }

  .el-table__header th {
    font-size: var(--font-size-base) !important;
  }

  .el-table__header th .cell {
    font-size: var(--font-size-base) !important;
  }

  /* 居中对齐的列 */
  .el-table th.is-center,
  .el-table td.is-center {
    text-align: center;
  }

  .el-table th.is-center .cell,
  .el-table td.is-center .cell {
    text-align: center;
  }

  /* 卡片样式 */
  .el-card {
    font-size: var(--font-size-base);
    border-radius: var(--radius-lg);
    border: 1px solid #ebeef5;
  }

  .el-card__header {
    padding: 20px 24px;
    font-size: var(--font-size-xl);
    font-weight: 600;
    background-color: #fafafa;
    border-bottom: 1px solid #ebeef5;
  }

  .el-card__body {
    padding: 24px;
  }

  /* 对话框样式 */
  .el-dialog {
    border-radius: var(--radius-lg);
  }

  .el-dialog__header {
    padding: 24px;
    font-size: var(--font-size-xl);
    font-weight: 600;
  }

  .el-dialog__body {
    padding: 24px;
  }

  .el-dialog__footer {
    padding: 16px 24px 24px;
  }

  /* 表单样式 */
  .el-form-item__label {
    font-size: var(--font-size-base);
    font-weight: 500;
  }

  .el-form-item {
    margin-bottom: 24px;
  }

  /* 标签样式 */
  .el-tag {
    font-size: var(--font-size-sm);
    padding: 6px 12px;
    height: auto;
    border-radius: var(--radius-sm);
  }

  /* 分页样式 */
  .el-pagination {
    font-size: var(--font-size-base);
  }

  .el-pagination button,
  .el-pagination .el-pager li {
    height: 36px;
    line-height: 36px;
    min-width: 36px;
    font-size: var(--font-size-base);
    border-radius: var(--radius-sm);
  }

  /* 菜单样式 */
  .el-menu-item {
    height: 48px;
    line-height: 48px;
    font-size: var(--font-size-base);
  }

  .el-menu-item .el-icon {
    font-size: 20px;
  }

  /* 头部样式 */
  .el-header {
    height: 60px !important;
    font-size: var(--font-size-base);
  }

  /* 侧边栏样式 */
  .el-aside {
    font-size: var(--font-size-base);
  }

  /* 主内容区 */
  .el-main {
    font-size: var(--font-size-base);
  }

  /* 下拉菜单 */
  .el-dropdown-menu__item {
    font-size: var(--font-size-base);
    padding: 10px 20px;
  }

  /* 数字输入框 */
  .el-input-number {
    height: 40px;
  }

  .el-input-number .el-input__inner {
    height: 40px;
    line-height: 40px;
  }

  .el-input-number .el-input-number__decrease,
  .el-input-number .el-input-number__increase {
    height: 19px;
    line-height: 19px;
    width: 32px;
  }

  /* 消息提示 */
  .el-message {
    font-size: var(--font-size-base);
    min-width: 320px;
    padding: 16px 20px;
    border-radius: var(--radius-md);
  }

  .el-message-box {
    font-size: var(--font-size-base);
    border-radius: var(--radius-lg);
  }

  .el-message-box__title {
    font-size: var(--font-size-xl);
  }

  .el-message-box__content {
    padding: 24px;
  }

  .el-message-box__btns {
    padding: 16px 20px 20px;
  }

  /* 图标 */
  .el-icon {
    font-size: 18px;
  }

  /* 表格单元格 */
  .el-table__cell {
    font-size: var(--font-size-base);
  }

  /* 选择器下拉 */
  .el-select-dropdown__item {
    font-size: var(--font-size-base);
    height: 40px;
    line-height: 40px;
    padding: 0 16px;
  }

  /* 日期选择器 */
  .el-picker-panel {
    font-size: var(--font-size-base);
  }

  .el-date-picker__header-label {
    font-size: var(--font-size-base);
  }

  .el-picker-panel__icon {
    font-size: 18px;
  }

  .el-picker-panel__content .el-date-table td .el-date-table-cell__text {
    font-size: var(--font-size-sm);
  }

  /* 加载状态 */
  .el-loading-mask {
    background-color: rgba(255, 255, 255, 0.9);
  }

  /* 响应式设计 */
  @media (max-width: 1440px) {
    .el-card__header {
      padding: 18px 20px;
    }
    .el-card__body {
      padding: 20px;
    }
  }

  @media (max-width: 1024px) {
    .el-table th,
    .el-table td {
      padding: 12px 0;
    }
  }
`
document.head.appendChild(style)

const app = createApp(App)

app.use(createPinia())
app.use(router)
app.use(ElementPlus, {
  locale: zhCn,
  size: 'default'
})

app.mount('#app')
