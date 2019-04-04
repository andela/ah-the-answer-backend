# from django.test import TestCase
# from django.urls import reverse
# from rest_framework import test, status
# from .models import User
# from .jwt_generator import jwt_encode, jwt_decode


# class TestJWTGenerator(TestCase):
#     def setUp(self):
#         self.id = 11
#         self.token = jwt_encode(self.id)
#         self.client = test.APIClient()
    
#     def test_that_token_encoded_decoded(self):
#         decoded_id = jwt_decode(self.token)

#         self.assertTrue(self.token)
#         self.assertEqual(decoded_id['user_id'], self.id)
    
#     def test_user_token_property(self):
#         user = User.objects.create(
#             username="test",
#             email="test@mail.com",
#             password="test123"
#         )
#         token = user.get_token

#         self.assertTrue(token)
#         self.assertEqual(jwt_decode(token)['user_id'], user.id)

#     def test_login_endpoint(self):
#         create_res = self.client.post(
#             reverse('authentication:user-signup'),
#             data={
#                 "user": {
#                     "email": "tester@mail.com",
#                     "username": "tester",
#                     "password": "tester1234"
#                 }
#             },
#             format="json"
#         )

#         login_res = self.client.post(
#             reverse('authentication:user-login'),
#             data={
#                 "user": {
#                     "email": "tester@mail.com",
#                     "password": "tester1234"
#                 }
#             },
#             format="json"
#         )

#         self.assertEqual(create_res.status_code, status.HTTP_201_CREATED)
#         self.assertEqual(login_res.status_code, status.HTTP_200_OK)
#         self.assertEqual(create_res.data['email'], login_res.data['email'])
#         self.assertEqual(create_res.data['username'], login_res.data['username'])
#         self.assertTrue(login_res.data['token'])
