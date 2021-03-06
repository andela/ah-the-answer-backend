from datetime import datetime

from django.shortcuts import render
from django.shortcuts import get_object_or_404

from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response

from .serializers import ReportSerializer
from .models import Report
from ..authentication.models import User
from ..articles.models import Article

from authors.apps.articles.views import find_article


class CreateListReportsAPIView(APIView):

    def post(self, request, id):
        """
        Creates a single report for a specific article
        """
        report = request.data.get('report', {})
        try:
            article = Article.objects.get(id=id)
        except:
            return Response(
                {
                    "error": "No article with that id found."
                },
                status=status.HTTP_404_NOT_FOUND)
        serializer = ReportSerializer(data=report)
        if serializer.is_valid(raise_exception=True):
            serializer.save(article_id=article.id)
            return Response(
                {
                    "success": "Logged {} report for article {}.".format
                    (report['violation'], article.title),
                    "report": serializer.data
                },
                status=status.HTTP_201_CREATED
            )

    def get(self, request, id):
        """
        Retrieve all reports for a specific article
        """
        permission_classes = (IsAuthenticated,)

        try:
            article = Article.objects.get(id=id)
        except:
            return Response(
                {
                    "error": "No article with that id found."
                },
                status=status.HTTP_404_NOT_FOUND)
        reports = Report.objects.filter(article_id=id).values(
            'reporter', 'createdAt', 'resolvedAt', 'violation',
            'isResolved', 'adminNote', 'reportDetails', 'id'
        )
        return Response(
            {
                "message": "successfully retrieved reports for "
                           "article {}".format(article.title),
                "reports": reports
            },
            status=status.HTTP_200_OK)

    def put(self, request, id):
        """
        Changes a single report 'isResolved' status to 'True'
        and sets the 'resolvedAt' date.
        """
        permission_classes = (IsAuthenticated,)

        try:
            report = Report.objects.get(id=id)
        except:
            return Response(
                {
                    "error": "No report with that id found."
                },
                status=status.HTTP_404_NOT_FOUND)
        update = request.data.get('resolve', {})
        report.resolvedAt = datetime.now().strftime('%Y-%m-%d')
        report.isResolved = True
        report.adminNote = update['adminNote']
        report.save(update_fields=['resolvedAt', 'adminNote', 'isResolved'])
        response_body = {
               "isResolved": report.isResolved,
               "resolvedAt": report.resolvedAt,
               "adminNote": report.adminNote
            }
        return Response(
            {
               "success": "Report Resolved",
               "report": response_body
            },
            status=status.HTTP_200_OK)

    def delete(self, request, id):
        """
        Removes a single report from the database
        """
        permission_classes = (IsAuthenticated,)

        try:
            report = Report.objects.get(id=id)
        except:
            return Response(
                {
                    "error": "No report with that id found."
                },
                status=status.HTTP_404_NOT_FOUND)
        report.delete()
        return Response(
            {
                "message": "report has been deleted"
            },
            status=status.HTTP_200_OK)


class GetAllReportsView(APIView):

    def get(self, request):
        """
        Retrieves all reports from the database
        """
        permission_classes = (IsAuthenticated,)

        reports = Report.objects.all().values()
        return Response(
            {
                "success": "All reports retrieved.",
                "reports": reports
            },
            status=status.HTTP_200_OK)
