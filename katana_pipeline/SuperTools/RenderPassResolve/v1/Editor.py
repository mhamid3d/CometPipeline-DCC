from PyQt5 import QtWidgets, QtGui, QtCore
from Katana import UI4
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


class RenderPassResolveEditor(QtWidgets.QWidget):
    def __init__(self, parent, node):
        if node:
            node.upgrade()

        self.node = node
        super(RenderPassResolveEditor, self).__init__(parent)

        self.mainLayout = QtWidgets.QVBoxLayout(self)
        self.setLayout(self.mainLayout)
        self.factory = UI4.FormMaster.KatanaFactory.ParameterWidgetFactory

        self.setup_ui()

    def setup_ui(self):
        self.create_widgets()
        self.edit_widgets()
        self.build_layouts()
        self.setup_styles()
        self.handle_signals()

    def create_widgets(self):
        # Layouts

        # Widgets
        self.renderPassWidget = self.factory.buildWidget(self, UI4.FormMaster.CreateParameterPolicy(None, self.node.getParameter('renderPass')))
        self.buildRenderWidget = self.factory.buildWidget(self, UI4.FormMaster.CreateParameterPolicy(None, self.node.getParameter('buildRenderNode')))

    def edit_widgets(self):
        pass

    def build_layouts(self):
        self.mainLayout.addWidget(self.renderPassWidget)
        self.mainLayout.addWidget(self.buildRenderWidget)

    def setup_styles(self):
        self.setStyleSheet("*{outline: 0;}")

    def handle_signals(self):
        pass


if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    win = RenderPassResolveEditor(None, None)
    win.resize(600, 850)
    win.show()
    sys.exit(app.exec_())
