from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from decouple import config

api_url = config("API_URL", default="http://localhost:8000/")

class CustomApiRootView(APIView):
    """
    Custom API root view that provides a list of all available endpoints.
    """
    permission_classes = []
    
    def get(self, request, *args, **kwargs):
        return Response(
            {
                'message': 'Welcome to the Blog API!',
                'note': 'This is API mapping, you can use it to discover the available endpoints',
                'endpoints': {
                    'articles': {
                        'list': f'{api_url}api/articles/',
                        'search': f'{api_url}api/articles/?search=<query>',
                        'pagination': f'{api_url}api/articles/?page=<page_number>',
                        'detail': f'{api_url}api/articles/<id>/',
                        'create (admin/editor)': f'{api_url}api/articles/',
                        'update (admin/editor)': f'{api_url}api/articles/<id>/',
                        'delete (admin)': f'{api_url}api/articles/<id>/',
                    },
                    'comments': {
                        'list for article': f'{api_url}api/articles/<article_id>/comments/',
                        'create (authenticated)': f'{api_url}api/articles/<article_id>/comments/',
                        'update (owner)': f'{api_url}api/comments/<id>/',
                        'delete (admin)': f'{api_url}api/comments/<id>/',
                    },
                    'authentication': {
                        'register': f'{api_url}api/register/',
                        'login': f'{api_url}api/login/',
                        'refresh token': f'{api_url}api/token/refresh/',
                    },
                    'users': {
                        'list (admin)': f'{api_url}api/users/',
                    }
                }
            },
            status=status.HTTP_200_OK
        )