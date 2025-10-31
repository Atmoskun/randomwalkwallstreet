# mailinglist/urls.py (这是新文件)
from django.urls import path
from . import views

urlpatterns = [
    # 当用户访问网站根目录 (空路径 '')
    # 运行 views.py 里的 index 函数
    path('', views.index, name='index'), 
]