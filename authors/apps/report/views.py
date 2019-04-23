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
    permission_classes = (IsAuthenticated,)

    def post(self, request, slug):
        report = request.data.get('report', {})
        serializer = self.serializer_class(data=report)
        serializer.is_valid(raise_exception=True)
        article = find_article(slug)
        author = request.user
        if article.author == author:
            return Response({'error': 'you cannot report your own article'},
                                        status=status.HTTP_400_BAD_REQUEST)
        serializer.save(author=author, article=article)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED 
        )
