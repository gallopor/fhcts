import os
import json
from django.shortcuts import render_to_response
from django.http import HttpResponse

from velocity.velsession import VelSession
from velocity.reservation import Reservation
from velocity.execution import Execution
from velocity.settings import VELOCITY_IP, PIPELINE_SCRIPTS, \
        PIPELINE_PARAMS, NOTIFICATION_URL

from ctfm.models import Order, Task

LOG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'log')
if os.path.isdir(LOG_DIR) == False:
    os.mkdir(LOG_DIR)

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
    return render_to_response('data/result_debug.json')

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

def notification(request):
    notif = json.loads(request.body.decode())
    events = {
        'EXECUTION_START' : start,
        'EXECUTION_ISSUE' : wait,
        'EXECUTION_COMPLETE' : end,
    }
    events[notif['eventType']](notif)
    return HttpResponse('OK')

def start(notif):
    exec_id = notif['executionID']
    exec_log = os.path.join(LOG_DIR, exec_id)
    exec_info = {
        'reportID': notif['reportID'],
        'status': 'STARTED',
        'start': notif['executionStart']
    }
    if os.path.exists(exec_log):
        fp = open(exec_log, 'r+')
        log_content = json.loads(fp.read())
        log_content.update(exec_info)
        fp.seek(0)
        json.dump(log_content, fp)
        fp.flush()
        fp.close()
    return

def end(notif):
    exec_id = notif['executionID']
    exec_log = os.path.join(LOG_DIR, exec_id)
    exec_info = {
        'status': notif['executionStatus'],
        'end': notif['executionEnd'],
        'duration': notif['duration']
    }
    if os.path.exists(exec_log):
        fp = open(exec_log, 'r+')
        log_content = json.loads(fp.read())
        log_content.update(exec_info)
        fp.seek(0)
        json.dump(log_content, fp)
        fp.flush()
        fp.close()
        
        resultsDump(log_content)
    return

def wait(notif):
    pass

def resultsDump(log):
    fp = open('ctfm/template/data/result_debug.json', 'r+')
    rj = json.loads(fp.read())
    
    log.pop('blade')
    codes = log.pop('codes').values()
    
    order = None
    for c in codes:
        if order is None:
            order = c[0:5]
        rj['tasks'][order]['blades'][c] = log
    fp.seek(0)
    json.dump(rj, fp, indent=4)
    fp.flush()
    fp.close()
    return

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
                            order_id = c[0:5], \
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
    if os.path.exists(os.path.join(LOG_DIR, exec_id)):
        fp = open(os.path.join(LOG_DIR, exec_id), 'r')
        print(fp.read())
    return render_to_response(os.path.join(LOG_DIR, exec_id))
