from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .llm.chat import chat
from rest_framework.permissions import IsAuthenticated
from chatapp.models import Message
from chatapp.serializers import MessageSerializer
from django.contrib.auth import get_user_model
from django.db.models import Q

User = get_user_model()

class ChatbotAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        query = request.data.get('message')
        receiver_id = request.data.get('receiver_id')
        
        if not query or not receiver_id:
            return Response({'error': 'Message and receiver_id are required'}, status=status.HTTP_400_BAD_REQUEST)

        user = request.user
        try:
            receiver = User.objects.get(id=receiver_id)
            
            # 사용자 메시지 저장
            user_message = Message.objects.create(
                sender=user,
                receiver=receiver,
                message=query
            )

            # 봇이 응답 생성
            bot_response = chat(query, receiver)

            # 봇 응답을 receiver가 보낸 것처럼 저장
            bot_message = Message.objects.create(
                sender=receiver,
                receiver=user,
                message=bot_response
            )

            # 시리얼라이저를 사용하여 응답 데이터 생성
            user_message_data = MessageSerializer(user_message).data
            bot_message_data = MessageSerializer(bot_message).data

            return Response({
                'user_message': user_message_data,
                'bot_message': bot_message_data
            }, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'error': 'Receiver not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get(self, request):
        user = request.user
        other_user_id = request.query_params.get('other_user_id')

        if not other_user_id:
            return Response({'error': 'other_user_id is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            other_user = User.objects.get(id=other_user_id)
            messages = Message.objects.filter(
                (Q(sender=user) & Q(receiver=other_user)) |
                (Q(sender=other_user) & Q(receiver=user))
            ).order_by('-timestamp')
            
            chat_history = [{
                'sender': msg.sender.username,
                'message': msg.message,
                'timestamp': msg.timestamp
            } for msg in messages]

            return Response(chat_history, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)