from django.db import models
from authors import settings
from authors.apps.articles.models import Article


class Report(models.Model):
    """
    This class represents the model for Author's Haven that records user
    reports on articles.
    """
    VIOLATION_CHOICES = (
        ('Hate Speech', 'Hate Speech'),
        ('Harrassment', 'Harassment'),
        ('Privacy and Reputation', 'Privacy and Reputation'),
        ('Spam', 'Spam'),
        ('Bot Account', 'Bot Account'),
        ('Deceptive Conduct', 'Deceptive Conduct'),
        ('Graphic Content', 'Graphic Content'),
        ('Exploitation of Minors', 'Exploitation of Minors'),
        ('Promotion of Self-harm', 'Promotion of Self-harm'),
        ('Other', 'Other')
    )
    article = models.ForeignKey(
        Article,
        on_delete=models.CASCADE
    )
    reporter = models.EmailField(default=None)
    createdAt = models.DateTimeField(auto_now_add=True)
    resolvedAt = models.DateField(blank=True, null=True)
    violation = models.CharField(max_length=30, choices=VIOLATION_CHOICES)
    reportDetails = models.TextField(max_length=1000, default="No Comment.")
    isResolved = models.BooleanField(default=False)
    adminNote = models.TextField(max_length=1000, default="No Comment.")

    class Meta:
        ordering = ["createdAt"]





