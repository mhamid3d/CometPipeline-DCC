from PyQt5 import QtWidgets, QtCore, QtGui
from cometqt.widgets.ui_entity_viewer import EntityPickerDialog
from Katana import UI4


class ModuleItem(QtWidgets.QTreeWidgetItem):
    def __init__(self, module, tree):
        super(ModuleItem, self).__init__(tree)
        self.tree = tree
        self.setText(0, module)


class ModuleTree(QtWidgets.QTreeWidget):
    def __init__(self):
        super(ModuleTree, self).__init__()
        self.setSelectionMode(QtWidgets.QTreeView.ExtendedSelection)
        self.setHeaderLabels(['Module', 'Version'])
        self.setRootIsDecorated(False)


class SVEN(UI4.Tabs.BaseTab):
    def __init__(self, parent):
        super(SVEN, self).__init__(parent)
        self.mainLayout = QtWidgets.QVBoxLayout(self)
        self.mainLayout.setContentsMargins(9, 9, 9, 9)
        self.setLayout(self.mainLayout)

        self.setup_ui()

    def setup_ui(self):
        self.create_widgets()
        self.edit_widgets()
        self.build_layouts()
        self.setup_styles()
        self.handle_signals()

    def create_widgets(self):
        self.topButtonsLayout = QtWidgets.QHBoxLayout()
        self.modulesPageLayout = QtWidgets.QVBoxLayout()

        self.refreshButton = QtWidgets.QPushButton("Refresh SVEN")
        self.buildButton = QtWidgets.QPushButton("Build")
        self.tabWidget = QtWidgets.QTabWidget()
        self.modulesPage = QtWidgets.QWidget()
        self.renderPassPage = QtWidgets.QWidget()
        self.moduleTree = ModuleTree()

    def edit_widgets(self):
        self.mainLayout.setAlignment(QtCore.Qt.AlignTop)

        self.refreshButton.setFixedHeight(32)
        self.buildButton.setFixedHeight(32)

        self.tabWidget.addTab(self.modulesPage, "Module Manager")
        self.tabWidget.addTab(self.renderPassPage, "Render Passes")

    def build_layouts(self):
        self.mainLayout.addLayout(self.topButtonsLayout)
        self.topButtonsLayout.addWidget(self.refreshButton)
        self.topButtonsLayout.addWidget(self.buildButton)
        self.mainLayout.addWidget(self.tabWidget)

        self.modulesPage.setLayout(self.modulesPageLayout)
        self.modulesPageLayout.addWidget(self.moduleTree)

    def setup_styles(self):
        self.setStyleSheet("*{outline: 0;}")
        self.moduleTree.setStyleSheet("""
            QTreeView{
                outline: 0;
            }
            QTreeView:item{
                padding: 15px;
            }
        """)

    def handle_signals(self):
        self.buildButton.clicked.connect(self.openShotPicker)

    def openShotPicker(self):
        shotPicker = EntityPickerDialog()
        shotPicker.entityViewer.entityTree.setSelectionMode(QtWidgets.QTreeView.ExtendedSelection)
        shotPicker.resize(450, 600)
        result = shotPicker.exec_()

        if result == QtWidgets.QDialog.Rejected:
            return

        selection = shotPicker.getSelection()


PluginRegistry = [
    ('KatanaPanel', 2.0, 'SVEN', SVEN),
]