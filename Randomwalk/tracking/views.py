from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import SiteVisit
import json

# 这里使用 csrf_exempt 是为了简化演示，生产环境建议配置 CSRF token
@csrf_exempt 
def update_visit_time(request):
    if request.method == 'POST':
        try:
            # 1. 解析前端发来的数据
            data = json.loads(request.body)
            path = data.get('path')
            duration = data.get('duration')
            session_key = request.session.session_key

            # 2. 找到最近的一次访问记录 (匹配 Session 和 Path)
            # 我们使用 .last() 获取该用户在该页面的最后一次访问
            visit = SiteVisit.objects.filter(
                session_key=session_key, 
                path=path
            ).last()

            # 3. 更新时长
            if visit:
                visit.time_spent_seconds = float(duration)
                visit.save()
                return JsonResponse({'status': 'success'})
            
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

    return JsonResponse({'status': 'invalid method'}, status=405)
# Create your views here.
