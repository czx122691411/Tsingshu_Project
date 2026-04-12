# 会员管理系统 - 生产环境上线清单

## 📋 总体流程

```
准备阶段 → 购买阶段 → 部署阶段 → 测试阶段 → 上线阶段
   ↓         ↓         ↓         ↓         ↓
  1天      1-2天     2-3小时     1小时     30分钟
```

**总耗时**：2-3天（主要是实名认证等待时间）
**总成本**：约¥1200-1500/年

---

## 🎯 第一阶段：准备阶段（1天）

### 1.1 确定基本信息

- [ ] **确定域名名称**
  - 准备3-5个备选名称
  - 格式：yourname.com / bookstore.com

- [ ] **确定服务器配置**
  - 推荐：2核4GB，40GB SSD，3Mbps
  - 预算：¥100-150/月

- [ ] **准备注册信息**
  - 身份证（域名实名认证用）
  - 手机号
  - 邮箱

### 1.2 创建必要账号

- [ ] 阿里云/腾讯云账号
  - 网址：https://www.aliyun.com 或 https://cloud.tencent.com
  - 手机号注册
  - 实名认证（需要身份证）

- [ ] GitHub账号（可选）
  - 用于代码管理和CI/CD

---

## 🛒 第二阶段：购买阶段（1-2天）

### 2.1 购买云服务器

#### 阿里云购买

**方式一：新用户优惠（推荐）**
```
1. 访问：https://www.aliyun.com/daily-act/ecs/activity_selection
2. 选择"新手入门"套餐
3. 通常是3个月免费或¥99/年
4. 立即购买
```

**方式二：正常购买**
```
1. 访问：https://www.aliyun.com/product/ecs
2. 点击"立即购买"
3. 配置选择：
   - 地域：选择最近的（杭州/北京/深圳）
   - 实例：2核4GB
   - 系统：Ubuntu 22.04 LTS
   - 带宽：3Mbps
   - 密码：设置root密码（记住！）
4. 支付
```

- [ ] 购买完成
- [ ] 记录服务器IP地址：_______________
- [ ] 测试SSH连接：
  ```bash
  ssh root@你的服务器IP
  ```

#### 配置安全组/防火墙

- [ ] 登录云控制台
- [ ] 进入"安全组"设置
- [ ] 添加入站规则：
  ```
  端口22  | SSH    | 0.0.0.0/0
  端口80  | HTTP   | 0.0.0.0/0
  端口443 | HTTPS  | 0.0.0.0/0
  ```

### 2.2 购买域名

#### 阿里云万网购买
```
1. 访问：https://wanwang.aliyun.com
2. 搜索想要的域名
3. 如果可注册，点击"加入清单"
4. 结算购买（建议1年起）
```

- [ ] 购买完成
- [ ] 记录域名：_______________
- [ ] 提交实名认证（1-3个工作日）

#### 配置域名解析

- [ ] 进入域名控制台
- [ ] 添加DNS解析记录：
  ```
  记录类型：A
  主机记录：@
  记录值：你的服务器IP

  记录类型：A
  主机记录：www
  记录值：你的服务器IP

  记录类型：A
  主机记录：api
  记录值：你的服务器IP
  ```

- [ ] 验证解析：
  ```bash
  ping yourdomain.com
  ping www.yourdomain.com
  ```

---

## 🚀 第三阶段：部署阶段（2-3小时）

### 3.1 连接服务器

```bash
# SSH连接服务器
ssh root@your_server_ip

# 输入密码后，您会看到：
# root@iZxxxxxx:~#
```

### 3.2 准备部署环境

```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装基础工具
sudo apt install -y git curl wget vim

# 安装Python 3.10
sudo apt install -y python3.10 python3-pip python3-venv

# 安装Node.js 18
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs

# 安装PostgreSQL
sudo apt install -y postgresql postgresql-contrib

# 安装Nginx
sudo apt install -y nginx
```

### 3.3 部署应用

#### 方式一：使用项目脚本（推荐）

```bash
# 1. 克隆项目
cd /var/www
sudo git clone <your-repo-url> member-management
cd member-management

# 2. 运行初始化脚本
sudo bash scripts/init.sh

# 3. 按提示输入：
#    - 域名：yourdomain.com
#    - 数据库密码：设置强密码
#    - 管理员账户：设置管理员信息

# 4. 启动服务
sudo systemctl start member-management
```

#### 方式二：手动部署（详见DEPLOYMENT.md）

### 3.4 配置SSL证书

