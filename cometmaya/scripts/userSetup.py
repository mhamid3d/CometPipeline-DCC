from cometmaya.ui.base_shelf import BaseShelf
from pipeicon import icon_paths
from pipeicon.util import fullIconPath
from maya import mel
from shiboken2 import wrapInstance
from qtpy import QtWidgets, QtGui
import pymel.core as pmc
import maya.OpenMayaUI as omui
import maya.cmds as mc
import os

# Shelf script imports
from cometmaya.shelf_scripts.entity_picker import entityPickerRun
from cometmaya.shelf_scripts.publish_model import run_publish_model


mc.evalDeferred('initialize_maya()')
mc.evalDeferred('CometShelf()')


def initialize_maya():
    import mongorm
    from cometmaya.scripts import configure_scene_for_entity

    handler = mongorm.getHandler()
    filt = mongorm.getFilter()
    job, entity = os.getenv("SHOW"), os.getenv("SHOT")
    filt.search(handler['entity'], job=job, label=entity)
    entityObject = handler['entity'].one(filt)
    filt.clear()

    filt.search(handler['job'], label=job)
    jobObject = handler['job'].one(filt)
    filt.clear()

    configure_scene_for_entity(jobObject, entityObject)


class CometShelf(BaseShelf):
    def __init__(self, name='Comet'):
        BaseShelf.__init__(self, name)

    def build(self):

        shelfName = pmc.MelGlobals()['gShelfTopLevel'] + "|{}".format(self.name)
        swigObject = omui.MQtUtil.findLayout(shelfName)
        qtObject = wrapInstance(swigObject, QtWidgets.QWidget)
        layout = qtObject.layout()

        self.addButton(label='Set Entity', icon=fullIconPath(icon_paths.ICON_SHOT_LRG), command='entityPickerRun()')
        self.addSeparator()

        # disciplineButton = QtWidgets.QToolButton()
        # disciplineButton.setText("Lighting")
        # disciplineButton.setIcon(QtGui.QIcon(icon_paths.ICON_COMETPIPE_LRG))
        # disciplineButton.setFixedSize(64, 32)
        # layout.addWidget(disciplineButton)

        mc.shelfButton(width=64, height=37, image=fullIconPath(icon_paths.ICON_COMETPIPE_LRG), command='', label='Discipline', olb=self.labelBackground, olc=self.labelColor, parent=self.mainShelf)
        p = mc.popupMenu(b=1)

        mc.menuItem(p=p, command="", label="Comet", c="", i="")
        mc.menuItem(p=p, command="", label="Anim", c="", i="")
        mc.menuItem(p=p, command="", label="Layout", c="", i="")
        mc.menuItem(p=p, command="", label="Modeling", c="", i="")
        mc.menuItem(p=p, command="", label="Groom", c="", i="")
        mc.menuItem(p=p, command="", label="All", c="", i="")

        self.addSeparator()
        self.addButton(label='Publish Model', icon=fullIconPath(icon_paths.ICON_MODEL_PUBLISH_LRG), command='run_publish_model()')
