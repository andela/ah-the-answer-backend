from django.test import TestCase
from django.test import Client
from django.urls import reverse

from rest_framework import test, status
from rest_framework.test import APIClient

from .models import Report
from authors.apps.articles.models import Article
from ..authentication.models import User


class TestReportViews(TestCase):
    """
    Tests the views contained in the 'report' app.
    """
    def setUp(self):

        """
        Create, authenticate and login first user.
        """
        self.client_1 = APIClient()
        self.user_1 = self.client_1.post(
            reverse('authentication:user-signup'),
            data={
                "user": {
                    "email": "demo@mail.com",
                    "username": "Bob",
                    "password": "Bob12345"
                }
            },
            format="json"
        )
        test_user_1 = User.objects.get(username='Bob')
        test_user_1.is_verified = True
        test_user_1.save()
        self.login_1 = self.client_1.post(
            reverse('authentication:user-login'),
            data={
                "user": {
                    "email": "demo@mail.com",
                    "password": "Bob12345"
                }
            },
            format="json"
        )
    
        """
        Create, authenticate and login a second user.
        """
        self.client_2 = APIClient()
        self.user_2 = self.client_2.post(
            reverse('authentication:user-signup'),
            data={
                "user": {
                    "email": "mail@demo.com",
                    "username": "Mary",
                    "password": "Mary12345"
                }
            },
            format="json"
        )
        test_user_2 = User.objects.get(username='Mary')
        test_user_2.is_verified = True
        test_user_2.save()
        self.login_2 = self.client_2.post(
            reverse('authentication:user-login'),
            data={
                "user": {
                    "email": "mail@demo.com",
                    "password": "Mary12345"
                }
            },
            format="json"
        )
        
        """
        Store the login tokens.
        """
        self.token_1 = self.login_1.data['token']
        self.token_2 = self.login_2.data['token']

        """
        Attach the login tokens to the user auth headers.
        """
        self.client_1.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token_1)
        self.client_2.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token_2)

        """
        Define two tests articles
        """
        self.user_article_1 = {
            "article":
            {
             "title": "Inappropriate Title",
             "body": "Explicit Material",
             "description": "Illegal Information.",
             "is_published": True
            }
        }

        self.user_article_2 = {
            "article":
            {
             "title": "Explicit Title",
             "body": "Obscene Material",
             "description": "Private Information",
             "is_published": True
            }
        }

    def test_create_report(self):
        self.user_report = {
            "report":
            {
                "reporter": "mail@demo.com",
                "violation": "Graphic Content",
                "reportDetails": "Offensive Images"
            }
        }
        self.client_1.post(reverse('articles:create-list'),
                           self.user_article_1, format="json")
        response = self.client_1.post(reverse('report:report-create', args=[1]),
                                      self.user_report, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['success'], "Logged Graphic Content "
                                                   "report for article "
                                                   "Inappropriate Title.")
    
    def test_get_all_reports_for_article(self):
        self.user_report_1 = {
            "report":
            {
                "reporter": "mail@demo.com",
                "article_id": 2,
                "violation": "Graphic Content",
                "reportDetails": "Offensive Images"
            }
        }
        self.user_report_2 = {
            "report":
            {
                "reporter": "Jane@demo.com",
                "article_id": 2,
                "violation": "Spam",
                "reportDetails": "Bot messages"
            }
        }
        self.user_report_3 = {
            "report":
            {
                "reporter": "Jacob@demo.com",
                "article_id": 2,
                "violation": "Harrassment",
                "reportDetails": "Bot messages"
            }
        }
        article_response = self.client_1.post(reverse('articles:create-list'),
                                              self.user_article_1,
                                              format="json")
        id = article_response.data['article']['id']
        self.client_1.post(reverse('report:report-create', args=[id]),
                           self.user_report_1, format='json')
        self.client_1.post(reverse('report:report-create', args=[id]),
                           self.user_report_2, format='json')
        self.client_1.post(reverse('report:report-create', args=[id]),
                           self.user_report_3, format='json')
        response = self.client_1.get(reverse('report:report-create',
                                     args=[id]), format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.assertEqual(len(response.data['reports']), 3)
