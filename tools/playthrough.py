import urllib.request, urllib.parse, http.cookiejar, json, time

cj = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
base = 'http://127.0.0.1:8787'

def post(path, payload=None):
    data = None
    if payload is not None:
        data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(base + path, data=data, headers={'Content-Type':'application/json'})
    with opener.open(req, timeout=10) as resp:
        txt = resp.read().decode('utf-8')
        try:
            return json.loads(txt)
        except Exception:
            return txt

print('Reset')
print(post('/api/reset'))
print('New game')
state = post('/api/new-game')
print('Started?', state.get('started'))
print('Pending choice id:', state.get('pending_choice', {}).get('id'))

# make the prologue choice
print('Making choice ask_guidance')
try:
    state = post('/api/choice', {'choice':'ask_guidance'})
    print('Choice result, unlocked actions:', [a['id'] for a in state.get('actions',[])])
except Exception as e:
    print('Choice failed', e)

# queue 3 gather_dew
print('Queue 3 gather_dew')
state = post('/api/action', {'action':'gather_dew', 'count':3})
print('Action queue (aggregated):', state.get('action_queue'))
print('activity:', state.get('activity'))

# poll state every 1s for 8s
for i in range(8):
    time.sleep(1)
    s = post('/api/state')
    print('t=', i+1, 'activity=', bool(s.get('activity')), 'progress=', s.get('activity',{}).get('progress'), 'queue=', s.get('action_queue'))

print('Final state snapshot:')
print(json.dumps(post('/api/state'), indent=2))
