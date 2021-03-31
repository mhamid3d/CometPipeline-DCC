import maya.OpenMayaUI as omui
import shiboken2
from qtpy import QtWidgets


def getMayaWindow():
    ptr = omui.MQtUtil.mainWindow()
    if ptr is not None:
        return shiboken2.wrapInstance(ptr, QtWidgets.QWidget)