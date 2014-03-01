__doc__ = '''
wpactrl defines a single class, WPACtrl, that must be instantiated
with the pathname of a UNIX domain socket control interface of a
wpa_supplicant/hostapd daemon.

Once a WPACtrl object has been instantiated, it may call several
helper methods to interact with the wpa_supplicant/hostapd daemon.
If an error occurs, a wpactrl.error exception is raised.

The destructor of a WPACtrl instance closes the connection to the
control interface socket.

Recommendations for the use of wpa_supplicant/hostapd control
interface access in external programs are at:
    <http://w1.fi/wpa_supplicant/devel/ctrl_iface_page.html>
'''

import wpa_ctrl

version = lambda: (1, 0, 1)

class WPACtrl(object):

    def __init__(self, ctrl_iface_path):
        if not isinstance(ctrl_iface_path, basestring):
            raise error('failed to parse ctrl_iface_path string')

        self.ctrl_iface_path = ctrl_iface_path

        self.ctrl_iface = wpa_ctrl.wpa_ctrl_open(ctrl_iface_path)

        if not self.ctrl_iface:
            raise error('wpa_ctrl_open failed')

        self.attached = 0

    def close(self):
        if self.attached == 1:
            self.detach()

        wpa_ctrl.wpa_ctrl_close(self.ctrl_iface)

        print 'Closed'

    def __del__(self):
        self.close()

    def request(self, cmd):
        '''
        Send a command to wpa_supplicant/hostapd. Returns the command response
		in a string.
        '''

        try:
            data = wpa_ctrl.wpa_ctrl_request(self.ctrl_iface, cmd)
        except wpa_ctrl.socket.error:
            raise error('wpa_ctrl_request failed')

        if data == -2:
            raise error('wpa_ctrl_request timed out')

        return data

    def attach(self):
        '''
        Register as an event monitor for the control interface.
        '''
        if self.attached == 1:
            return

        try:
            ret = wpa_ctrl.wpa_ctrl_attach(self.ctrl_iface)
        except wpa_ctrl.socket.error:
            raise error('wpa_ctrl_attach failed')

        if ret == True:
            self.attached = 1
        elif ret == -2:
            raise error('wpa_ctrl_attach timed out')

    def detach(self):
        '''
        Unregister event monitor from the control interface.
        '''
        if self.attached == 0:
            return

        try:
            ret = wpa_ctrl.wpa_ctrl_detach(self.ctrl_iface)
        except wpa_ctrl.socket.error:
            raise error('wpa_ctrl_detach failed')

        if ret == True:
            self.attached = 0
        elif ret == -2:
            raise error('wpa_ctrl_attach timed out')

    def pending(self):
        '''
        Check if any events/messages are pending. Returns True if messages are pending,
		otherwise False.
        '''
        try:
            return wpa_ctrl.wpa_ctrl_pending(self.ctrl_iface)
        except wpa_ctrl.socket.error:
            raise error('wpa_ctrl_pending failed')

    def recv(self):
        '''
        Recieve a pending event/message from ctrl socket. Returns a message string.
        '''
        try:
            data = wpa_ctrl.wpa_ctrl_recv()
        except wpa_ctrl.socket.error:
            raise error('wpa_ctrl_recv failed')

    def scanresults(self):
        '''
        Return list of scan results. Each element of the scan result list is a string
		of properties for a single BSS. This method is specific to wpa_supplicant.
        '''

        bssids = []

        for cell in range(1000):
            ret = self.request('BSS %d' % cell)

            if 'bssid=' in ret:
                bssids.append(ret)
            else:
                break

        return bssids


class error(Exception): pass