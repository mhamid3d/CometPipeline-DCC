from PyQt5 import QtWidgets, QtGui, QtCore
from Katana import UI4
from ui_extra import toggle_button as togg
import ScriptActions as SA


def h_line():
    frame = QtWidgets.QFrame()
    frame.setFrameShape(QtWidgets.QFrame.HLine)
    frame.setStyleSheet("""
        QFrame{
            color: #4e4e4e;
        }
    """)
    return frame


class AovItem(QtWidgets.QTreeWidgetItem):
    def __init__(self, name=None, tree=None, node=None):
        super(AovItem, self).__init__(tree)
        self.tree = tree
        self._name = name
        self._node = node
        self.setup_ui()

    @property
    def state(self):
        activeAOVs = [x.getValue(0) for x in self._node.getParameter('activeAOVs').getChildren()]
        return self._name in activeAOVs

    def setup_ui(self):
        self._widget = QtWidgets.QWidget(self.tree)
        self._layout = QtWidgets.QHBoxLayout()
        self._widget.setLayout(self._layout)
        self.toggle = togg.ToggleButton(colorActive=togg.ORANGE, height=13, roundedCorner=False)
        self.toggle.state = self.state
        self._layout.addWidget(self.toggle)
        self.label = QtWidgets.QLabel(self._name)
        self._layout.addWidget(self.label)

        self.toggle.clicked.connect(self.item_toggled)

        self.tree.setItemWidget(self, 0, self._widget)

    def isCustom(self):
        aovNamesList = [x.keys()[0] for x in SA.aovList]
        return not self._name not in aovNamesList

    def item_toggled(self):
        state = self.toggle.state
        sel = self.tree.selectedItems()
        operation = self._node.getParameter("operation").getValue(0)

        if not sel or self not in sel:
            if state:
                self._node.addAov(self._name)
            else:
                self._node.removeAov(self._name)
        else:
            for aov in sel:
                if state:
                    if not aov.nodeExists():
                        aov._node.addAov(aov._name)
                else:
                    aov._node.removeAov(aov._name)
                if aov is not self:
                    aov.toggle.state = state

        self.tree.refreshActiveAovs()

    def nodeExists(self):
        for node in self._node.getChildren():
            param = node.getParameter("aov")
            if param and param.getValue(0) == self._name:
                return True

        return False


class AovTree(QtWidgets.QTreeWidget):
    def __init__(self, node=None):
        super(AovTree, self).__init__()
        self.node = node
        self.setSelectionMode(QtWidgets.QTreeView.ExtendedSelection)
        self.setColumnCount(1)
        self.setHeaderHidden(True)
        self.itemDoubleClicked.connect(self.handle_doubleClick)
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.contextMenu)

    def handle_doubleClick(self, *args, **kwargs):
        item = args[0]
        item.toggle._doToggle()

    def contextMenu(self, event):
        self._menu = QtWidgets.QMenu()
        delete_action = self._menu.addAction("Delete AOV")
        sel = self.selectedItems()

        filteredSel = [x for x in sel if not x.isCustom()]
        if len(filteredSel) is 0:
            delete_action.setEnabled(False)

        main_action = self._menu.exec_(self.mapToGlobal(event))

        if main_action:
            if main_action == delete_action:
                for item in filteredSel:
                    self.takeTopLevelItem(self.indexOfTopLevelItem(item))
                    self.node.removeAov(item._name)
                    self.refreshActiveAovs()

    def refreshActiveAovs(self):

        for child in self.node.getParameter('activeAOVs').getChildren():
            self.node.getParameter('activeAOVs').deleteChild(child)

        activeList = []
        for group in self.node.getChildren():
            param = group.getParameter('aov')
            if param:
                activeList.append(param.getValue(0))

        for idx, active in enumerate(activeList):
            self.node.getParameter('activeAOVs').createChildString('i{}'.format(idx), active)


