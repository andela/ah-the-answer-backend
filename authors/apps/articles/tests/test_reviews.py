from .commons import *


class TestReviewModel(BaseSetup):
    def setUp(self):
        user = User.objects.create(username="johndoe")
        article = Article.objects.create(
            title="Test title",
            body="This is a very awesome article on testing tests",
            description="Written by testing tester",
            author=user
        )
        self.review_body = "John Doe"
        self.rating_value = int(5)
        self.review = ReviewsModel(
            article=article,
            review_body=self.review_body,
            rating_value=self.rating_value,
            reviewed_by=user,
        )

    def test_model_can_create_review(self):
        """Test whether model can create a record"""
        initial = ReviewsModel.objects.count()
        self.review.save()
        updated = ReviewsModel.objects.count()
        self.assertNotEqual(initial, updated)


class ReviewTestCase(BaseSetup):

    def test_user_can_create_review(self):
        response = self.post_article()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response = self.post_review()
        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_user_can_get_reviews(self):
        response = self.post_article()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response = self.post_review()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response = self.client2.get(
            reverse('articles:review', kwargs={
                "slug": Article.objects.get().slug
            }),
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, "I really liked the article")

    def test_user_can_edit_review(self):
        response = self.post_article()

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response = self.post_review()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response = self.client2.put(reverse('articles:alter-review', kwargs={
            "slug": Article.objects.get().slug, 'username': "Pete"
        }), data={
            "review": {
                "review_body": "I did not liked the article",
                "rating_value": 3
            }
        },
            format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_can_delete_review(self):
        response = self.post_article()

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response = self.post_review()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response = self.client2.delete(reverse('articles:alter-review', kwargs={
            "slug": Article.objects.get().slug, 'username': "Pete"
        }))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_delete = self.client2.get(
            reverse('articles:review', kwargs={
                "slug": Article.objects.get().slug
            }),
            format="json"
        )
        self.assertEqual(response_delete.status_code,
                         status.HTTP_404_NOT_FOUND)
        self.assertRaises(Exception)

    def test_unautheticated_user_cant_create_review(self):
        response = self.post_article()

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.client2.logout()
        response = self.post_review()
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_review_creation_with_wrong_values(self):
        response = self.post_article()

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response = self.client2.post(
            reverse('articles:review', kwargs={
                "slug": Article.objects.get().slug
            }),
            data={
                "review": {
                    "review_body": "I really liked the article",
                    "rating_value": True
                }
            },
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_cannot_review_own_article(self):
        response = self.post_article()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response = self.client.post(
            reverse('articles:review', kwargs={
                "slug": Article.objects.get().slug
            }),
            data={
                "review": {
                    "review_body": "I really liked the article",
                    "rating_value": 5
                }
            },
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_cant_edit_non_existent_review(self):
        self.test_user_can_delete_review()
        response = self.client2.delete(reverse('articles:alter-review', kwargs={
            "slug": Article.objects.get().slug, 'username': User.objects.filter(username="Pete").first()
        }))
        self.assertEqual(response.status_code,
                         status.HTTP_404_NOT_FOUND)
        self.assertRaises(Exception)

    def test_cant_review_non_existent_article(self):
        response = self.client2.post(
            reverse('articles:review', kwargs={
                "slug": "fake_article"
            }),
            data={
                "review": {
                    "review_body": "I really liked the article",
                    "rating_value": 5
                }
            },
            format="json"
        )
        self.assertEqual(response.status_code,
                         status.HTTP_404_NOT_FOUND)
        self.assertRaises(Exception)
