import os


class IPMITool():
    
    def __init__(self, target, username, password):
        self._target = target
        self._username = username
        self._password = password
 
    def power_on(self):
        cmd = 'ipmitool -I lanplus -H ' +str(self._target) + ' -U ' \
              + str(self._username) + ' -P '+ str(self._password) +' chassis power on'
        os.system(cmd)

    def power_off(self):
        cmd = 'ipmitool -I lanplus -H ' +str(self._target) + ' -U ' \
              + str(self._username) + ' -P '+ str(self._password) +' chassis power off'
        os.system(cmd)

    def power_cycle(self):
        cmd = 'ipmitool -I lanplus -H ' +str(self._target) + ' -U ' \
              + str(self._username) + ' -P '+ str(self._password) +' chassis power cycle'
        os.system(cmd)

    def power_reset(self):
        cmd = 'ipmitool -I lanplus -H ' +str(self._target) + ' -U ' \
              + str(self._username) + ' -P '+ str(self._password) +' chassis power reset'
        os.system(cmd)

    def power_status(self):
        cmd = 'ipmitool -I lanplus -H ' +str(self._target) + ' -U ' \
              + str(self._username) + ' -P '+ str(self._password) +' chassis power status'
        os.system(cmd)
    
