import json
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
    
    def test_create_report_for_invalid_article(self):
        self.user_report = {
            "report":
            {
                "reporter": "mail@demo.com",
                "violation": "Graphic Content",
                "reportDetails": "Offensive Images"
            }
        }
        response = self.client_1.post(reverse('report:report-create', args=[31]),
                                      self.user_report, format='json')
        output = json.loads(response.content)
        self.assertIn(
            'No article with that id found.',
            str(output))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


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
    
    def test_get_reports_for_nonexistent_article(self):
        response = self.client_1.get(reverse('report:report-create',
                                     args=[48]), format='json')
        output = json.loads(response.content)
        self.assertIn(
            'No article with that id found.',
            str(output))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_all_reports(self):
        self.user_report_1 = {
            "report":
            {
                "reporter": "Jane@demo.com",
                "violation": "Spam",
                "reportDetails": "Bot messages"
            }
        }
        self.user_report_2 = {
            "report":
            {
                "reporter": "Jacob@demo.com",
                "violation": "Harrassment",
                "reportDetails": "Bot messages"
            }
        }
        response_1 = self.client_1.post(reverse('articles:create-list'), 
                                        self.user_article_1, format="json")
        response_2 = self.client_1.post(reverse('articles:create-list'), 
                                        self.user_article_2, format="json")
        id_1 = response_1.data['article']['id']
        id_2 = response_2.data['article']['id']

        self.client_1.post(reverse('report:report-create', args=[id_1]),
                           self.user_report_1, format='json')
        self.client_1.post(reverse('report:report-create', args=[id_2]),
                           self.user_report_2, format='json')
    
        response = self.client_1.get(reverse('report:fetch-reports'), format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        print(response.data)
        self.assertEqual(len(response.data['reports']), 2)
    
    def test_resolve_report(self):
        self.user_report_1 = {
            "report":
            {
                "reporter": "Jane@demo.com",
                "violation": "Spam",
                "reportDetails": "Bot messages"
            }
        }
        self.admin_resolve = {
            "resolve":
            {
                "adminNote": "Ban User"
            }
        }
        response_1 = self.client_1.post(reverse('articles:create-list'), 
                                        self.user_article_1, format="json")
        id_1 = response_1.data['article']['id']

        report = self.client_1.post(reverse('report:report-create', args=[id_1]),
                                    self.user_report_1, format='json')
        report_id = report.data['report']['id']
        response = self.client_1.put(reverse('report:report-create', 
                                     args=[report_id]), self.admin_resolve,
                                     format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['isResolved'], True)
        self.assertEqual(response.data['adminNote'], "Ban User")
    
    def test_update_invalid_report(self):
        self.admin_resolve = {
            "resolve":
            {
                "adminNote": "Ban User"
            }
        }
        response = self.client_1.put(reverse('report:report-create', 
                                     args=[29]), self.admin_resolve,
                                     format='json')
        output = json.loads(response.content)
        self.assertIn(
            'No report with that id found.',
            str(output))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    
    def test_delete_report(self):
        self.user_report_1 = {
            "report":
            {
                "reporter": "Jane@demo.com",
                "violation": "Spam",
                "reportDetails": "Bot messages"
            }
        }
        response_1 = self.client_1.post(reverse('articles:create-list'), 
                                        self.user_article_1, format="json")
        id_1 = response_1.data['article']['id']
        report = self.client_1.post(reverse('report:report-create', args=[id_1]),
                                    self.user_report_1, format='json')
        report_id = report.data['report']['id']                         
        response = self.client_1.delete(reverse('report:report-create', 
                                     args=[report_id]),
                                     format='json')
        output = json.loads(response.content)
        self.assertIn(
            'report has been deleted',
            str(output))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_invalid_report(self):
                       
        response = self.client_1.delete(reverse('report:report-create', 
                                     args=[12]),
                                     format='json')
        output = json.loads(response.content)
        self.assertIn(
            'No report with that id found.',
            str(output))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)