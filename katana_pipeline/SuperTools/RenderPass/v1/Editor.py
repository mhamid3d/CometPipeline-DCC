from PyQt5 import QtWidgets, QtGui, QtCore
from Katana import UI4, Utils, QT4FormWidgets
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


update_parameters_list = [
    "passRootLocation"
]


class RenderPassEditor(QtWidgets.QWidget):
    def __init__(self, parent, node):
        self.__node = node

        QtWidgets.QWidget.__init__(self, parent)
        QtWidgets.QVBoxLayout(self)

        self.__frozen = True
        self.__updateOnIdle = False

        katana_factory = UI4.FormMaster.KatanaFactory.ParameterWidgetFactory

        scenegraph_group = QT4FormWidgets.PythonGroupPolicy("SceneGraph")
        scenegraph_group.getWidgetHints()["hideTitle"] = True
        scenegraph_group.getWidgetHints()["open"] = True

        scenegraph_pass_root_location_policy = UI4.FormMaster.CreateParameterPolicy(
            scenegraph_group, self.__node.getParameter("passRootLocation"))
        scenegraph_group.addChildPolicy(scenegraph_pass_root_location_policy)

        widget_ui = katana_factory.buildWidget(self, scenegraph_group)

        self.layout().addWidget(widget_ui)

        self.create_ui_from_generic_assign("renderPass", "render_pass_ga")

        # TODO
        self.render_pass_ga_node = SA.get_reference_node(self.__node, "render_pass_ga")
        # TODO
        self.render_pass_ga_update_parameters_list = [
            self.render_pass_ga_node.getParameter("args.renderPass.definition.prefix.enable"),
            self.render_pass_ga_node.getParameter("args.renderPass.definition.label.enable"),
            self.render_pass_ga_node.getParameter("args.renderPass.definition.layer.enable"),
            self.render_pass_ga_node.getParameter("args.renderPass.definition.type.enable")
        ]

    def create_ui_from_generic_assign(self, generic_assign_name, node_reference_name):
        generic_assign_node = SA.get_reference_node(self.__node, node_reference_name)

        group_parameter = generic_assign_node.getParameter("args.{generic_assign_name}".format(
            generic_assign_name=generic_assign_name
        ))

        policy = UI4.FormMaster.CreateParameterPolicy(None, group_parameter)
        widget_factory = UI4.FormMaster.KatanaFactory.ParameterWidgetFactory
        widget = widget_factory.buildWidget(self, policy)

        self.layout().addWidget(widget)
    #
    # def create_ui_group_from_generic_assign(self, generic_assign_name, node_reference_name, group_name):
    #     generic_assign_node = SA.get_reference_node(self.__node, node_reference_name)
    #
    #     group_parameter = generic_assign_node.getParameter("args.{generic_assign_name}.{group_name}".format(
    #         generic_assign_name=generic_assign_name,
    #         group_name=group_name
    #     ))
    #
    #     policy = UI4.FormMaster.CreateParameterPolicy(None, group_parameter)
    #     widget_factory = UI4.FormMaster.KatanaFactory.ParameterWidgetFactory
    #     widget = widget_factory.buildWidget(self, policy)
    #
    #     self.layout().addWidget(widget)
    #
    def showEvent(self, event):
        QtWidgets.QWidget.showEvent(self, event)
        if self.__frozen:
            self.__frozen = False
            self._thaw()

    def hideEvent(self, event):
        QtWidgets.QWidget.hideEvent(self, event)
        if not self.__frozen:
            self.__frozen = True
            self._freeze()

    def _thaw(self):
        self.__setupEventHandlers(True)

    def _freeze(self):
        self.__setupEventHandlers(False)

    def __setupEventHandlers(self, enabled):
        Utils.EventModule.RegisterEventHandler(self.__idle_callback,
            "event_idle", enabled=enabled)
        Utils.EventModule.RegisterCollapsedHandler(self.__updateCB,
            "parameter_finalizeValue", enabled=enabled)

    def __updateCB(self, args):

        if self.__updateOnIdle:
            return

        for arg in args:
            if arg[0] in "parameter_finalizeValue":
                node = arg[2].get("node")
                param = arg[2].get("param")

                if node == self.__node and param.getName() in update_parameters_list:
                    self.__updateOnIdle = True

                    return
                elif node == self.render_pass_ga_node and param in self.render_pass_ga_update_parameters_list:
                    self.__updateOnIdle = True

                    return

    def __idle_callback(self, *args, **kwargs):
        if self.__updateOnIdle:
            self.__updateOnIdle = False

            self.__node.clear_pass_data()
            self.__node.update_pass_data(self.render_pass_ga_node)
            self.__node.update_pass_location(self.render_pass_ga_node)


if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    win = RenderPassEditor(None, None)
    win.resize(600, 850)
    win.show()
    sys.exit(app.exec_())
