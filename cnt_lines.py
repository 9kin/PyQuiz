files = [
    'api.py',
    'config_stuff.py',
    'config.csv',
    'constants.py',
    'main.py',
    'server_api.py'
]
s = 0
for i in files:
    f = list(map(str.strip, open(i).readlines()))
    ans = 0
    for i in f:
        if i != '':
            ans += 1
    s += ans
    print(ans)
print(s)
