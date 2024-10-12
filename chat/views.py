from django.shortcuts import render, redirect
from rest_framework import generics, permissions, response, status, exceptions
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from user_profile.models import UserProfile
from task.models import Task
from chat.models import ChatSession, ChatMessage
from chat.serializers import ChatSessionSerializers, ChatMessageSerializers
from core.paginate import ExtraSmallResultsSetPagination
from user_profile.serializers import UserSerializer
from django.db.models import Q


def chatPage(request, *args, **kwargs):
    context = {}
    return render(request, "chat/chatPage.html", context)

class SearchChatUserListView(generics.ListAPIView):
    serializer_class = UserSerializer
    queryset = UserProfile.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'q',
                openapi.IN_QUERY,
                description='Query params for provider or performer search it will be based on first_name and last_name',
                type=openapi.TYPE_STRING
            )
        ],
        operation_id='list_performer'
    )
    def get_queryset(self):
        q = self.request.GET.get('q', None)

        user = self.request.user
        if q:
            return UserProfile.objects.filter(Q(Q(user__first_name__icontains=q) | Q(user__last_name__icontains=q))).order_by('user__last_name')

        return []


class ChatSessionListCreateView(generics.ListCreateAPIView):
    serializer_class = ChatSessionSerializers
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'is_provider',
                openapi.IN_QUERY,
                description='Query params for chat provider search, based on first_name and last_name',
                type=openapi.TYPE_STRING
            )
        ],
        operation_id='list_provider'
    )
    def get_queryset(self):
        user_profile = self.request.user.profile  # Get current user's profile

        # Define task statuses to exclude
        excluded_statuses = ['REJECTED', 'CANCELLED', 'COMPLETED']

        # Filter chat sessions based on task conditions
        return ChatSession.objects.filter(
            # Exclude tasks with REJECTED, CANCELLED, or COMPLETED status
            ~Q(task__status__in=excluded_statuses),

            # Include chat sessions where the current user is either the provider or performer
            Q(provider=user_profile) | Q(performer=user_profile),

            # Additional filter for tasks where the current user is the performer:
            # - Include tasks where the performer is null
            # - If the performer is not null, ensure it matches the current user
            Q(task__performer=user_profile) | Q(task__performer__isnull=True)
        ).exclude(
            # Exclude suspended providers and performers
            Q(provider__is_suspended=True) | Q(performer__is_suspended=True)
        ).distinct()

    def post(self, request, *args, **kwargs):
        # Extract required fields from request data
        task_id = request.data.get('task_id')
        provider_id = request.data.get('provider_id')
        performer_id = request.data.get('performer_id')
        room_name = request.data.get('room_name')

        # Validate required fields
        if not all([task_id, provider_id, performer_id, room_name]):
            return response.Response(
                {"detail": "Missing required fields."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Retrieve or raise errors if any objects do not exist
        try:
            provider = UserProfile.objects.get(pk=provider_id)
            performer = UserProfile.objects.get(pk=performer_id)
            task = Task.objects.get(pk=task_id)
        except (UserProfile.DoesNotExist, Task.DoesNotExist) as e:
            return response.Response({"detail": str(e)}, status=status.HTTP_404_NOT_FOUND)

        # Validate user's status before creating TaskApplicant
        if provider.is_suspended:
            raise exceptions.ValidationError({"error_message": "Your account is suspended."})
    
        if provider.is_terminated:
            raise exceptions.ValidationError({"error_message": "Your account is terminated."})

        if performer.is_suspended:
            raise exceptions.ValidationError({"error_message": "Your account is suspended."})
    
        if performer.is_terminated:
            raise exceptions.ValidationError({"error_message": "Your account is terminated."})

        # Use `get_or_create` to simplify the check and create logic
        chat_session, created = ChatSession.objects.get_or_create(
            task=task,
            provider=provider,
            performer=performer,
            room_name=room_name
        )

        # Serialize the chat session
        serializer = ChatSessionSerializers(chat_session)

        # Return appropriate response based on whether the session was created
        return response.Response(
            serializer.data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK
        )



class ChatMessageListView(generics.ListAPIView):
    serializer_class = ChatMessageSerializers
    queryset = ChatMessage.objects.all()
    permission_classes = [permissions.IsAuthenticated,]
    pagination_class = ExtraSmallResultsSetPagination

    def get_queryset(self):
        session_id = self.request.GET.get('session_id', None)

        if session_id:
            return ChatMessage.objects.filter(chat_session__pk=session_id)
        
        return []


class ChatMessageRetrieveView(generics.RetrieveAPIView):
    serializer_class = ChatSessionSerializers
    queryset = ChatSession.objects.all()
    permission_classes = [permissions.IsAuthenticated,]

    def get(self, request, *args, **kwargs):
        room_name = request.GET.get('room_name', None)

        chat_sessions = ChatSession.objects.filter(room_name=room_name)

        if chat_sessions.exists():
            serializer = ChatSessionSerializers(chat_sessions.first())
            return response.Response(serializer.data, status=status.HTTP_200_OK)

        return response.Response({"error_message": "Not found"}, status=status.HTTP_400_BAD_REQUEST)