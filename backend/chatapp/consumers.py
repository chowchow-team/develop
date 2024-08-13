import json
import random
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
import asyncio
from django.contrib.auth import get_user_model
import notificationapp
import os
import uuid
import redis.asyncio as redis


class ChatConsumer(AsyncWebsocketConsumer):
    lock = asyncio.Lock()

    async def connect(self):
        redis_url = os.environ.get('REDIS_URL')
        if redis_url!="redis://redis":
            redis_url = "redis://localhost"
        self.user = self.scope['user']

        query_string = self.scope["query_string"].decode("utf-8")
        query_params = dict(qc.split("=") for qc in query_string.split("&"))
        connection_type = query_params.get("type")
        friend_username = query_params.get("friend_username")

        try:
            self.room_name = self.scope['url_route']['kwargs']['room_name']
        except:
            self.room_name = None

        if self.user.is_authenticated:
            await self.accept()
            # Redis에 연결 # 주소 잠깐 서버용으로. 로컬과 범용성있게 바꿀것. 환경변수활용
            self.redis = await redis.from_url(redis_url, encoding="utf-8", decode_responses=True)
            # 매칭 로직 실행
            #asyncio.create_task(self.attempt_matching())

            #if self.room_name == None and connection_type=="random": # 디엠기능에서도 이게 논으로 뜰 수 있음
            #    print("room_name is None")
            #    await self.attempt_matching()
            #else:
            #    print(f"room_name: {self.room_name}")
            #    if "random" in self.room_name:
            #        await self.attempt_matching()
            #    elif "dm" in self.room_name:
            #        await self.setup_direct_message()
            
            if connection_type=="random":
                await self.attempt_matching()
            elif connection_type=="dm" and friend_username:
                await self.setup_direct_message(friend_username)
    
    async def setup_direct_message(self, friend_username):
        sorted_usernames = sorted([self.user.username, friend_username])
        room_name = f"dm_{sorted_usernames[0]}_{sorted_usernames[1]}"
        self.room_name = room_name
        await self.channel_layer.group_add(room_name, self.channel_name)
        await self.redis.set(f"dm_room_name_{self.user.username}", room_name)

    async def setup_friend_list(self, friend_list):
        print(f"setup_friend_list: {friend_list}")
        for friend_username in friend_list:
            sorted_usernames = sorted([self.user.username, friend_username])
            room_name = f"dm_{sorted_usernames[0]}_{sorted_usernames[1]}"
            self.room_name = room_name
            await self.channel_layer.group_add(room_name, self.channel_name)
            await self.redis.set(f"dm_room_name_{self.user.username}", room_name)

    @database_sync_to_async
    def get_user_school(self, username):
        User = get_user_model()
        user = User.objects.filter(username=username).first()

        schools = load_schools_from_json()
        school_id_to_name = {str(school['id']): school['name'] for school in schools}

        if user and user.school in school_id_to_name:
            return school_id_to_name[user.school]
        return "알 수 없는 학교"

    """
    async def attempt_matching(self):
        async with self.lock:
            await self.redis.set(f"channel_name_{self.user.username}", self.channel_name)
            await self.redis.sadd("waiting_users", self.user.username)
            waiting_users = await self.redis.smembers("waiting_users")
            if len(waiting_users) > 1:
                peer_user = random.choice(list(waiting_users - {self.user.username}))
                await self.redis.srem("waiting_users", self.user.username, peer_user)

                sorted_usernames = sorted([self.user.username, peer_user])
                room_name = f"chat_{sorted_usernames[0]}_{sorted_usernames[1]}"
                await self.channel_layer.group_add(room_name, self.channel_name)
                await self.redis.set(f"room_name_{self.user.username}", room_name)

                peer_channel_name = await self.redis.get(f"channel_name_{peer_user}")
                if peer_channel_name:
                    await self.channel_layer.group_add(room_name, peer_channel_name)
                    await self.redis.set(f"room_name_{peer_user}", room_name)

                peer_school = await self.get_user_school(peer_user)
                your_school = await self.get_user_school(self.user.username)
                await self.channel_layer.group_send(room_name, {
                    'type': 'match_success_message',
                    'message': [{"username":peer_user, "school":peer_school}, 
                                {"username":self.user.username, "school":your_school}]
                })
    """

    async def attempt_matching(self):
        async with self.lock:
            await self.redis.set(f"channel_name_{self.user.username}", self.channel_name)
            await self.redis.sadd("waiting_users", self.user.username)
            waiting_users = await self.redis.smembers("waiting_users")
            
            # 채팅 중인 사용자를 제외해서 대기중인 사용자 집합 생성함.
            available_users = set()
            for user in waiting_users:
                room_name = await self.redis.get(f"room_name_{user}")
                if not room_name:
                    available_users.add(user)
            
            if len(available_users) > 1:
                peer_user = random.choice(list(available_users - {self.user.username}))
                await self.redis.srem("waiting_users", self.user.username, peer_user)

                sorted_usernames = sorted([self.user.username, peer_user])
                room_name = f"chat_{sorted_usernames[0]}_{sorted_usernames[1]}"
                await self.channel_layer.group_add(room_name, self.channel_name)
                await self.redis.set(f"room_name_{self.user.username}", room_name)

                peer_channel_name = await self.redis.get(f"channel_name_{peer_user}")
                if peer_channel_name:
                    await self.channel_layer.group_add(room_name, peer_channel_name)
                    await self.redis.set(f"room_name_{peer_user}", room_name)

                peer_school = await self.get_user_school(peer_user)
                your_school = await self.get_user_school(self.user.username)
                await self.channel_layer.group_send(room_name, {
                    'type': 'match_success_message',
                    'message': [{"username": peer_user, "school": peer_school}, 
                                {"username": self.user.username, "school": your_school}]
                })


    async def disconnect(self, close_code):
        if hasattr(self, 'redis'):
            room_name = await self.redis.get(f"room_name_{self.user.username}")
            if room_name:
                await self.channel_layer.group_discard(room_name, self.channel_name)
            await self.redis.srem("waiting_users", self.user.username)
            await self.redis.delete(f"room_name_{self.user.username}")
            await self.redis.close()

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_type = text_data_json['type']

        if message_type == 'chat_message':
            message = text_data_json['message']
            room_name = await self.redis.get(f"room_name_{self.user.username}")
            if room_name:
                await self.channel_layer.group_send(room_name, {
                    'type': 'chat_message',
                    'message': message,
                    'sender': self.user.username
                })
        elif message_type == 'dm_message':
            message = text_data_json['message']
            room_name = await self.redis.get(f"dm_room_name_{self.user.username}")
            if room_name:
                message = await self.save_message(self.user.username, room_name, message)
                print(f"dm문제 확인중. message: {message.id}")
                await self.channel_layer.group_send(room_name, {
                    'message': [message.message, message.id],
                    'type': 'dm_message',
                    'sender': message.sender.username,
                })
            #await database_sync_to_async(self.save_message)(self.user.username, room_name, message)
            
        elif message_type == 'friend_list':
            friend_list = text_data_json['username_list']
            print(f"friend_list: {friend_list}")
            await self.setup_friend_list(friend_list)

        elif message_type == 'start_dm':
            my_username = self.user.username
            friend_username = text_data_json.get('friend_username')
            # 레디스에 dm_active 설정
            key = f"dm_active:{my_username}:{friend_username}"
            await self.redis.set(key, "True")
            await self.setup_direct_message(friend_username)
        
        elif message_type == 'end_dm': # 웹소켓은 종료안하고, 키만 삭제하면 됨.
            my_username = self.user.username
            friend_username = text_data_json.get('friend_username')
            # 레디스에 dm_active 설정
            key = f"dm_active:{my_username}:{friend_username}"
            await self.redis.delete(key)

        elif message_type == 'start_chat':
            await self.attempt_matching()

        elif message_type == 'chat_end':
            await self.end_chat()

        elif message_type in ['typing_start', 'typing_end']:
            room_name = await self.redis.get(f"room_name_{self.user.username}")
            if room_name:
                await self.channel_layer.group_send(room_name, {
                    'type': f'{message_type}_message',
                    'sender': self.user.username
                })
        
        elif message_type == 'accept_friend_request' or message_type == 'reject_friend_request':
            print(f"receive: {message_type}") # 여기 체크해보자. text_data_json 까보면 될듯. 아예 안받는디?
            print(f"receive: {text_data_json}")
            if 'from_username' in text_data_json:
                if message_type == 'accept_friend_request':
                    print(f"accept_friend_request: {text_data_json['from_username']}")
                    await self.accept_friend_request(text_data_json['from_username'])
                else:
                    room_name = await self.redis.get(f"room_name_{self.user.username}")
                    if room_name:
                        await self.channel_layer.group_send(room_name, {
                            'type': 'reject_friend_request'
                        })
                    await self.reject_friend_request(text_data_json['from_username'])
        elif message_type == 'send_friend_request':
            if 'to_username' in text_data_json:
                await self.handle_send_friend_request(text_data_json['to_username'])
    
    # 비동기로 바꿔야 할 함수를 동기 방식으로 정의
    def save_message_sync(self, sender_username, room_name, message):
        from .models import Message
        User = get_user_model()
        
        # User 모델에서 sender와 receiver를 동기적으로 가져옴
        sender = User.objects.get(username=sender_username)
        _, first_username, second_username = room_name.split('_')
        receiver_username = second_username if sender_username == first_username else first_username
        receiver = User.objects.get(username=receiver_username)
        
        # 메시지를 데이터베이스에 저장
        message=Message.objects.create(sender=sender, receiver=receiver, message=message)
        return message
    
    # save_message_sync 함수를 비동기적으로 실행할 수 있도록 래핑
    async def save_message(self, sender_username, room_name, message):
        message_instance = await database_sync_to_async(self.save_message_sync)(sender_username, room_name, message)
        
        my_username = self.user.username
        friend_username = [username for username in room_name.split("_") if username != my_username][1]
        my_key = f"dm_active:{my_username}:{friend_username}"
        friend_key = f"dm_active:{friend_username}:{my_username}"
        my_dm_status = await self.redis.get(my_key)
        friend_dm_status = await self.redis.get(friend_key)
        # 나와 상대가 모두 dm접속 상태가 아니라면 알림을 생성
        if (my_dm_status == "False" or my_dm_status == None) or (friend_dm_status == "False" or friend_dm_status == None):
            await self.create_notification(message_instance)
        return message_instance
    
    async def create_notification(self, message_instance):
        # 비동기적으로 알림을 생성하는 메서드입니다.
        await database_sync_to_async(self.create_notification_sync)(message_instance)

    def create_notification_sync(self, message_instance):
        # 실제로 알림을 생성하는 동기 메서드입니다.
        notificationapp.models.Notification.objects.create(
            notification_type=0,  # 'dm'에 해당하는 코드
            sender=message_instance.sender,
            receiver=message_instance.receiver,
            text_preview=message_instance.message[:20],  # 필요에 따라 조정
            user_has_seen=False
        )
    
    
    async def end_chat(self):
        room_name = await self.redis.get(f"room_name_{self.user.username}")
        if room_name:
            # 채팅 종료 알림을 채팅방의 모든 참여자에게 전송
            await self.channel_layer.group_send(room_name, {
                'type': 'chat_end_message',
            })
            
            # 채팅방에서 사용자를 제거
            await self.channel_layer.group_discard(room_name, self.channel_name)


    async def accept_friend_request(self, friend_username):
        from friendapp.models import Friendship, FriendRequest
        # 비동기로 친구 요청을 조회
        friend_request = await self.get_friend_request(friend_username)
        if friend_request:
            from_user_instance = await database_sync_to_async(FriendRequest.objects.get)(pk=friend_request.pk)
            from_user = await database_sync_to_async(lambda: from_user_instance.from_user)()
            
            # 비동기로 친구 관계 생성
            await database_sync_to_async(Friendship.create_friendship)(self.user, from_user)
            room_name = await self.redis.get(f"room_name_{self.user.username}")
            if room_name:
                await self.channel_layer.group_send(room_name, {
                    'type': 'send_friend_request_response',  # 이 메서드는 아래에 정의해야 합니다.
                    'response_type': 'accept_friend_request'
                })
            
            # 비동기로 FriendRequest 인스턴스 삭제
            await database_sync_to_async(friend_request.delete)()


    async def reject_friend_request(self, friend_username):
        # 비동기로 친구 요청을 조회
        friend_request = await self.get_friend_request(friend_username)
        if friend_request:
            room_name = await self.redis.get(f"room_name_{self.user.username}")
            if room_name:
                await self.channel_layer.group_send(room_name, {
                    'type': 'send_friend_request_response',  # 이 메서드는 아래에 정의해야 합니다.
                    'response_type': 'reject_friend_request'
                })
            # 비동기로 FriendRequest 인스턴스 삭제
            await database_sync_to_async(friend_request.delete)()
    
    async def get_friend_request(self, friend_username):
        from friendapp.models import FriendRequest
        friend_request_query = await database_sync_to_async(FriendRequest.objects.filter)(
            from_user__username=friend_username,
            to_user=self.user
        )
        friend_request = await database_sync_to_async(friend_request_query.first)()
        return friend_request


        
   
    async def handle_send_friend_request(self, to_username):
        room_name = await self.redis.get(f"room_name_{self.user.username}")
        if room_name:
            usernames = room_name.split("_")[1:]  # room_name이 "chat_user1_user2" 형식이라고 가정
            peer_username = [username for username in usernames if username != self.user.username][0]

            User = get_user_model()
            peer_user = await database_sync_to_async(User.objects.get)(username=peer_username)

            from friendapp.models import FriendRequest
            friend_request = await database_sync_to_async(FriendRequest.objects.create)(
                from_user=self.scope['user'],
                to_user=peer_user
            )
            
            peer_channel_name = await self.redis.get(f"channel_name_{peer_username}")
            if peer_channel_name:
                await self.channel_layer.send(peer_channel_name, {
                    "type": "friend_request",
                    "from_username": self.user.username,
                    "peer_username": peer_username
                })



    ###########################
    #                         #
    # 아래는 전부 처리로직들. 핸들러 #
    #                         #
    ###########################
    async def chat_message(self, event):
        message = event['message']
        sender = event['sender']
        await self.send(text_data=json.dumps({
            'type': 'chat',
            'message': message,
            'sender': sender
        }))

    async def match_success_message(self, event):
        # 매칭 성공 메시지 처리 로직
        message = event['message']
        print(f"[match_success_message] Handling 'match_success_message' event: {message}")

        # WebSocket 클라이언트에 매칭 성공 메시지 전송
        await self.send(text_data=json.dumps({
            'type': 'match_success',
            'message': message
        }))
    
    async def chat_end_message(self, event):
        # 채팅 종료 처리 로직
        await self.send(text_data=json.dumps({
            'type': 'chat_end',
            'message': '채팅이 종료되었습니다.'
        }))
    
    async def typing_start_message(self, event):
        # 클라이언트에 타이핑 시작 메시지 전송
        await self.send(text_data=json.dumps({
            'type': 'typing_start',
            'sender': event['sender']
        }))

    async def typing_end_message(self, event):
        # 클라이언트에 타이핑 종료 메시지 전송
        await self.send(text_data=json.dumps({
            'type': 'typing_end',
            'sender': event['sender']
        }))

    async def friend_request(self, event):
        # 친구 요청 메시지를 클라이언트에 전송
        await self.send(text_data=json.dumps({
            'type': 'friend_request',
            'from_username': event['from_username'],
            'peer_username': event['peer_username']
        }))
    
    async def dm_message(self, event):
        message = event['message']
        sender = event['sender']

        await self.send(text_data=json.dumps({
            'type': 'dm_message',
            'message': message,
            'sender': sender
        }))

    async def send_friend_request_response(self, event):
        # 클라이언트로 보낼 메시지 구성
        response_type = event['response_type']

        # 클라이언트에게 메시지 전송
        await self.send(text_data=json.dumps({
            'type': response_type,  # 클라이언트가 이해할 수 있는 메시지 타입
        }))



class CountConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        redis_url = os.environ.get('REDIS_URL')
        if redis_url != "redis://redis":
            redis_url = "redis://localhost"
        self.redis = await redis.from_url(redis_url, encoding="utf-8", decode_responses=True)
        self.user = self.scope["user"]
        if self.user.is_authenticated:
            await self.channel_layer.group_add("online_users_group", self.channel_name)
            await self.accept()
            await self.add_online_user()
        else:
            await self.close()

    async def disconnect(self, close_code):
        if self.user.is_authenticated:
            await self.remove_online_user()
            await self.channel_layer.group_discard("online_users_group", self.channel_name)
        await self.redis.close()

    async def add_online_user(self):
        try:
            username = self.user.username
            online_users = await self.redis.lrange("online_users_list", 0, -1)
            if username not in online_users:
                await self.redis.rpush("online_users_list", username)
        except Exception as e:
            print(f"Add User Error: {e}")

        await self.update_online_users_count()

    async def remove_online_user(self):
        try:
            username = self.user.username
            await self.redis.lrem("online_users_list", 1, username)
        except Exception as e:
            print(f"Remove User Error: {e}")

        await self.update_online_users_count()

    @staticmethod
    async def get_online_users_count():
        redis_url = os.environ.get('REDIS_URL')
        if redis_url != "redis://redis":
            redis_url = "redis://localhost"
        redis = await redis.from_url(redis_url, encoding="utf-8", decode_responses=True)
        online_users = await redis.lrange("online_users_list", 0, -1)
        return len(online_users)

    async def update_online_users_count(self):
        count = await self.get_online_users_count()
        await self.channel_layer.group_send("online_users_group", {
            "type": "update_online_users_count_message",
            "count": count
        })

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_type = text_data_json['type']

        if message_type == 'get_online_users_count':
            count = await self.get_online_users_count()
            await self.send(text_data=json.dumps({
                'type': 'online_users_count',
                'count': count
            }))

    async def update_online_users_count_message(self, event):
        count = event['count']
        await self.send(text_data=json.dumps({
            'type': 'online_users_count',
            'count': count
        }))