from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.base import ContentFile
from .models import Video

@csrf_exempt
def upload_video(request):
    if request.method == 'POST':
        video_data = request.FILES['video']
        video = Video(video_file=video_data)
        video.save()

        # 최대 4개의 동영상만 유지 (현재 촬영 중인 비디오 포함)
        videos = Video.objects.all().order_by('-timestamp')
        if videos.count() > 4:
            for old_video in videos[4:]:
                old_video.video_file.delete()
                old_video.delete()

        return JsonResponse({'message': 'Video uploaded successfully'})

def get_latest_videos(request):
    videos = Video.objects.all().order_by('-timestamp')[:3]
    video_urls = [video.video_file.url for video in videos]
    return JsonResponse({'video_urls': video_urls})
