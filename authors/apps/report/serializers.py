from rest_framework import serializers
from authors.apps.report.models import Report


class ReportSerializer(serializers.ModelSerializer):
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
        fields = ['id', 'reporter', 'violation', 'reportDetails',
                  'isResolved', 'adminNote']
