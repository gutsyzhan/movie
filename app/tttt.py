#
#
# from werkzeug.security import generate_password_hash
#
# print(generate_password_hash('1242'))

import uuid

a = [(1, " 你好"), (2, "不错"), (3, "加油")]
l=[]
for x in a:
    print(x[0], type(x[0]))
    l.append(x[0])
    print(l, type(l))
print("***************************")
# list(map(lambda x:x[0])for x in a)
print(list(map(lambda x:x[0],[(1, " 你好"), (2, "不错"), (3, "加油")])))

print(list(map(lambda x:x[0],form.auths.choices)))