class SearchableListWidget(QtWidgets.QWidget):
    def __init__(self, label="", node=None, parent=None):
        super(SearchableListWidget, self).__init__(parent)

        self.node = node
        self._label = label
        self.mainLayout = QtWidgets.QVBoxLayout(self)
        self.setLayout(self.mainLayout)

        self.searchLayout = QtWidgets.QHBoxLayout()
        self.addCustomButton = QtWidgets.QPushButton("Add Custom")
        self.hideDisabledCheck = QtWidgets.QCheckBox("Hide Disabled")

        self.searchBar = QtWidgets.QLineEdit()
        self.searchBar.setPlaceholderText("Search...")
        self.title = QtWidgets.QLabel(self._label)
        self.title.setAlignment(QtCore.Qt.AlignLeft)
        self.title.setIndent(0)

        self.list = AovTree(node=self.node)

        self.hideDisabledCheck.stateChanged.connect(self.tree_manip)
        self.searchBar.textChanged.connect(self.tree_manip)
        self.addCustomButton.clicked.connect(self.addCustomAov)

        self.hideDisabledCheck.setChecked(self.node.getParameter('hideDisabled').getValue(0))

        SEARCH_HEIGHT = 32

        self.searchBar.setFixedHeight(SEARCH_HEIGHT)
        self.hideDisabledCheck.setFixedHeight(SEARCH_HEIGHT)
        self.addCustomButton.setFixedHeight(SEARCH_HEIGHT)

        self.list.setStyleSheet("""
            QTreeView{
                background: #1e1e1e;
                color: #D9D9D9;
                border: 0px;
                selection-background-color: transparent;
            }
            QTreeView:item{
                background-color: #2e2e2e;
                margin: 1px 0px 1px 0px;
                padding: 4px;
                border: 1px solid #4e4e4e;
                border-right: 0px;
            }
            QTreeView::item:hover{
                background-color: #807153;
                }
            QTreeView::item:selected{
                background-color: #6e6e6e;
            }
            QTreeView::branch:hover{
                background: #2e2e2e;
            }
            QHeaderView::section{
                background-color: #3e3e3e;
                color: white;
            }
            QScrollBar:vertical{
                background: #1e1e1e;
                width: 15px;
                padding: 1px;
                margin: 0;
            }
            QScrollBar:horizontal{
                background: #1e1e1e;
                height: 15px;
                padding: 1px;
                margin: 0;
            }
            QScrollBar::handle:vertical,
            QScrollBar::handle:horizontal{
                background: #3e3e3e;
            }
            QScrollBar::handle:vertical:hover,
            QScrollBar::handle:horizontal:hover{
                background: #5e5e5e;
            }
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical,
            QScrollBar::add-page:vertical,
            QScrollBar::sub-page:vertical{
                height: 0px;
            }
            QScrollBar::add-line:horizontal,
            QScrollBar::sub-line:horizontal,
            QScrollBar::add-page:horizontal,
            QScrollBar::sub-page:horizontal{
                width: 0px;
            }
        """)

        self.mainLayout.addWidget(self.title)
        self.mainLayout.addLayout(self.searchLayout)
        self.searchLayout.addWidget(self.searchBar)
        self.searchLayout.addWidget(self.addCustomButton)
        self.mainLayout.addWidget(self.list)
        self.mainLayout.addWidget(self.hideDisabledCheck)
        self.mainLayout.addWidget(h_line())

    def tree_manip(self):
        hideDisabled = self.hideDisabledCheck.isChecked()
        searchText = self.searchBar.text().upper()

        self.node.getParameter('hideDisabled').setValue(1 if hideDisabled else 0, 0)

        for i in range(self.list.topLevelItemCount()):
            aovItem = self.list.topLevelItem(i)
            aovName = aovItem._name.upper()
            aovItem.setHidden(True)

            if hideDisabled and not aovItem.toggle.state:
                continue
            elif searchText not in aovName:
                continue
            else:
                aovItem.setHidden(False)

    def addCustomAov(self):
        diag = QtWidgets.QDialog()
        diag.setWindowTitle("New AOV")
        lyt = QtWidgets.QVBoxLayout()
        diag.setLayout(lyt)
        aovNameLabel = QtWidgets.QLabel("AOV Name")
        aovLineEdit = QtWidgets.QLineEdit()
        btnBox = QtWidgets.QDialogButtonBox()
        createButton = QtWidgets.QPushButton("Create")
        cancelButton = QtWidgets.QPushButton("Cancel")
        btnBox.addButton(createButton, QtWidgets.QDialogButtonBox.AcceptRole)
        btnBox.addButton(cancelButton, QtWidgets.QDialogButtonBox.RejectRole)

        btnBox.accepted.connect(diag.accept)
        btnBox.rejected.connect(diag.reject)

        lyt.addWidget(aovNameLabel)
        lyt.addWidget(aovLineEdit)
        lyt.addWidget(btnBox)

        value = diag.exec_()

        if value == QtWidgets.QDialog.Accepted:
            newAovName = str(aovLineEdit.text())
            node = self.parent().node
            aovGroup = node.addAov(newAovName)

            self.list.refreshActiveAovs()

            for aov in self.parent().populate():
                if aov._name == newAovName:
                    self.list.setCurrentItem(aov)
                    break


