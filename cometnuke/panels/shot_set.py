from qtpy import QtWidgets, QtGui, QtCore
from cometqt.widgets.ui_entity_combobox import EntityComboBox
from cometqt.util import FormVBoxLayout
import os
import nuke


class ShotSetWidget(QtWidgets.QWidget):
    def __init__(self):
        super(ShotSetWidget, self).__init__()
        self.mainLayout = QtWidgets.QVBoxLayout()
        self.mainLayout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.mainLayout)
        self.formLayout = FormVBoxLayout()
        self.mainLayout.addLayout(self.formLayout)
        self.entityComboBox = EntityComboBox(parent=self)
        self.formLayout.addRow(label="Set Shot", widget=self.entityComboBox)

        if self.entityComboBox.entityMenu.entityViewer.entityType == self.entityComboBox.entityMenu.entityViewer.TYPE_ASSETS:
            self.entityComboBox.setSelectedEntity(None)
            self.entityComboBox.entityMenu.entityViewer.setEntityType(self.entityComboBox.entityMenu.entityViewer.TYPE_PRODUCTION)

        self.entityComboBox.entityMenu.entityViewer.assetsButton.setDisabled(True)
        self.frameRangeLabel = QtWidgets.QLabel("()-()")
        self.formLayout.addRow(label="Frame Range", widget=self.frameRangeLabel)

        self.setRangeButton = QtWidgets.QPushButton("Set Script Range")
        self.formLayout.addRow(label="Set Script Range", widget=self.setRangeButton)

        self.updateFrameRange()

        self.setRangeButton.clicked.connect(self.setScriptRange)
        self.entityComboBox.entityChanged.connect(self.entityChanged)

    def entityChanged(self):
        entity = self.entityComboBox.getSelectedEntity()
        job = self.entityComboBox.getSelectedJob()

        if not entity or not job:
            return None

        os.environ['SHOW'] = job.get("label")
        os.environ['SHOT'] = entity.get("label")

        self.updateFrameRange()

    def getShotFrameRange(self):
        entity = self.entityComboBox.getSelectedEntity()
        if not entity:
            return [1001, 1101]
        frameRange = entity.get("framerange")
        if not frameRange:
            return [1001, 1101]

        return frameRange

    def updateFrameRange(self):
        fr = self.getShotFrameRange()
        self.frameRangeLabel.setText("{} - {}".format(fr[0], fr[1]))
        self.setScriptRange()

    def setScriptRange(self):
        fr = self.getShotFrameRange()
        nuke.knobDefault('Root.first_frame', str(fr[0]))
        nuke.knobDefault('Root.last_frame', str(fr[1]))
        nuke.frame(fr[0])
        nuke.knob('root.first_frame', str(fr[0]))
        nuke.knob('root.last_frame', str(fr[1]))