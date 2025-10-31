# mailinglist/views.py
from django.shortcuts import render, redirect
from django.contrib import messages  # 用来发送“成功”消息
from .models import Submission      # 导入我们的数据库“蓝图”

def index(request):
    # 检查是不是 POST 提交数据
    if request.method == "POST":
        # 1. 从表单获取数据
        username = request.POST.get("username", "").strip()
        email = request.POST.get("email", "").strip()

        # 2. 检查数据是不是空的
        if username and email:
            # 3. 存到数据库里！
            Submission.objects.create(username=username, email=email)

            # 4. 发一个“成功”消息
            messages.success(request, 'Success submit!')

            # 5. 重定向回首页 (防止刷新页面时重复提交)
            return redirect('index')

        else:
            # 6. 如果数据不完整，发一个“错误”消息
            messages.error(request, 'Please provide both a user name and an email address.')
            # 并且重新显示表单页面
            return render(request, 'mailinglist/index.html')

    # 如果只是普通访问 (GET)，就显示表单页面
    return render(request, 'mailinglist/index.html')