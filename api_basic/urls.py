from django.urls import path, include
from .views import article_list, article_detail, FilesAPIView,ArticleModelViewSet,ArticleGenericViewSet, ArticleViewSet, ArticleAPIView, ArticleDetails, GenericAPIView
from rest_framework.routers import DefaultRouter


router = DefaultRouter()
router.register('article', ArticleViewSet, basename='article')
router.register('generic', ArticleGenericViewSet, basename='generic')
router.register('model', ArticleModelViewSet, basename='model')

urlpatterns = [
    path('viewset/', include(router.urls)),
    path('viewset/<int:pk>', include(router.urls)),
    #path('article', article_list),
    path('article', ArticleAPIView.as_view()),
    path('detail/<int:id>', ArticleDetails.as_view()),
    path('generic/article/<int:id>', GenericAPIView.as_view()),
    #path('detail/<int:pk>', article_detail),
    path('files/', FilesAPIView.as_view()),
]