class ArnoldAOVsEditor(QtWidgets.QWidget):
    def __init__(self, parent, node):
        if node:
            node.upgrade()

        self.node = node
        super(ArnoldAOVsEditor, self).__init__(parent)

        self.mainLayout = QtWidgets.QVBoxLayout(self)
        self.setLayout(self.mainLayout)

        self.setup_ui()

    def setup_ui(self):
        self.create_widgets()
        self.edit_widgets()
        self.build_layouts()
        self.setup_styles()
        self.handle_signals()
        self.populate()

    def create_widgets(self):
        # Layouts
        self.listsLayout = QtWidgets.QHBoxLayout()

        # Widgets
        self.aovListWidget = SearchableListWidget(label="AOVs", node=self.node, parent=self)
        factory = UI4.FormMaster.KatanaFactory.ParameterWidgetFactory
        operationPolicy = UI4.FormMaster.CreateParameterPolicy(
            None, self.node.getParameter('operation'))
        self.operationModeWidget = factory.buildWidget(self, operationPolicy)
        self.settingsWidget = QtWidgets.QWidget()
        self.settingsLayout = QtWidgets.QVBoxLayout()

    def show_settings(self):

        for i in range(self.settingsLayout.count()):
            w = self.settingsLayout.itemAt(i).widget()
            w.deleteLater()
        self.settingsWidget.hide()

        sel = self.aovListWidget.list.selectedItems()
        node = None
        if not len(sel) > 1 and not len(sel) == 0:
            sel = sel[0]
            for grp in self.node.getChildren():
                param = grp.getParameter('aov')
                if param and param.getValue(0) == sel._name:
                    node = grp
                    break
            if node is None:
                return
            aocdNode = node.getChildByIndex(0)
        else:
            return

        self.settingsWidget.show()
        factory = UI4.FormMaster.KatanaFactory.ParameterWidgetFactory
        lpePolicy = UI4.FormMaster.CreateParameterPolicy(
            None, aocdNode.getParameter('lightPathExpression'))
        lpeParam = factory.buildWidget(self, lpePolicy)
        self.settingsLayout.addWidget(lpeParam)

    def edit_widgets(self):
        self.settingsWidget.hide()

    def build_layouts(self):
        self.mainLayout.addWidget(self.operationModeWidget)
        self.mainLayout.addLayout(self.listsLayout)
        self.listsLayout.addWidget(self.aovListWidget)
        self.mainLayout.addWidget(self.settingsWidget)
        self.settingsWidget.setLayout(self.settingsLayout)

    def setup_styles(self):
        self.setStyleSheet("*{outline: 0;}")

    def handle_signals(self):
        self.aovListWidget.list.itemSelectionChanged.connect(self.show_settings)

    def populate(self):
        self.aovListWidget.list.clear()
        defaultAovs = SA.aovList
        aovsToAdd = [x.keys()[0] for x in defaultAovs]
        for activeAovParam in self.node.getParameter('activeAOVs').getChildren():
            activeAov = activeAovParam.getValue(0)
            if not activeAov in aovsToAdd:
                aovsToAdd.append(activeAov)

        items = []
        for aov in aovsToAdd:
            item = AovItem(name=aov, tree=self.aovListWidget.list, node=self.node)
            items.append(item)

        self.aovListWidget.tree_manip()

        return items


if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    win = ArnoldAOVsEditor(None, None)
    win.resize(600, 850)
    win.show()
    sys.exit(app.exec_())