```bash
# 安装Certbot
sudo apt install -y certbot python3-certbot-nginx

# 获取SSL证书
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com -d api.yourdomain.com

# 按提示输入邮箱，同意条款

# 验证证书
sudo certbot certificates
```

---

## ✅ 第四阶段：测试阶段（1小时）

### 4.1 功能测试

- [ ] **前端访问测试**
  - 访问：https://yourdomain.com
  - 验证：页面正常显示，样式正常

- [ ] **后端API测试**
  - 访问：https://api.yourdomain.com/api/
  - 验证：返回API信息

- [ ] **管理后台测试**
  - 访问：https://api.yourdomain.com/admin/
  - 验证：可以登录，功能正常

- [ ] **会员端测试**
  - 访问：https://yourdomain.com/member/login
  - 验证：会员可以登录

### 4.2 安全测试

- [ ] **HTTPS正常**
  - 浏览器地址栏显示锁图标
  - HTTP自动跳转到HTTPS

- [ ] **SSL证书有效**
  - 没有证书警告
  - 证书在有效期内

- [ ] **防火墙生效**
  - 只有80、443端口开放
  - 其他端口拒绝连接

### 4.3 性能测试

```bash
# 查看服务器资源使用
htop

# 查看服务状态
sudo systemctl status member-management
sudo systemctl status nginx

# 查看日志
sudo journalctl -u member-management -f
```

---

## 🌟 第五阶段：上线阶段（30分钟）

### 5.1 配置备份

- [ ] **配置自动备份**
  ```bash
  # 添加定时任务
  sudo crontab -e

  # 添加以下行（每天凌晨2点备份）
  0 2 * * * /usr/local/bin/member-backup.sh
  ```

- [ ] **测试备份恢复**
  ```bash
  # 手动触发备份
  sudo bash /var/www/member-management/scripts/backup.sh

  # 查看备份文件
  ls -lh /var/backups/member-management/
  ```

### 5.2 监控配置

- [ ] **配置日志监控**
  ```bash
  # 实时查看日志
  sudo journalctl -u member-management -f
  ```

- [ ] **配置告警（可选）**
  - 使用Sentry进行错误追踪
  - 配置邮件告警

### 5.3 发布准备

- [ ] **准备公告**
  - 系统上线公告
  - 用户使用指南

- [ ] **准备培训**
  - 管理员操作培训
  - 会员使用说明

### 5.4 正式上线

- [ ] **通知用户**
  - 发送系统上线通知
  - 分发用户手册

- [ ] **监控运行**
  - 实时监控系统状态
  - 准备处理问题

---

## 📊 成本汇总

### 初期成本

| 项目 | 费用 | 周期 |
|------|------|------|
| 云服务器 | ¥100-150 | 月 |
| 域名 | ¥50-100 | 年 |
| SSL证书 | ¥0 | 永久免费 |
| **初期总计** | **¥1200-1500** | 年 |

### 运营成本

| 项目 | 费用 | 说明 |
|------|------|------|
| 服务器 | ¥1200-1800 | 年 |
| 域名续费 | ¥50-100 | 年 |
| 带宽超出 | 按需 | 流量超出时 |
| **年度总计** | **¥1300-1900** | 年 |

---

## 🔧 日常维护清单

### 每日检查
- [ ] 检查服务状态
- [ ] 查看错误日志
- [ ] 监控服务器资源

### 每周任务
- [ ] 检查备份是否正常
- [ ] 查看系统更新
- [ ] 分析访问统计

### 每月任务
- [ ] 更新系统安全补丁
- [ ] 清理旧日志和备份
- [ ] 性能评估

---

## 📞 需要帮助？

### 文档资源
- 完整部署指南：`DEPLOYMENT.md`
- 快速入门：`QUICK_START.md`
- 项目结构：`PROJECT_STRUCTURE.md`

### 常见问题
**Q：部署失败怎么办？**
A：查看日志 `sudo journalctl -u member-management -n 50`

**Q：无法连接服务器？**
A：检查安全组规则和SSH服务状态

**Q：网站打不开？**
A：检查Nginx状态和DNS解析

**Q：数据库连接失败？**
A：检查PostgreSQL服务和密码配置

---

## 🎉 上线后

恭喜！系统已成功上线。

现在您可以：
1. 开始添加会员数据
2. 创建活动和书籍
3. 培训管理员使用
4. 邀请会员注册使用

**建议上线首周密切关注系统运行状态，及时处理问题。**

---

## 📞 技术支持

如遇到问题：
1. 查看部署文档
2. 检查日志文件
3. 参考故障排查章节

祝您运营顺利！🚀
