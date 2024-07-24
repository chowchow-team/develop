from django.shortcuts import get_object_or_404
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.status import HTTP_201_CREATED, HTTP_400_BAD_REQUEST
from django.contrib.auth import get_user_model
from accountapp.token import account_activation_token
from accountapp.models import User, Profile
from accountapp.serializers import AccountCreateSerializer, ProfileSerializer
from django.conf import settings
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt # 배포시 해결할것
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from rest_framework import status, permissions
from django.contrib.auth import login, logout
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth import update_session_auth_hash
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseRedirect
from utils.school_loader import load_schools_from_json

class AccountCreateAPI(APIView):
    def post(self, request):
        serializer = AccountCreateSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            user.is_active = False
            user.save()

            current_site = get_current_site(request)
            mail_subject = '[ Mongle ]이메일 인증을 완료해주세요!'
            # URL 생성
            activation_link = request.build_absolute_uri(
                reverse('account:activate', kwargs={
                    'uidb64': urlsafe_base64_encode(force_bytes(user.pk)),
                    'token': account_activation_token.make_token(user)
                })
            )
            html_message = render_to_string('accountapp/validation_email.html', {
                'user': user,
                'activation_link': activation_link,
            })
            to_email = serializer.validated_data['email']
            send_mail(
                subject=mail_subject, 
                message="", 
                from_email='dev.mongle@gmail.com', 
                recipient_list=[to_email], 
                html_message=html_message
            )

            return Response({'message': '인증메일이 발송되었습니다. 링크를 통해 회원가입을 완료할 수 있습니다.'}, status=HTTP_201_CREATED)
        return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)
    
