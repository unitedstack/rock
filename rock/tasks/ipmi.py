import os


class IPMITool():
    
    def __init__(self,target,username,password):
        self._target = target
        self._username = username
        self._password = password
        
    def power_on(self):
        cmd = ipmitool -I lanplus -H self._target -U self._username -P self.password power on

    def power_off(self):
        cmd = ipmitool -I lanplus -H self._target -U self._username -P self.password power off 

    def power_cycle(self):
        cmd = ipmitool -I lanplus -H self._target -U self._username -P self.password power cycle

    def power_reset(self):
        cmd = ipmitool -I lanplus -H self._target -U self._username -P self.password power reset

    
    os.system(cmd) 
