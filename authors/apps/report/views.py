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


class CreateListReportsAPIView(APIView):
    serializer_class = ReportSerializer

    def get_object(self, id):
        try:
            articleID = Article.objects.get(id=id).id
            return articleID
        except:
            return Response({"error": "No article with that id found."},
                            status=status.HTTP_404_NOT_FOUND)

    def post(self, request):
        """Method for creating report for a particular article"""
        report = request.data.get('report', {})
        
        article = self.get_object(report['article_id'])
        
        serializer = self.serializer_class(data=report)
        if serializer.is_valid(raise_exception=True):
            profile_saved = serializer.save(article_id=article)
            return Response(
                {
                    "success": "Created"
                },
                status=status.HTTP_201_CREATED
            )
    
    def get(self, request):
        """Method to retrieve reports for a particular report"""
        report
