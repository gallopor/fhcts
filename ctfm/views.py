import json
from django.shortcuts import render_to_response
from django.http import HttpResponse

from ctfm.models import Task

from velocity.velsession import VelSession
from velocity.reservation import Reservation
from velocity.execution import Execution
from velocity.settings import VELOCITY_IP, PIPELINE_SCRIPTS, \
        PIPELINE_PARAMS, NOTIFICATION_URL

def index(request):
    return render_to_response('index.html')

def login(request):
    return render_to_response('login.html')

def dashboard(request):
    return render_to_response('dashboard.html')

def testing(request):
    return render_to_response('testing.html')

def get_process(request):
    return render_to_response('data/task_process.json')

def get_schedule(request):
    return render_to_response('data/schedule.json')

def get_utilization(request):
    return render_to_response('data/utilization.json')

def get_results(request):
    resv_id = request.POST['resv_id']
    results = {}
    ''' 在Task表单中查询执行状态 '''
    for t in Task.objects.filter(resv_id = resv_id):
        item =  {t.part_sn: {'status': t.exec_status, \
                             'start_time': t.start_time, \
                             'duration': t.duration}}
        results.update(item) 
    return HttpResponse(json.dumps(results))

def auth(request):
    user = request.POST['user']
    pswd = request.POST['pswd']
    vs = VelSession(host=VELOCITY_IP, user=user, pswd=pswd)
    return HttpResponse(vs.token())

def reserve(request):
    token = request.POST['token']
    topo = request.POST['topo']
    duration = request.POST['duration']
    vs = VelSession(host=VELOCITY_IP, token=token)
    rsv = Reservation(vs)
    r_info = rsv.topoReserve(name=topo, duration=duration)
    ret = {'status': '', 'msg': '', 'id': ''}
    if('id' in r_info):
        ret['status'] = True
        ret['id'] = r_info['id']
    else:
        ret['status'] = False
        ret['msg'] = r_info['errorId']
    return HttpResponse(json.dumps(ret))

def get_reservations(request):
    token = request.POST['token']
    vs = VelSession(host=VELOCITY_IP, token=token)
    rsv = Reservation(vs)
    
    ret = {'resv_id': ''}
    rsv_info = rsv.getActResvByMe()
    if rsv_info['total'] > 0:
        ret['resv_id'] = rsv_info['reservations'][0]['id']
    return HttpResponse(json.dumps(ret))

def notification(request):
    notif = json.loads(request.body.decode())
    print(notif)
    events = {
        'EXECUTION_START' : start,
        'EXECUTION_ISSUE' : wait,
        'EXECUTION_COMPLETE' : end,
    }
    events[notif['eventType']](notif)
    return HttpResponse('OK')

def start(notif):
    exec_id = notif['executionID']
    ''' 更新Task表单数据 '''
    for t in Task.objects.filter(exec_id = exec_id):
        t.exec_status = 'STARTED'
        t.start_time = notif['executionStart']
        t.save()                
    return

def end(notif):
    exec_id = notif['executionID']
    ''' 更新Task表单数据 '''
    for t in Task.objects.filter(exec_id = exec_id):
        t.exec_status = notif['executionStatus']
        t.duration = notif['duration']
        t.save() 
    return

def wait(notif):
    pass

def task_exec(request):
    token = request.POST['token']
    resv_id = request.POST['resv_id']
    pipeline = request.POST['pipeline']
    blade = request.POST['blade']
    codes = json.loads(request.POST['codes'])

    ''' 添加数据到Task表单 '''
    for c in codes.values():
        Task.objects.create(part_sn = c, \
                            model = blade, \
                            resv_id = resv_id)

    script = PIPELINE_SCRIPTS[pipeline]
    params = PIPELINE_PARAMS[pipeline]
    i = 0
    j = 0
    for p in params:
        if p['name'] == 'SlotsCode':
            for c in p['parameters']:
                params[i]['parameters'][j]['value'] = codes[c['name']]
                j += 1
        i += 1
    vs = VelSession(host=VELOCITY_IP, token=token)
    ex = Execution(vs)
    ex_info = ex.testExec(script, parametersList=params, \
                          callbackURL=NOTIFICATION_URL)
    ret = {'status': '', 'msg': '', 'id': ''}
    if('executionID' in ex_info):
        ret['status'] = True
        ret['id'] = ex_info['executionID']
        
        ''' 更新Task表单数据 '''
        for c in codes.values():
            t = Task.objects.get(part_sn = c)
            t.exec_id = ex_info['executionID']
            t.save()                
    else:
        ret['status'] = False
        ret['msg'] = ex_info['errorId']
    return HttpResponse(json.dumps(ret))

def exec_status(request):
    exec_id = request.POST['exec_id']
    es = {'status': ''}
    ''' 在Task表单中查询执行状态 '''
    t = Task.objects.filter(exec_id = exec_id)[0]
    es['status'] = t.exec_status
    return HttpResponse(json.dumps(es))