# 계정활성화
class ActivateAccountAPI(APIView):
    def get(self, request, uidb64, token):
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=uid)
        except(TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None
        if user is not None and account_activation_token.check_token(user, token):
            user.is_active = True
            user.save()
            #print('이메일 인증이 성공하였습니다.') # 검토후 삭제
            #return Response({'message': '이메일 인증이 완료되었습니다.'})
            if settings.DEBUG:
                return HttpResponseRedirect('http://localhost:3000/login')
            else:
                return HttpResponseRedirect('https://mongles.com/login')
        else:
            if user is not None and user.is_active==False:
                user.delete()
            if settings.DEBUG:
                return HttpResponseRedirect('http://localhost:3000/login')
            else:
                return HttpResponseRedirect('https://mongles.com/login')
            #print('이메일 인증이 실패하였습니다.') # 검토후 삭제
            #return Response({'message': '이메일 인증이 실패하였습니다.'})
        
        #HttpResponseRedirect(f'http://localhost:3000/activate/{uidb64}/{token}')
        
# 로그인
class LoginAPI(APIView):
    #@csrf_exempt # 배포시 해결할것
    def post(self, request, format=None):
        username = request.data.get("username")
        password = request.data.get("password")
        user = authenticate(username=username, password=password)
        if user:
            login(request, user)
            #token, created = Token.objects.get_or_create(user=user)
            return Response({"message": "로그인 성공"}, status=status.HTTP_200_OK)
            #return Response({"token": token.key}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "아이디/패스워드를 확인하세요."}, status=status.HTTP_400_BAD_REQUEST)
        

class LogoutAPI(APIView):
    permission_classes = [permissions.IsAuthenticated] 
    def post(self, request):
        logout(request) 
        return Response({"message": "로그아웃 되었습니다."}, status=status.HTTP_200_OK)

class UserProfileDetailAPI(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, slug, format=None):
        user = get_object_or_404(User, username=slug)
        profile = get_object_or_404(Profile, user=user)
        serializer = ProfileSerializer(profile)
        return Response(serializer.data)

class UserProfileUpdateAPI(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, slug, format=None):
        user = get_object_or_404(User, username=slug)  # username을 slug로 사용
        if request.user != user:
            return Response({'error': '권한이 없습니다.'}, status=status.HTTP_403_FORBIDDEN)
        profile, created = Profile.objects.get_or_create(user=user)
        serializer = ProfileSerializer(profile, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UsernameRecoveryAPI(APIView):
    def post(self, request):
        email = request.data.get('email')
        user_model = get_user_model()
        try:
            user = user_model.objects.get(email=email)
        except user_model.DoesNotExist:
            return Response({'error': '해당 이메일로 등록된 사용자가 없습니다.'}, status=status.HTTP_400_BAD_REQUEST)
        
        current_site = get_current_site(request)
        mail_subject = '[몽글몽글] 아이디 찾기 요청 결과입니다'
        message = "귀하의 아이디 찾기 요청에 대한 정보입니다. 이 메일은 HTML 형식으로 보내진 메일입니다. 메일 클라이언트가 HTML을 지원하지 않는 경우, 이 텍스트 메시지를 보게 됩니다."
        html_message = render_to_string('accountapp/recover_username_email.html', {
            'username': user.username,
            #'domain': current_site.domain,
            'domain': "mongles.com",
        })
        send_mail(
            subject=mail_subject, 
            message=message, 
            from_email='dev.mongle@gmail.com', 
            recipient_list=[email], 
            fail_silently=False,
            html_message=html_message
        )
        
        return Response({'message': '귀하의 아이디 정보를 이메일로 전송하였습니다.'}, status=status.HTTP_200_OK)

class PasswordResetRequestAPI(APIView): # 등록된 이메일인지확인, 새로운 비밀번호 전송
    def post(self, request):
        email = request.data.get('email')
        user_model = get_user_model()
        try:
            user = user_model.objects.get(email=email)
        except user_model.DoesNotExist:
            return Response({'error': '해당 이메일로 등록된 사용자가 없습니다.'}, status=status.HTTP_400_BAD_REQUEST)
        
        new_password = User.objects.make_random_password()  # 새로운 랜덤 비밀번호 생성
        
        user.set_password(new_password)  # 비밀번호 설정
        user.save()
        
        # 이메일에 보낼 내용 구성
        mail_subject = '[몽글몽글] 비밀번호 변경 안내'
        message = f"새로운 비밀번호: {new_password}\n로그인 후에 비밀번호를 변경해주세요.\n변경방법: 계정관리 > 비밀번호 변경"
        
        # 이메일 보내기
        send_mail(
            subject=mail_subject,
            message=message,
            from_email='dev.mongle@gmail.com',
            recipient_list=[email],
            fail_silently=False,
        )
        
        return Response({'message': '새로운 비밀번호를 이메일로 전송하였습니다.'}, status=status.HTTP_200_OK)


#class PasswordResetConfirmAPI(APIView):
#    def post(self, request, uidb64, token):
#        try:
#            uid = force_str(urlsafe_base64_decode(uidb64))
#            user = User.objects.get(pk=uid)
#        except(TypeError, ValueError, OverflowError, User.DoesNotExist):
#            user = None
#        
#        if user is not None and default_token_generator.check_token(user, token):
#            new_password = request.data.get('new_password')
#            user.set_password(new_password)
#            user.save()
#            return Response({'message': '비밀번호가 재설정되었습니다.'}, status=status.HTTP_200_OK)
#        else:
#            return Response({'error': '비밀번호 재설정 링크가 유효하지 않습니다.'}, status=status.HTTP_400_BAD_REQUEST)
#    
#    def get(self, request, uidb64, token):
#        try:
#            uid = force_str(urlsafe_base64_decode(uidb64))
#            user = get_user_model().objects.get(pk=uid)
#        except (TypeError, ValueError, OverflowError, get_user_model().DoesNotExist):
#            user = None
#
#        if user is not None and default_token_generator.check_token(user, token):
#            return HttpResponseRedirect(f'http://localhost:3000/password-reset/{uidb64}/{token}')
#        else:
#            return HttpResponseBadRequest('비밀번호 재설정 요청이 유효하지 않습니다.')

class AccountDeleteAPI(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user = request.user
        user.delete()
        return Response({"message": "계정이 성공적으로 삭제되었습니다."}, status=status.HTTP_200_OK)

class ChangePasswordAPI(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user = request.user
        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')
        
        if not user.check_password(old_password):
            return Response({'error': '현재 비밀번호가 잘못되었습니다.'}, status=status.HTTP_400_BAD_REQUEST)
        
        user.set_password(new_password)
        user.save()
        # 세션 업데이트를 통해 사용자가 로그아웃되지 않도록 합니다.
        update_session_auth_hash(request, user)
        
        return Response({'message': '비밀번호가 성공적으로 변경되었습니다.'}, status=status.HTTP_200_OK)

class SchoolListView(APIView):
    def get(self, request, format=None):
        try:
            schools = load_schools_from_json()
            return Response(schools, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)