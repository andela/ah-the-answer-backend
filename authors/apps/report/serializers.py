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
        fields = ['reporter', 'violation', 'reportDetails',
                  'isResolved', 'adminNote']
    
    def create(self, validated_data):
        """
        Creates new report record after validation.
        """

        return Report.objects.create(**validated_data)

    def update(self, instance, validated_data):
        """
        Passes in an instance of the report to be updated.
        Update occurs if new values are provided.
        Otheriwse instance values remain the same.
        """

        instance.resolvedAt = validated_data.get('resolvedAt',
                                                 instance.resolvedAt)
        instance.isResolved = validated_data.get('isResolved',
                                                 instance.isResolved)
        instance.adminNote = validated_data.get('adminNote',
                                                instance.adminNote)
        instance.save()

        return instance
