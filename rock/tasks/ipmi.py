import os


class IPMITool():
    
    def __init__(self, target, username, password):
        self._target = target
        self._username = username
        self._password = password
 
    def power_on(self):
<<<<<<< HEAD
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
=======
        cmd = ipmitool -I lanplus -H self._target -U self._username -P self._password power on

    def power_off(self):
        cmd = ipmitool -I lanplus -H self._target -U self._username -P self._password power off 

    def power_cycle(self):
        cmd = ipmitool -I lanplus -H self._target -U self._username -P self._password power cycle

    def power_reset(self):
        cmd = ipmitool -I lanplus -H self._target -U self._username -P self._password power reset
>>>>>>> 16f9b8a4eeb66a08662cfce3e7fce66ae2c3b10d

    def power_status(self):
        cmd = 'ipmitool -I lanplus -H ' +str(self._target) + ' -U ' \
              + str(self._username) + ' -P '+ str(self._password) +' chassis power status'
        os.system(cmd)
    
