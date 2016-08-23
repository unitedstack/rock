# -*-coding utf-8 -*-
#


import commands
import time
import multiprocessing


def fun1():
    while True:
        status = commands.getoutput('systemctl is-active openstack-nova-compute')
        print status
        if status != 'active':
            status = commands.getoutput('systemctl start openstack-nova-compute')
        time.sleep(1)


def fun2():
    while True:
        status = commands.getoutput('systemctl is-active openstack-nova-api')
        print status
        if status != 'active':
            status = commands.getoutput('systemctl start openstack-nova-api')
        time.sleep(1)


process = []
if __name__ == '__main__':
    p1 = multiprocessing.Process(target=fun1)
    p2 = multiprocessing.Process(target=fun2)
    process.append(p1)
    process.append(p2)

    for t in process:
        t.start()

    for t in process:
        t.join()


