"""tp URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url

from ctfm.views import auth, login, index, dashboard, testing, \
        get_process, get_schedule, get_utilization, get_results, \
        reserve, task_exec, exec_status, notification

urlpatterns = [
    url(r'^index/$', index),
    url(r'^index/dashboard.html/$', dashboard),
    url(r'^index/testing.html/$', testing),
    url(r'^login/$', login),
    url(r'^process/$', get_process),
    url(r'^schedule/$', get_schedule),
    url(r'^utilization/$', get_utilization),
    url(r'^result/$', get_results),
    url(r'^auth/$', auth),
    url(r'^notification/$', notification),
    url(r'^reserve/$', reserve),
    url(r'^taskExec/$', task_exec),
    url(r'^execStatus/$', exec_status)
]

