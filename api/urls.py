from django.urls import path, include
from rest_framework.routers import DefaultRouter

from django.contrib.auth import views as auth_views

from user_profile.views import (ProfileView,
                                RegisterView, ChangePasswordView, 
                                UploadPhotoView, RequestPasswordResetEmail, UserReportCreateView
                                )

from task.views import (TaskCategoryListView, TaskListView, TaskViewSet, TaskReviewListView, 
                        TaskApplicantCreateView, TaskListApplicantView, PerformerTaskViewSet, TaskReviewViewSet)
from chat.views import ChatMessageListView, ChatMessageRetrieveView, ChatSessionListCreateView, SearchChatUserListView

app_name = 'api'


router = DefaultRouter()
router.register(r'provider/task', TaskViewSet, basename='provider')
router.register(r'performer/task', PerformerTaskViewSet, basename='performer')


urlpatterns = [
     path('signup', RegisterView.as_view(), name='signup'),
     path('profile', ProfileView.as_view(), name='profile'),
     path('upload-photo/<pk>', UploadPhotoView.as_view(), name='upload-photo'),
     path('change-password', ChangePasswordView.as_view(), name='change-password'),

     path('forgot-password', RequestPasswordResetEmail.as_view(),
          name='forgot-password '),
     path('password-reset-confirm/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(),
         name='password-reset-confirm'),   

     path('task/category/list',
         TaskCategoryListView.as_view(),
         name='task-category-list'),  
     path('task/list',
         TaskListView.as_view(),
         name='task-list'),   
     path('', include(router.urls)),
     path('task/review/list',
         TaskReviewListView.as_view(),
         name='task-review-list'),
     path('task/<int:task_id>/review/', TaskReviewViewSet.as_view({'post': 'create_or_update', 'get': 'retrieve'})),

     path('taskapplicant/create/', TaskApplicantCreateView.as_view(), name='taskapplicant-create'),
     path('taskapplicant/list/', TaskListApplicantView.as_view(), name='taskapplicant-list'),
     
     # Chat
     path('chat-sessions', ChatSessionListCreateView.as_view(),
          name='chat-sessions'),
     path('chat-messages', ChatMessageListView.as_view(),
          name='chat-messages'),
     path('chat-session/retrieve', ChatMessageRetrieveView.as_view(),
     name='chat-session'),
     path('chat-sessions/search', SearchChatUserListView.as_view(),
          name='chat-sessions-search'),
     
     #  Reports
     path('reports/', UserReportCreateView.as_view(), name='user-report-create'),

]
