from django.shortcuts import render

from rest_framework.permissions import IsAuthenticated


class ManageFollows(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, username):
        """Returns a list of usernames that follow the user."""
        
