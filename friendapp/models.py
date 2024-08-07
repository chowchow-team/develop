from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

# 사용자 모델을 동적으로 가져오기 위해 get_user_model 사용
User = get_user_model()

class Friendship(models.Model):
    # ManyToManyField를 사용하여 사용자 간의 친구 관계를 나타냄
    users = models.ManyToManyField(User, related_name='friendships')
    created_at = models.DateTimeField(auto_now_add=True)  # 친구 관계 생성 시간

    def __str__(self):
        # 친구 관계를 문자열로 나타냄
        return ', '.join(user.username for user in self.users.all())

    @classmethod
    def create_friendship(cls, user1, user2):
        # 이미 존재하는 친구 관계를 찾습니다.
        friendships = cls.objects.filter(users=user1).filter(users=user2)
        if friendships.exists():
            # 이미 친구 관계가 존재하면 반환합니다.
            return friendships.first(), False
        else:
            # 새로운 친구 관계를 생성합니다.
            friendship = cls.objects.create()
            friendship.users.add(user1, user2)
            return friendship, True

    def remove_friendship(self):
        # 친구 관계를 삭제하는 메소드
        self.delete()

class FriendRequest(models.Model):
    # 친구 요청을 보낸 사용자
    from_user = models.ForeignKey(User, related_name='sent_friend_requests', on_delete=models.CASCADE)
    # 친구 요청을 받은 사용자
    to_user = models.ForeignKey(User, related_name='received_friend_requests', on_delete=models.CASCADE)
    # 요청 시간
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        # 친구 요청을 문자열로 나타냄
        return f"{self.from_user.username} to {self.to_user.username}"
