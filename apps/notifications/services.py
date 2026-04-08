"""
Notification service for creating and managing notifications
"""
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

from apps.notifications.models import Notification
from apps.accounts.models import User


class NotificationService:
    """Service class for managing notifications"""
    
    @staticmethod
    def send_notification(recipient, title_en, content_en, notification_type='system', 
                          priority='normal', sender=None, related_object=None, 
                          action_url=None, title_zh=None, content_zh=None):
        """
        Create and send a notification to a user
        """
        notification = Notification.objects.create(
            recipient=recipient,
            sender=sender,
            title_en=title_en,
            title_zh=title_zh or title_en,
            content_en=content_en,
            content_zh=content_zh or content_en,
            notification_type=notification_type,
            priority=priority,
            action_url=action_url
        )
        
        # Set related object if provided
        if related_object:
            notification.related_object_type = related_object.__class__.__name__
            notification.related_object_id = related_object.id
            notification.save(update_fields=['related_object_type', 'related_object_id'])
        
        return notification
    
    @staticmethod
    def notify_grade_published(student_user, enrollment, final_result):
        """Send grade published notification"""
        course_title = enrollment.course_offering.course.get_title()
        
        return NotificationService.send_notification(
            recipient=student_user,
            title_en=f"Grade Published: {course_title}",
            title_zh=f"成绩已发布: {course_title}",
            content_en=f"Your grade for {course_title} has been published. "
                      f"You received {final_result.letter_grade} ({final_result.total_score:.2f}%)",
            content_zh=f"您在 {course_title} 的成绩已发布。 "
                      f"您获得了 {final_result.letter_grade} ({final_result.total_score:.2f}%)",
            notification_type='grade',
            priority='high',
            related_object=final_result,
            action_url=f'/student-portal/results/'
        )
    
    @staticmethod
    def notify_attendance_risk(student_user, enrollment, attendance_percentage):
        """Send attendance risk warning"""
        course_title = enrollment.course_offering.course.get_title()
        
        return NotificationService.send_notification(
            recipient=student_user,
            title_en="Attendance Warning",
            title_zh="出勤警告",
            content_en=f"Your attendance in {course_title} is {attendance_percentage:.1f}%. "
                      f"Please maintain regular attendance to avoid academic penalties.",
            content_zh=f"您在 {course_title} 的出勤率为 {attendance_percentage:.1f}%。 "
                      f"请保持定期出勤以避免学术处罚。",
            notification_type='attendance',
            priority='high',
            related_object=enrollment,
            action_url=f'/student-portal/attendance/'
        )
    
    @staticmethod
    def notify_academic_warning(student_user, warning):
        """Send academic warning notification"""
        return NotificationService.send_notification(
            recipient=student_user,
            title_en="Academic Warning Issued",
            title_zh="学术警告已发布",
            content_en=f"An academic warning has been issued for {warning.semester.display_name}. "
                      f"Warning Level: {warning.warning_level}. "
                      f"Please check the warning center for details.",
            content_zh=f"已为 {warning.semester.display_name} 发布学术警告。 "
                      f"警告级别: {warning.warning_level}。 "
                      f"请查看警告中心了解详情。",
            notification_type='warning',
            priority='urgent',
            related_object=warning,
            action_url=f'/student-portal/warnings/'
        )
    
    @staticmethod
    def notify_announcement(recipients, announcement, sender=None):
        """Send announcement notification to multiple users"""
        notifications = []
        
        for recipient in recipients:
            notification = NotificationService.send_notification(
                recipient=recipient,
                title_en=announcement.get_title('en'),
                title_zh=announcement.get_title('zh'),
                content_en=announcement.get_content('en'),
                content_zh=announcement.get_content('zh'),
                notification_type='announcement',
                priority=announcement.priority if hasattr(announcement, 'priority') else 'normal',
                sender=sender,
                related_object=announcement
            )
            notifications.append(notification)
        
        return notifications
    
    @staticmethod
    def notify_course_enrollment(student_user, enrollment):
        """Send course enrollment confirmation"""
        course_title = enrollment.course_offering.course.get_title()
        semester_name = enrollment.course_offering.semester.display_name if enrollment.course_offering.semester else 'N/A'
        
        return NotificationService.send_notification(
            recipient=student_user,
            title_en=f"Enrolled in {course_title}",
            title_zh=f"已注册 {course_title}",
            content_en=f"You have been successfully enrolled in {course_title} for {semester_name}.",
            content_zh=f"您已成功注册 {course_title} ({semester_name})。",
            notification_type='academic',
            priority='normal',
            related_object=enrollment,
            action_url=f'/student-portal/courses/'
        )
    
    @staticmethod
    def notify_teachers_about_risk_students(teachers, at_risk_count, semester):
        """Notify teachers about at-risk students in their courses"""
        notifications = []
        
        for teacher in teachers:
            notification = NotificationService.send_notification(
                recipient=teacher.user,
                title_en="At-Risk Students Alert",
                title_zh="风险学生提醒",
                content_en=f"You have {at_risk_count} at-risk student(s) in your courses for {semester.display_name}. "
                          f"Please review and provide necessary support.",
                content_zh=f"您在 {semester.display_name} 的课程中有 {at_risk_count} 名风险学生。 "
                          f"请查看并提供必要的支持。",
                notification_type='warning',
                priority='high',
                action_url=f'/teacher-portal/at-risk/'
            )
            notifications.append(notification)
        
        return notifications
    
    @staticmethod
    def get_unread_count(user):
        """Get count of unread notifications for user"""
        return Notification.objects.filter(recipient=user, is_read=False).count()
    
    @staticmethod
    def mark_all_as_read(user):
        """Mark all notifications as read for user"""
        unread = Notification.objects.filter(recipient=user, is_read=False)
        count = unread.count()
        unread.update(is_read=True, read_at=timezone.now())
        return count
    
    @staticmethod
    def get_recent_notifications(user, limit=10):
        """Get recent notifications for user"""
        return Notification.objects.filter(recipient=user).order_by('-created_at')[:limit]
