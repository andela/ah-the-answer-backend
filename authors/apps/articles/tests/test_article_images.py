import tempfile

from django.test import TestCase
from django.urls import reverse
from PIL import Image
from rest_framework import status, test

from authors.apps.articles.models import Article, ArticleImage
from authors.apps.authentication.models import User


class TestArticle(TestCase):
    def setUp(self):
        self.client = test.APIClient()
        self.user = User.objects.create_user(
            email='test@mail.com',
            username='Test',
            password='test1234'
        )

        # verify email
        test_user = User.objects.get(username='Test')
        test_user.is_verified = True
        test_user.save()
        self.login = self.client.post(
            reverse('authentication:user-login'),
            data={
                "user": {
                    "email": "test@mail.com",
                    "password": "test1234"
                }
            },
            format="json"
        )

        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + self.login.data['token'])

        self.client.post(
            reverse('articles:create-list'),
            data={
                "article": {
                    "title": "Test title",
                    "body": "This is a very awesome article on testing tests",
                    "description": "Written by testing tester",
                    "tags": []
                }
            },
            format="json"
        )
        self.client_3 = test.APIClient()
        self.user_3 = User.objects.create_user(
            email='test3@mail.com',
            username='Test3',
            password='test1234'
        )

        test_user_3 = User.objects.get(username='Test3')
        test_user_3.is_verified = True
        test_user_3.save()
        self.login_3 = self.client_3.post(
            reverse('authentication:user-login'),
            data={
                "user": {
                    "email": "test3@mail.com",
                    "password": "test1234"
                }
            },
            format="json"
        )

        self.client_3.credentials(
            HTTP_AUTHORIZATION='Bearer ' + self.login_3.data['token'])

    @property
    def temporary_image(self):
        """
        Creates a dummy, temporary image for testing purposes
        Returns a new temporary image file
        """

        image = Image.new('RGB', (1, 1))
        tmp_file = tempfile.NamedTemporaryFile(suffix='.jpg')
        image.save(tmp_file, 'jpeg')
        # important because after save(),
        # the fp is already at the end of the file
        tmp_file.seek(0)  # retrieves the created temp file
        return tmp_file

    @property
    def temporary_unsupported_image(self):
        """
        Creates a dummy, temporary image for testing purposes
        Returns a new temporary image file
        """
        image = Image.new('RGB', (1, 1))
        tmp_file = tempfile.NamedTemporaryFile(suffix='.ppm')
        image.save(tmp_file, 'ppm')
        # important because after save(),
        # the fp is already at the end of the file
        tmp_file.seek(0)  # retrieves the created temp file
        return tmp_file

    def test_get_article_images(self):

        response = self.client.get(
            reverse(
                'articles:add-image',
                kwargs={"slug": Article.objects.get().slug},
            ),
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['imagesCount'], 0)

    def test_get_specific_image(self):

        response = self.client.get(
            reverse(
                'articles:image-details',
                kwargs={"slug": Article.objects.get().slug,
                        "id": Article.objects.get().id},
            ),
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['image'], [])

    def test_delete_nonexistent_image(self):

        response = self.client.delete(
            reverse(
                'articles:image-details',
                kwargs={
                    "slug": Article.objects.get().slug,
                    "id": Article.objects.get().id,
                }
            ),
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['message'],
                         'The requested image does not exist.')

    def test_delete_specific_image(self):

        self.client.post(
            reverse('articles:add-image',
                    kwargs={
                        "slug": Article.objects.get().slug
                    }),
            data={
                "file": self.temporary_image
            },
            format='multipart'
        )

        response = self.client.delete(
            reverse(
                'articles:image-details',
                kwargs={
                    "slug": Article.objects.get().slug,
                    "id": ArticleImage.objects.get().id,
                }
            ),
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_multiple_images(self):
        i = 0
        while i < 3:
            self.client.post(
                reverse('articles:add-image',
                        kwargs={
                            "slug": Article.objects.get().slug
                        }),
                data={
                    "file": self.temporary_image
                },
                format='multipart'
            )
            i += 1

        response = self.client.delete(
            reverse(
                'articles:details',
                kwargs={
                    "slug": Article.objects.get().slug
                }
            ),
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_upload_not_authorized(self):
        response = self.client_3.post(
            reverse(
                'articles:add-image',
                kwargs={
                    "slug": Article.objects.get().slug
                }
            ),
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['message'],
                         'Only the owner of this article can upload images.')

    def test_delete_not_authorized(self):
        self.client.post(
            reverse('articles:add-image',
                    kwargs={
                        "slug": Article.objects.get().slug
                    }),
            data={
                "file": self.temporary_image
            },
            format='multipart'
        )

        response = self.client_3.delete(
            reverse(
                'articles:image-details',
                kwargs={
                    "slug": Article.objects.get().slug,
                    "id": ArticleImage.objects.get().id,
                }
            ),
            format="json"
        )
        self.client.delete(
            reverse(
                'articles:image-details',
                kwargs={
                    "slug": Article.objects.get().slug,
                    "id": ArticleImage.objects.get().id,
                }
            ),
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['message'],
                         'Only the owner can delete this image.')

    def test_invalid_image_upload(self):
        """
        This test case tests that an authenticated
        user can't upload invalid image for their article
        """
        res = self.client.post(
            reverse('articles:add-image',
                    kwargs={
                        "slug": Article.objects.get().slug
                    }),
            data={
                "file": self.temporary_unsupported_image
            },
            format='multipart'
        )
        self.assertEquals(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertRaises(Exception)

    def tearDown(self):
        Article.objects.all().delete()
