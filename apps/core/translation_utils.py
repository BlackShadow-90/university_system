"""
Custom translation utilities for when gettext compilation is not available
"""
from django.utils import translation
from django.conf import settings
import os

# Simple translation dictionary for Chinese
SIMPLE_TRANSLATIONS = {
    # Student Dashboard
    'Student Dashboard': '学生仪表板',
    'Welcome': '欢迎',
    'Academic Warning!': '学业警告！',
    'Please check your': '请查看您的',
    'Warning Center': '预警中心',
    'for details and recommended actions.': '了解详细信息和建议措施。',
    'CGPA': '累积GPA',
    'Current GPA': '当前GPA',
    'Current Courses': '当前课程',
    'Status': '状态',
    'Course': '课程',
    'Attendance': '出勤',
    'Grade': '成绩',
    'Actions': '操作',
    'View All': '查看全部',
    'No current enrollments': '暂无当前选课',
    'Quick Actions': '快速操作',
    'My Results': '我的成绩',
    'GPA / CGPA': 'GPA / 累积GPA',
    'Transcript': '成绩单',
    'Announcements': '公告',
    'No announcements': '暂无公告',
    
    # Navigation
    'Home': '首页',
    'Dashboard': '仪表板',
    'Users': '用户',
    'Students': '学生',
    'Teachers': '教师',
    'Departments': '院系',
    'Courses': '课程',
    'Enrollments': '注册',
    'Warnings': '预警',
    'Reports': '报告',
    'Settings': '设置',
    'Audit Logs': '审计日志',
    'Menu': '菜单',
    'My Courses': '我的课程',
    'Enter Marks': '录入成绩',
    'At-Risk Students': '风险学生',
    'Performance Analytics': '成绩分析',
    
    # Forms and Actions
    'Add New Student': '添加新学生',
    'Search': '搜索',
    'All Status': '所有状态',
    'Active': '在读',
    'Inactive': '休学',
    'Suspended': '停学',
    'Graduated': '已毕业',
    'All Departments': '所有院系',
    'Batch Year': '年级',
    'Year...': '年份...',
    'Per Page': '每页显示',
    'Apply Filters': '应用筛选',
    'Clear Filters': '清除筛选',
    'Student ID': '学号',
    'Name': '姓名',
    'Program': '专业',
    'View': '查看',
    'Edit': '编辑',
    'Delete': '删除',
    'Add Teacher': '添加教师',
    'Edit Teacher': '编辑教师',
    'Account Information': '账户信息',
    'Email': '邮箱',
    'Full Name (English)': '英文姓名',
    'Full Name (Chinese)': '中文姓名',
    'Phone Number': '电话号码',
    'Employment Information': '就业信息',
    'Teacher Number': '教师编号',
    'Select Department': '选择院系',
    'Title': '职称',
    'Select Title': '选择职称',
    'Lecturer': '讲师',
    'Assistant Professor': '助理教授',
    'Associate Professor': '副教授',
    'Professor': '教授',
    'Visiting Professor': '客座教授',
    'Employment Type': '就业类型',
    'Full Time': '全职',
    'Part Time': '兼职',
    'Contract': '合同制',
    'Specialization': '专业领域',
    'Join Date': '入职日期',
    'On Leave': '休假',
    'Retired': '退休',
    'Save Teacher': '保存教师',
    'Cancel': '取消',
    'Back': '返回',
    
    # Bulk Enrollment
    'Bulk Student Enrollment': '批量学生注册',
    'Back to Enrollments': '返回注册管理',
    'Enroll Multiple Students': '注册多名学生',
    'Select Course': '选择课程',
    'Choose a course...': '选择课程...',
    'Course Info': '课程信息',
    'Select Students': '选择学生',
    'Select All': '全选',
    'Deselect All': '取消全选',
    'No active students found': '未找到在读学生',
    'students selected': '名学生已选择',
    'Clear': '清除',
    'Enroll Selected Students': '注册选中学生',
    'Semester:': '学期：',
    'Credits:': '学分：',
    'Instructor:': '教师：',
    
    # General
    'Profile': '个人资料',
    'Change Password': '修改密码',
    'Logout': '退出登录',
    'Login': '登录',
    'All rights reserved.': '版权所有。',
    'Bilingual Academic Performance Management System': '双语学业成绩管理系统',
}

def simple_trans(text):
    """Simple translation function that works without gettext compilation"""
    current_language = translation.get_language()
    if current_language == 'zh-hans' and text in SIMPLE_TRANSLATIONS:
        return SIMPLE_TRANSLATIONS[text]
    return text

# Template filter
from django import template
register = template.Library()

@register.filter
def simple_translate(text):
    return simple_trans(text)
