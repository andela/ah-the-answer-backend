from django.shortcuts import render
from django.shortcuts import get_object_or_404

from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response

from ..authentication.models import User
from ..articles.models import Article
from .models import Report
from authors.apps.articles.views import find_article

from .serializers import ReportSerializer

def find_object(article_id):
    try:
        articleID = Article.objects.get(id=article_id)
        return articleID
    except:
        return Response({"error": "No article with that id found."},
                        status=status.HTTP_404_NOT_FOUND)


class CreateListReportsAPIView(APIView):
    serializer_class = ReportSerializer

    def post(self, request, id):
        """Method for creating report for a particular article"""
        report = request.data.get('report', {})
        try:
            article = Article.objects.get(id=id)
        except:
            return Response(
                {
                    "error": "No article with that id found."
                },
                status=status.HTTP_404_NOT_FOUND)
        serializer = self.serializer_class(data=report)
        if serializer.is_valid(raise_exception=True):
            serializer.save(article_id=article.id)
            return Response(
                {
                    "success": "Logged {} report for article {}.".format
                    (report['violation'], article.title)
                },
                status=status.HTTP_201_CREATED
            )
    
    def get(self, request, id):
        """Method to retrieve reports for a particular report"""
        article = find_object(id)

        reports = Report.objects.filter(article_id=id).values(
            'reporter', 'createdAt', 'resolvedAt', 'violation',
            'isResolved', 'adminNote', 'reportDetails', 'id'
        )
        # serializer = self.serializer_class(reports, many=True)
        #print(reports[0])
        return Response(
            {
                "message": "successfully retrieved reports for article {}".format(article.title),
                "reports": reports
            },
            status=status.HTTP_200_OK)


class GetAllReportsView(APIView):

    def get(self, request):
        """retrieve a report by id"""
        reports = Report.objects.all().values()
        return Response(
            {
                "success": "All reports retrieved.",
                "reports": reports
            },
            status=status.HTTP_200_OK)

    
    