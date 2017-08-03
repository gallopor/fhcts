from django.db import models

# Create your models here.
class Order(models.Model):
    ''' 表的结构 '''
    id = models.IntegerField(primary_key=True)                  # 订单号
    model = models.CharField(max_length=16)                     # 产品型号
    count = models.IntegerField(null=True)                               # 数量
    status = models.CharField(max_length=16, default='')        # 订单状态
    hw_version = models.CharField(max_length=16, default='')    # 硬件版本
    hw_update_time = models.IntegerField(null=True)             # 硬件版本更新时间
    sw_version = models.CharField(max_length=16, default='')    # 软件版本
    sw_update_time = models.IntegerField(null=True)             # 软件版本更新时间
    
class Task(models.Model):
    ''' 表的结构 '''
    part_sn = models.IntegerField(primary_key=True)             # 产品序列号
    order_id = models.IntegerField()                            # 订单号
    model = models.CharField(max_length=16)                     # 产品型号
    resv_id = models.CharField(max_length=64, default='')       # 资源预约识别号
    exec_id = models.CharField(max_length=64, default='')       # 任务执行识别号
    exec_status = models.CharField(max_length=16, default='')   # 任务执行状态
    start_time = models.IntegerField(null=True)                 # 测试开始时间
    duration = models.IntegerField(null=True)                   # 测试时长
    version_case_result = models.NullBooleanField()             # 版本验证结果
    version_case_report = models.TextField(default='')          # 版本验证报告
    switch_case_result = models.NullBooleanField()              # 倒换测试结果
    switch_case_report = models.TextField(default='')           # 倒换测试报告
    forward_case_result = models.NullBooleanField()             # 转发测试结果
    forward_case_report = models.TextField(default='')          # 转发测试报告

if __name__ == "__main__":
#     ''' 添加Order对象 '''
#     Order.objects.create(id = 11111, \
#                          model = '2201110R1A', \
#                          count = 10, \
#                          status = '')
# 
#     ''' 添加Task对象 '''
#     init = 111112230001
#     i = 0
#     while i < 10:
#         sn = str(init + i)
#         Task.objects.create(part_sn = sn, \
#                             model = '2201110R1A', \
#                             order_id = 11111)
#  
#         i += 1           

    init = 1101
    i = 0
    for t in Task.objects.all()[0:5]:
        t.resv_id = 1001
        t.exec_id = init + i
        t.exec_status = 'COMPLETED'
        t.version_case_result=True
        t.switch_case_result=True
        t.forward_case_result=True
        t.save()
        i += 1
