from django.contrib.auth.models import User
from .models import FollowList

class FollowService:
    @staticmethod
    def follow(follower: User, following: User):
        if not FollowService.is_following(follower,following):
            FollowList.objects.create(follower=follower, following=following)
    
    @staticmethod
    def unfollow(follower: User, following: User):
        FollowList.objects.filter(follower=follower,following=following).delete()
    
    @staticmethod
    def is_following(follower: User, following: User):
        return FollowList.objects.filter(follower=follower,following=following).exists()
    
    @staticmethod
    def get_follower(user: User):
        return FollowList.objects.filter(following=user).values_list('follower', flat=True)
    
    @staticmethod
    def get_following(user: User):
        return FollowList.objects.filter(follower=user).values_list('following', flat=True)
