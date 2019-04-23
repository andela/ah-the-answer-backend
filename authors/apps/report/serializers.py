from rest_framework import serializers
from authors.apps.report.models import Report


class ReportSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    reporter = serializers.EmailField(max_length=254)
    violation = serializers.ChoiceField(choices=['Hate Speech', 'Harrassment',
                                                 'Privacy and Reputation',
                                                 'Spam', 'Bot Account',
                                                 'Deceptive Conduct',
                                                 'Graphic Content',
                                                 'Exploitation of Minors',
                                                 'Promotion of Self-harm',
                                                 'Other'])

    class Meta:
        model = Report
        fields = ['article_id', 'reporter', 'createdAt', 'resolvedAt',
                  'violation', 'reportDetails', 'isResolved', 'adminNote']
