from collections import defaultdict
from qtpy import QtWidgets, QtCore, QtGui
from pipeicon import icon_paths
import maya.cmds as mc
import os
import yaml

UNDEFINED_STRING = "META_UNDEFINED"
try:
    MATCONFIG_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), "materialTagConfig.yaml"))
except:
    MATCONFIG_FILE = "/home/mhamid/_dev/CometPipeline-DCC/cometmaya/shelf_scripts/materialTagConfig.yaml"


def createMat(matName):
    mat_name = "{}".format(matName)
    shd_name = "{}_SG".format(matName)
    shd = mc.shadingNode('lambert', name=mat_name, asShader=True)
    shdSG = mc.sets(name=shd_name, empty=True, renderable=True, noSurfaceShader=True)
    mc.connectAttr('{}.outColor'.format(mat_name), '{}.surfaceShader'.format(shd_name))

    return shdSG


class MaterialTagManager(QtWidgets.QDialog):
    def __init__(self):
        super(MaterialTagManager, self).__init__()
        self.resize(600, 700)

        self.mainLayout = QtWidgets.QVBoxLayout(self)
        self.setLayout(self.mainLayout)
        self.setWindowTitle("Material Tag Manager")

        self.mainGroupBox = QtWidgets.QGroupBox()
        self.searchBar = QtWidgets.QLineEdit()
        self.mainTree = QtWidgets.QTreeWidget()
        self.controlsGroupBox = QtWidgets.QGroupBox()
        self.reloadButton = QtWidgets.QToolButton()
        self.reloadButton.setText("Reload All")
        self.addTagButton = QtWidgets.QToolButton()
        self.addTagButton.setText("Add Tag")
        self.deleteTagButton = QtWidgets.QToolButton()
        self.deleteTagButton.setText("Delete Tag")
        self.changeColorButton = QtWidgets.QToolButton()
        self.changeColorButton.setText("Change Color")
        self.generateMaterialsButton = QtWidgets.QToolButton()
        self.generateMaterialsButton.setText("Generate Materials")
        self.assignToSelButton = QtWidgets.QToolButton()
        self.assignToSelButton.setText("Assign To Selection")
        self.closeButton = QtWidgets.QPushButton("Close")
        self.reloadButton.setIcon(QtGui.QIcon(icon_paths.ICON_RELOAD_LRG))
        self.addTagButton.setIcon(QtGui.QIcon(icon_paths.ICON_PLUS_LRG))
        self.deleteTagButton.setIcon(QtGui.QIcon(icon_paths.ICON_TRASH_LRG))
        self.changeColorButton.setIcon((QtGui.QIcon(icon_paths.ICON_SLIDERS_LRG)))
        self.generateMaterialsButton.setIcon(QtGui.QIcon(icon_paths.ICON_CRAFT_LRG))
        self.assignToSelButton.setIcon((QtGui.QIcon(icon_paths.ICON_ARROWRIGHT_LRG)))
        self.onlySceneMatsCheck = QtWidgets.QCheckBox("Show Only Scene Materials")

        self.mainGroupLayout = QtWidgets.QVBoxLayout()
        self.editorLayout = QtWidgets.QHBoxLayout()
        self.controlsGroupLayout = QtWidgets.QVBoxLayout()
        self.bottomSettingsLayout = QtWidgets.QHBoxLayout()

        self.searchBar.setMinimumHeight(32)
        self.searchBar.setPlaceholderText("Search...")
        self.controlsGroupLayout.setAlignment(QtCore.Qt.AlignTop)
        self.controlsGroupLayout.setContentsMargins(0, 0, 0, 0)
        self.mainTree.setHeaderLabels(['Material Tag', 'Display Color'])
        self.onlySceneMatsCheck.setChecked(True)

        self.mainGroupBox.setLayout(self.mainGroupLayout)
        self.mainGroupLayout.addWidget(self.searchBar)
        self.mainGroupLayout.addWidget(self.onlySceneMatsCheck)
        self.mainGroupLayout.addLayout(self.editorLayout)
        self.editorLayout.addWidget(self.mainTree)
        self.editorLayout.addWidget(self.controlsGroupBox)
        self.controlsGroupBox.setLayout(self.controlsGroupLayout)

        for button in [self.reloadButton, self.addTagButton, self.deleteTagButton, self.generateMaterialsButton,
                       self.changeColorButton, self.assignToSelButton]:
            button.setFixedSize(128, 64)
            button.setToolButtonStyle(QtCore.Qt.ToolButtonTextUnderIcon)
            button.setCursor(QtCore.Qt.PointingHandCursor)
            button.setStyleSheet("""
                QToolButton{
                    background: #3e3e3e;
                    border-radius: 5px;
                    padding: 8px;
                }
                QToolButton:hover{
                    background: #5e5e5e;
                }
                QToolButton:pressed{
                    background: #2e2e2e;
                }
            """)
            self.controlsGroupLayout.addWidget(button)

        self.mainGroupLayout.addLayout(self.bottomSettingsLayout)
        self.mainLayout.addWidget(self.mainGroupBox)
        self.mainLayout.addWidget(self.closeButton, alignment=QtCore.Qt.AlignRight)

        self.mainTree.setIconSize(QtCore.QSize(18, 18))
        self.mainTree.setExpandsOnDoubleClick(False)
        self.mainTree.setStyleSheet("""
            QTreeWidget{
                background: #2e2e2e;
                font: bold;
                outline: 0;
                show-decoration-selected: 0;
            }
            QTreeWidget:item{
                background: #3e3e3e;
                margin: 1px;
                padding: 5px;
            }
            QTreeWidget:item:hover{
                background: #4e4e4e;
            }
            QTreeWidget:item:selected{
                background: #1464A0;
            }
        """)

        self.closeButton.clicked.connect(self.close)
        self.reloadButton.clicked.connect(self.populateTree)
        self.onlySceneMatsCheck.stateChanged.connect(self.handle_onlySceneMatsChanged)
        self.mainTree.itemDoubleClicked.connect(self.handle_itemDoubleClicked)
        self.assignToSelButton.clicked.connect(self.handle_assignToSelection)
        self.addTagButton.clicked.connect(self.handle_addTag)
        self.deleteTagButton.clicked.connect(self.handle_deleteTag)
        self.changeColorButton.clicked.connect(self.handle_changeColor)
        self.searchBar.textChanged.connect(self.handle_searchChanged)
        self.generateMaterialsButton.clicked.connect(self.handle_generateMaterials)

        self.populateTree()

    def handle_searchChanged(self):
        currentText = self.searchBar.text()
        state = self.onlySceneMatsCheck.isChecked()

        allItems = [self.mainTree.topLevelItem(i) for i in range(self.mainTree.topLevelItemCount())]
        for item in allItems:
            for c in range(item.childCount()):
                allItems.append(item.child(c))

        for item in allItems:
            item.setHidden(True)
            if state and not item.parent() and item.childCount() == 0:
                continue
            if currentText in item.text(0):
                item.setHidden(False)
                if item.parent():
                    item.parent().setHidden(False)

    def handle_assignToSelection(self):
        currentItem = self.mainTree.currentItem()
        if not currentItem:
            return
        elif currentItem.text(0) == "Unassigned Objects":
            return
        elif currentItem.parent():
            return
        else:
            materialTag = currentItem.text(0)

        mayaSel = mc.ls(sl=True, dag=True, type=['mesh', 'nurbsSurface'])
        if not mayaSel:
            return
        for shape in mayaSel:
            if not mc.attributeQuery("materialTag", node=shape, exists=True):
                mc.addAttr(shape, ln="materialTag", dt="string")

            mc.setAttr(shape + ".materialTag", materialTag, type="string")

        self.populateTree()

    def handle_itemDoubleClicked(self, item):
        if item.parent():
            mc.select(str(item.text(0)))
        else:
            mc.select(clear=True)
            for c in range(item.childCount()):
                child = item.child(c)
                mc.select(str(child.text(0)), add=True)

    def handle_onlySceneMatsChanged(self):
        state = self.onlySceneMatsCheck.isChecked()

        for i in range(self.mainTree.topLevelItemCount()):
            item = self.mainTree.topLevelItem(i)
            item.setHidden(False)
            if state:
                if item.childCount() == 0:
                    item.setHidden(True)

    def handle_addTag(self):
        diag = QtWidgets.QDialog(parent=self)
        diag.setWindowTitle("Add Material Tag")
        layout = QtWidgets.QVBoxLayout()
        diag.setLayout(layout)
        form = QtWidgets.QFormLayout()
        layout.addLayout(form)
        buttonBox = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Apply|QtWidgets.QDialogButtonBox.Cancel)
        layout.addWidget(buttonBox)
        buttonBox.button(QtWidgets.QDialogButtonBox.Apply).clicked.connect(diag.accept)
        buttonBox.button(QtWidgets.QDialogButtonBox.Cancel).clicked.connect(diag.reject)

        materialTagLE = QtWidgets.QLineEdit()
        materialTagLE.setPlaceholderText("Material Tag Name...")
        colorPushButton = QtWidgets.QPushButton()
        colorPushButton.setFixedHeight(32)
        colorPushButton.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        colorPushButton.setCursor(QtCore.Qt.PointingHandCursor)
        colorPushButton.setStyleSheet("""
            QPushButton{
                background: white;            
            }
        """)
        colorPushButton.color = [1.0, 1.0, 1.0]
        colorDialog = QtWidgets.QColorDialog()
        colorDialog.setCurrentColor(QtGui.QColor("white"))
        colorDialog.accepted.connect(lambda: setattr(colorPushButton, "color", colorDialog.currentColor().getRgbF()))
        colorDialog.accepted.connect(lambda: colorPushButton.setStyleSheet("background: rgb(%s, %s, %s)" %
                                                                         (
                                                                             colorDialog.currentColor().red(),
                                                                             colorDialog.currentColor().green(),
                                                                             colorDialog.currentColor().blue()
                                                                         )))
        colorPushButton.clicked.connect(colorDialog.exec_)

        form.addRow("Material Tag Name: ", materialTagLE)
        form.addRow("Display Color: ", colorPushButton)

        def applyClicked(*args, **kwargs):
            if materialTagLE.text() in self.getMatPresetData():
                msgBox = QtWidgets.QMessageBox(parent=diag)
                msgBox.setWindowTitle("Error")
                msgBox.setText('The material tag "{}" already exists in the config file! Please use a different name.'.format(materialTagLE.text()))
                msgBox.exec_()
            else:
                return QtWidgets.QDialog.accept(diag)

        diag.accept = applyClicked

        result = diag.exec_()

        if not result:
            return

        materialTag = materialTagLE.text()
        displayColor = list(colorPushButton.color)
        displayColor.pop()
        displayColor = [round(x, 4) for x in displayColor]

        with open(MATCONFIG_FILE) as f:
            data = yaml.load(f, Loader=yaml.FullLoader)

        with open(MATCONFIG_FILE, "w") as f:
            data['presets'][materialTag] = {'color': displayColor}
            yaml.dump(data, f)

        self.populateTree()

    def handle_deleteTag(self):
        currentItem = self.mainTree.currentItem()
        if not currentItem:
            return
        elif currentItem.text(0) == "Unassigned Objects":
            return
        elif currentItem.parent():
            return
        else:
            materialTag = currentItem.text(0)

        msgBox = QtWidgets.QMessageBox()
        msgBox.setIcon(QtWidgets.QMessageBox.Warning)
        msgBox.setText("Are you sure you want to delete {}? This is UNDOABLE!".format(materialTag))
        msgBox.setStandardButtons(QtWidgets.QMessageBox.Yes|QtWidgets.QMessageBox.No)
        msgBox.setDefaultButton(msgBox.button(QtWidgets.QMessageBox.No))
        result = msgBox.exec_()

        if result == QtWidgets.QMessageBox.No:
            return

        with open(MATCONFIG_FILE) as f:
            data = yaml.load(f, Loader=yaml.FullLoader)

        with open(MATCONFIG_FILE, "w") as f:
            data['presets'].pop(materialTag, None)
            yaml.dump(data, f)

        if currentItem.childCount() > 0:
            for c in range(currentItem.childCount()):
                child = currentItem.child(c)
                if mc.getAttr(str(child.text(0)) + ".materialTag") == materialTag:
                    mc.setAttr(str(child.text(0)) + ".materialTag", "", type="string")

        self.populateTree()

    def handle_changeColor(self):
        currentItem = self.mainTree.currentItem()
        if not currentItem:
            return
        elif currentItem.text(0) == "Unassigned Objects":
            return
        elif currentItem.parent():
            return
        else:
            materialTag = currentItem.text(0)

        colorDialog = QtWidgets.QColorDialog()
        color = [int(x*255) for x in self.getMatPresetData()[materialTag]['color']]
        colorDialog.setCurrentColor(QtGui.QColor(color[0], color[1], color[2]))
        result = colorDialog.exec_()

        if not result:
            return

        newColor = list(colorDialog.currentColor().getRgbF())
        newColor.pop()
        newColor = [round(x, 4) for x in newColor]

        with open(MATCONFIG_FILE) as f:
            data = yaml.load(f, Loader=yaml.FullLoader)

        with open(MATCONFIG_FILE, "w") as f:
            data['presets'][materialTag]['color'] = newColor
            yaml.dump(data, f)

        self.populateTree()

    def handle_generateMaterials(self):
        allShapes = mc.ls(dag=True, type=['mesh', 'nurbsSurface'])

        materialTagDict = defaultdict(list)
        for shape in allShapes:
            if mc.attributeQuery("materialTag", node=shape, exists=True) and str(mc.getAttr(shape + ".materialTag")):
                materialTag = str(mc.getAttr(shape + ".materialTag"))
                materialTagDict[materialTag].append(shape)
            else:
                materialTagDict[UNDEFINED_STRING].append(shape)

        for mTag, shapes in materialTagDict.items():
            if mTag == UNDEFINED_STRING:
                material = "initialShadingGroup"
            else:
                if mc.ls(mTag + "_SG", type=['shadingEngine']):
                    material = mTag + "_SG"
                else:
                    material = createMat(mTag)

                try:
                    color = self.getMatPresetData()[mTag]['color']
                except KeyError:
                    color = [0.0, 1.0, 0.0]

                mat = mc.listConnections(material + ".surfaceShader")[0]
                mc.setAttr(mat + ".color", *color, type="double3")

            for shape in shapes:
                mc.sets(shape, e=True, forceElement=material)

    def getMatPresetData(self):
        with open(MATCONFIG_FILE) as f:
            data = yaml.load(f, Loader=yaml.FullLoader)['presets']

        return data

    def populateTree(self):

        self.mainTree.clear()

        materialData = self.getMatPresetData()
        allShapes = mc.ls(dag=True, type=['mesh', 'nurbsSurface'])
        if not allShapes:
            return

        materialTagDict = defaultdict(list)
        for shape in allShapes:
            attrExists = mc.attributeQuery("materialTag", node=shape, exists=True)
            if attrExists and mc.getAttr(shape + ".materialTag"):
                materialTagDict[mc.getAttr(shape + ".materialTag")].append(shape)
            else:
                materialTagDict[UNDEFINED_STRING].append(shape)

        for tag, shapes in materialTagDict.items():
            item = QtWidgets.QTreeWidgetItem(self.mainTree)
            if tag == UNDEFINED_STRING:
                item.setText(0, "Unassigned Objects")
                item.setIcon(0, QtGui.QIcon(icon_paths.ICON_XRED_LRG))
            else:
                item.setText(0, tag)
                item.setIcon(0, QtGui.QIcon(icon_paths.ICON_CHECKGREEN_LRG))

            for shape in sorted(shapes):
                shpItem = QtWidgets.QTreeWidgetItem(item)
                shpItem.setText(0, str(shape))

        for tag, data in materialData.items():
            if not tag in materialTagDict:
                item = QtWidgets.QTreeWidgetItem(self.mainTree)
                item.setText(0, tag)
                item.setIcon(0, QtGui.QIcon(icon_paths.ICON_SHADER_LRG))
                if self.onlySceneMatsCheck.isChecked():
                    item.setHidden(True)

        for i in range(self.mainTree.topLevelItemCount()):
            item = self.mainTree.topLevelItem(i)
            if item.text(0) in materialData:
                colorWidget = QtWidgets.QFrame()
                color = [int(x*255) for x in materialData[item.text(0)]['color']]
                colorWidget.setStyleSheet("background: rgb(%s, %s, %s)" % (color[0], color[1], color[2]))
                self.mainTree.setItemWidget(item, 1, colorWidget)

        self.mainTree.setColumnWidth(0, 300)
        self.handle_searchChanged()


win = MaterialTagManager()
win.show()