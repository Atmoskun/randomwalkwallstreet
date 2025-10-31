# mailinglist/views.py

from django.shortcuts import render
from .models import Submission  # 导入你的 Submission 模型

def index(request):
    
    # 1. 准备一个空的消息变量
    message_to_show = ""
    
    # 2. 检查用户是否按了 "提交" 按钮 (POST)
    if request.method == "POST":
        
        # 3. 从表单里把数据拿出来
        #    (对应 index.html 里的 name="username")
        name_from_form = request.POST.get("username")
        #    (对应 index.html 里的 name="email")
        email_from_form = request.POST.get("email")
        
        # 4. 检查一下 (虽然HTML里有required, 再检查一次更安全)
        if name_from_form and email_from_form:
        
            # 5. 把数据存到数据库里
            Submission.objects.create(
                username=name_from_form, 
                email=email_from_form
            )
            
            # 6. 准备一句 "提交成功" 的话
            message_to_show = "提交成功！谢谢你，" + name_from_form
        
        else:
            # 7. 如果有人绕过了HTML的 "required"
            message_to_show = "请填好所有信息哦！"

    # 8. 
    # 把 index.html 网页显示出来
    # 并且把 'success_message' 变量传给HTML
    #
    # (注意：路径要和你的一致 'mailinglist/index.html')
    return render(request, 'mailinglist/index.html', {
        'success_message': message_to_show
    })