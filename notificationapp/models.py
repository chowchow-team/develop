from django.db import models
import accountapp

class Notification(models.Model):
    TYPE_CHOICES = (
        (0, 'dm'),
    )
    notification_type = models.IntegerField(choices=TYPE_CHOICES)
    sender = models.ForeignKey('accountapp.User', related_name='notification_from', on_delete=models.CASCADE, null=True)
    receiver = models.ForeignKey('accountapp.User', related_name='notification_to', on_delete=models.CASCADE, null=True)
    text_preview = models.CharField(max_length=15, null=True, blank=True)
    user_has_seen = models.BooleanField(default=False)
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date']
    def __str__(self):
        return f"{self.get_notification_type_display()} from {self.sender} to {self.receiver} on {self.date}"


