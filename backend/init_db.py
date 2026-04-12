#!/usr/bin/env python
"""
初始化数据库脚本
创建管理员用户和示例数据
"""
import os
import sys
import django

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'member_system.settings')
django.setup()

from apps.users.models import User
from apps.members.models import Member, Payment
from apps.borrows.models import Book, Borrow
from datetime import date, timedelta


def init_data():
    print("开始初始化数据...")

    # 创建管理员用户
    if not User.objects.filter(username='admin').exists():
        admin = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='admin123',
            role='admin'
        )
        print("✓ 创建管理员用户: admin / admin123")
    else:
        print("× 管理员用户已存在")

    # 创建工作人员用户
    if not User.objects.filter(username='staff').exists():
        staff = User.objects.create_user(
            username='staff',
            email='staff@example.com',
            password='staff123',
            role='staff'
        )
        print("✓ 创建工作人员用户: staff / staff123")
    else:
        print("× 工作人员用户已存在")

    # 创建示例会员
    admin_user = User.objects.get(username='admin')
    if not Member.objects.exists():
        member1 = Member.objects.create(
            code='M-0001',
            name='张三',
            phone='13800138000',
            start_date=date.today(),
            end_date=date.today() + timedelta(days=365),
            pay_date=date.today(),
            note='示例会员',
            created_by=admin_user
        )
        Payment.objects.create(
            member=member1,
            amount=365,
            pay_date=date.today(),
            note='会员费',
            created_by=admin_user
        )
        print("✓ 创建示例会员: 张三")
    else:
        print("× 会员数据已存在")

    # 创建示例书籍
    if not Book.objects.exists():
        Book.objects.create(
            title='三体',
            author='刘慈欣',
            isbn='9787536692930',
            total=3,
            note='科幻小说'
        )
        Book.objects.create(
            title='活着',
            author='余华',
            isbn='9787503365582',
            total=2,
            note='现代文学'
        )
        print("✓ 创建示例书籍: 三体、活着")
    else:
        print("× 书籍数据已存在")

    print("\n初始化完成！")
    print("\n登录信息:")
    print("  管理员: admin / admin123")
    print("  工作人员: staff / staff123")


if __name__ == '__main__':
    init_data()
