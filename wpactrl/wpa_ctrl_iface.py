import os

try:
    from gevent import (socket, select)
except ImportError:
    import socket, select

''' # Incompatibilities

Generally, socker errors are handled in a more pythonic manor.
While the original wpa_ctrl.c implementation deals with a lot of error
handling and returns different error codes (as it surely should, since it's
a C library), this implementation simply does not handle socket exceptions.

## wpa_ctrl_request()
* Does not use cmd_len, since there's really no need for this in the python implementation.
* Does not take a reply buffer pointer, since we'll just receive into a new string.
  It does however use reply_len as size hinting for recv.
* The msg_cb only takes a msg argument, not len.

## wpa_ctrl_recv()
* Does not take a reply buffer pointer, for the same reason mentioned for wpa_ctrl_request()
'''

class wpa_ctrl(object):
    s = local = dest = None

def wpa_ctrl_open(ctrl_path):
    '''
    Open a control interface to wpa_supplicant/hostapd.
    '''

    ctrl = wpa_ctrl()

    try:
        ctrl.s = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM, 0)
    except socket.error:
        return None

    ctrl.local = '/tmp/wpa_ctrl_%d-%d' % (os.getpid(), wpa_ctrl_open.counter)
    wpa_ctrl_open.counter += 1

    try:
        ctrl.s.bind(ctrl.local)
    except socket.error:
        ctrl.s.close()

        return None

    try:
        ctrl.s.connect(ctrl_path)
    except socket.error:
        wpa_ctrl_close(ctrl)

        return None

    return ctrl

wpa_ctrl_open.counter = 0

def wpa_ctrl_close(ctrl):
    '''
    Close a control interface to wpa_supplicant/hostapd.
    '''

    os.unlink(ctrl.local)
    ctrl.s.close()

def wpa_ctrl_request(ctrl, cmd, msg_cb=None, reply_len=4096):
    '''
    Send a command to wpa_supplicant/hostapd.
    '''

    ctrl.s.send(cmd)

    while True:
        rlist, wlist, xlist = select.select([ctrl.s], [], [], 2)

        if rlist and (ctrl.s in rlist):
            data = ctrl.s.recv(reply_len)

            if data and data[0] == '<':
                if msg_cb:
                    msg_cb(data)

                continue
            else:
                return data
        else:
            return -2 # Timed out


def wpa_ctrl_attach_helper(ctrl, attach):
    ret = wpa_ctrl_request(ctrl, 'ATTACH' if attach else 'DETACH')

    if isinstance(ret, basestring):
        return ret == 'OK\n'
    else:
        return ret

def wpa_ctrl_attach(ctrl):
    '''
    Register as an event monitor for the control interface.
    '''
    return wpa_ctrl_attach_helper(ctrl, True)

def wpa_ctrl_detach(ctrl):
    '''
    Unregister event monitor from the control interface.
    '''
    return wpa_ctrl_attach_helper(ctrl, False)

def wpa_ctrl_recv(ctrl, reply_len=4096):
    '''
    Receive a pending control interface message.
    '''
    return ctrl.s.recv(reply_len)

def wpa_ctrl_pending(ctrl):
    '''
    Check whether there are pending event messages.
    '''

    rlist, wlist, xlist = select.select([ctrl.s], [], [], 0)

    return ctrl.s in rlist

def wpa_ctrl_get_fd(ctrl):
    '''
    Get file descriptor used by the control interface.
    '''

    return ctrl.s.fileno()
