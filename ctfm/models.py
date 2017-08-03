from django.db import models

# Create your models here.
class Order(models.Model):
    ''' 表的结构 '''
    order_id = models.IntegerField(primary_key=True)        # 订单号
    model = models.CharField(max_length=16)                 # 产品型号
    count = models.IntegerField()                           # 数量
    status = models.CharField(max_length=16)                # 订单状态
    hw_version = models.CharField(max_length=16)            # 硬件版本
    hw_update_time = models.TimeField                       # 硬件版本更新时间
    sw_version = models.CharField(max_length=16)            # 软件版本
    sw_update_time = models.TimeField                       # 软件版本更新时间
    
class Task(models.Model):
    ''' 表的结构 '''
    part_sn = models.IntegerField(primary_key=True)         # 产品序列号
    order_id = models.IntegerField()                        # 订单号
    model = models.CharField(max_length=16)                 # 产品型号
    resv_id = models.CharField(max_length=64)               # 资源预约识别号
    exec_id = models.CharField(max_length=64)               # 任务执行识别号
    exec_status = models.CharField(max_length=16)           # 任务执行状态
    start_time = models.TimeField                           # 测试开始时间
    duration = models.DurationField                         # 测试时长
    version_case_result = models.BooleanField               # 版本验证结果
    version_case_report = models.TextField                  # 版本验证报告
    switch_case_result = models.BooleanField                # 倒换测试结果
    switch_case_report = models.TextField                   # 倒换测试报告
    forward_case_result = models.BooleanField               # 转发测试结果
    forward_case_report = models.TextField                  # 转发测试报告
    