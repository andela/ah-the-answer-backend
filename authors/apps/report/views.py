from django.shortcuts import render
from django.shortcuts import get_object_or_404

from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response

from ..authentication.models import User
from ..articles.models import Article
from .models import Report

from .serializers import ReportSerializer


class ManageReport(APIView):
    permission_classes = (IsAuthenticated,)
