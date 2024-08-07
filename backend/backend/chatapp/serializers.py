from rest_framework import serializers
from .models import Message
from django.utils import timezone

class MessageSerializer(serializers.ModelSerializer):
    sender = serializers.CharField(source='sender.username', read_only=True)
    receiver = serializers.CharField(source='receiver.username', read_only=True)

    class Meta:
        model = Message
        fields = ['id', 'sender', 'receiver', 'message', 'timestamp']
        read_only_fields = ('sender',)

    #def get_timestamp(self, obj):
    #    # 현재 시간과 메시지의 timestamp 시간 차이가 하루 미만일 경우 "오전/오후 시:분" 형식으로 반환
    #    if timezone.now() - obj.timestamp < timezone.timedelta(days=1):
    #        return obj.timestamp.strftime("%p %I:%M").replace("AM", "오전").replace("PM", "오후")
    #    else:
    #        # 하루 이상일 경우, 날짜를 포함한 형식으로 반환
    #        return obj.timestamp.strftime("%Y-%m-%d %p %I:%M").replace("AM", "오전").replace("PM", "오후")