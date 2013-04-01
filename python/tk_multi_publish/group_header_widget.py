"""
Copyright (c) 2013 Shotgun Software, Inc
----------------------------------------------------
"""

import tank
from tank.platform.qt import QtCore, QtGui

class GroupHeaderWidget(QtGui.QWidget):
    """
    """
    def __init__(self, parent=None):
        """
        Construction
        """
        QtGui.QWidget.__init__(self, parent)
    
        # set up the UI
        from .ui.group_header_ui import Ui_Form
        self._ui = Ui_Form() 
        self._ui.setupUi(self)