#!/usr/bin/python3.5
# CDDL HEADER START
#
# The contents of this file are subject to the terms of the
# Common Development and Distribution License (the "License").
# You may not use this file except in compliance with the License.
#
# You can obtain a copy of the license at usr/src/OPENSOLARIS.LICENSE
# or http://www.opensolaris.org/os/licensing.
# See the License for the specific language governing permissions
# and limitations under the License.
#
# When distributing Covered Code, include this CDDL HEADER in each
# file and include the License file at usr/src/OPENSOLARIS.LICENSE.
# If applicable, add the following below this CDDL HEADER, with the
# fields enclosed by brackets "[]" replaced with your own identifying
# information: Portions Copyright [yyyy] [name of copyright owner]
#
# CDDL HEADER END
#

import os
import subprocess
import sys
import syslog
import math
from gi.repository import Gio, GLib

def run_command(command, raise_on_try=True):
    """
    Wrapper function around subprocess.Popen
    Returns a tuple of standard out and stander error.
    Throws a RunTimeError if the command failed to execute or
    if the command returns a non-zero exit status.
    """
    try:
        p = subprocess.Popen(command,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE,
                             close_fds=True,
                             universal_newlines=True)
        outdata,errdata = p.communicate()
        err = p.wait()
    except OSError as message:
        raise RuntimeError("%s subprocess error:\n %s" % \
                            (command, str(message)))
    if err != 0 and raise_on_try:
        raise RuntimeError('%s failed with exit code %d\n%s' % \
                            (str(command), err, errdata))
    return outdata,errdata

def debug(message, verbose):
    """
    Prints message out to standard error and syslog if
    verbose = True.
    Note that the caller needs to first establish a syslog
    context using syslog.openlog()
    """
    if verbose:
        syslog.syslog(syslog.LOG_NOTICE, message + '\n')
        sys.stderr.write(message + '\n')

def log_error(loglevel, message):
    """
    Trivial syslog wrapper that also outputs to stderr
    Requires caller to have first opened a syslog session
    using syslog.openlog()
    """
    syslog.syslog(loglevel, message + '\n')
    sys.stderr.write(message + '\n')

def get_filesystem_capacity(path):
    """Returns filesystem space usage of path as an integer percentage of
       the entire capacity of path.
    """
    if not os.path.exists(path):
        raise ValueError("%s is a non-existent path" % path)
    f = os.statvfs(path)

    unavailBlocks = f.f_blocks - f.f_bavail
    capacity = int(math.ceil(100 * (unavailBlocks / float(f.f_blocks))))

    return capacity

def get_available_size(path):
    """Returns the available space in bytes under path"""
    if not os.path.exists(path):
        raise ValueError("%s is a non-existent path" % path)
    f = os.statvfs(path)
    free = int(f.f_bavail * f.f_frsize)
    
    return free

def get_used_size(path):
    """Returns the used space in bytes of fileystem associated
       with path"""
    if not os.path.exists(path):
        raise ValueError("%s is a non-existent path" % path)
    f = os.statvfs(path)

    unavailBlocks = f.f_blocks - f.f_bavail
    used = int(unavailBlocks * f.f_frsize)

    return used

def get_total_size(path):
    """Returns the total storage space in bytes of fileystem
       associated with path"""
    if not os.path.exists(path):
        raise ValueError("%s is a non-existent path" % path)
    f = os.statvfs(path)
    total = int(f.f_blocks * f.f_frsize)

    return total

def path_to_volume(path):
    """
       Tries to map a given path name to a gio Volume and
       returns the gio.Volume object the enclosing
       volume.
       If it fails to find an enclosing volume it returns
       None
    """
    gFile = Gio.File.new_for_path(path)
    try:
        mount = gFile.find_enclosing_mount()
    except GLib.Error:
        return None
    else:
        if mount != None:
            volume = mount.get_volume()
            return volume
    return None
