from Katana import NodegraphAPI, Utils, UniqueName
from Upgrade import Upgrade
import ScriptActions as SA
import OpScripts
import logging

log = logging.getLogger("RenderPass")


class RenderPassNode(NodegraphAPI.SuperTool):

    def __init__(self):
        self.hideNodegraphGroupControls()
        self.addInputPort('in')
        self.addOutputPort('out')

        self.pass_data = {}
        self.pass_root_location = ""
        self.pass_name = ""
        self.pass_location = ""

        self.setup_parameters()
        self.setup_nodes()

    def setup_parameters(self):
        self.getParameters().createChildString("passRootLocation", "/root/passes")

    def setup_nodes(self):
        merge_node = self.create_merge_inputs_node()
        render_pass_ga_node = self.create_pass_define_ga_node()
        opscript_node = self.create_opscript_node()

        render_pass_ga_node.getParameters().getChild("CEL").setExpression('getParent().passRootLocation + "/" + '
        'getParent().getNode().getChild(str(getParent().getChildren()[3])).getParameter("user.prefix").getValue(frame) + '
        '"_" + getParent().getNode().getChild(str(getParent().getChildren()[3])).getParameter("user.label").getValue(frame) + ' 
        '"_" + getParent().getNode().getChild(str(getParent().getChildren()[3])).getParameter("user.layer").getValue(frame) + ' 
        '"_" + getParent().getNode().getChild(str(getParent().getChildren()[3])).getParameter("user.type").getValue(frame)')

        NodegraphAPI.SetNodePosition(opscript_node, (0, -50))
        NodegraphAPI.SetNodePosition(render_pass_ga_node, (0, -100))

        self.update_pass_data(render_pass_ga_node)
        self.setup_opscript_node(opscript_node)
        self.update_pass_location(render_pass_ga_node)

        merge_node.getInputPortByIndex(0).connect(self.getSendPort(self.getInputPortByIndex(0).getName()))
        opscript_node.getInputPortByIndex(0).connect(merge_node.getOutputPortByIndex(0))
        opscript_node.getOutputPortByIndex(0).connect(render_pass_ga_node.getInputPortByIndex(0))
        render_pass_ga_node.getOutputPortByIndex(0).connect(self.getReturnPort(self.getOutputPortByIndex(0).getName()))

    def addParameterHints(self, attrName, inputDict):

        inputDict.update(_node_fields_hints.get(attrName, {}))

    def create_merge_inputs_node(self):

        merge_node = NodegraphAPI.CreateNode("Merge", self)
        merge_node.setName("Merge_Input")
        merge_node.addInputPort('sceneInput')

        SA.add_node_reference_param(self, "node_merge", merge_node)

        return merge_node

    def create_opscript_node(self):

        opscript_node = NodegraphAPI.CreateNode('OpScript', self)
        opscript_node.setName('OpScript_CreatePassLocation')

        SA.add_node_reference_param(self, 'node_opscript_create_pass', opscript_node)

        return opscript_node

    def create_pass_define_ga_node(self):

        render_pass_ga_node = NodegraphAPI.CreateNode("RenderPassGA", self)
        render_pass_ga_node.setName("RenderPassGA_PassParameters")

        SA.add_node_reference_param(self, "node_render_pass_ga", render_pass_ga_node)

        return render_pass_ga_node

    def setup_opscript_node(self, opscript_node):

        opscript_node.getParameter("script.lua").setValue(OpScripts.pass_location_script(), 0)

        configure_pass_location_opscript_usergroup = opscript_node.getParameters().createChildGroup("user")
        configure_pass_location_opscript_usergroup.createChildString("passRootLocation", "")
        configure_pass_location_opscript_usergroup.createChildString("enablePass", "")
        configure_pass_location_opscript_usergroup.createChildString("prefix", "")
        configure_pass_location_opscript_usergroup.createChildString("label", "")
        configure_pass_location_opscript_usergroup.createChildString("layer", "")
        configure_pass_location_opscript_usergroup.createChildString("type", "")

        opscript_node.getParameter("user.passRootLocation").setExpression(
            ("getParent().passRootLocation")
        )
        opscript_node.getParameter("user.enablePass").setExpression(
            ("getParent().getNode().getChild(str(getParent().getChildren()[2])).getParameter(\"args.renderPass.enablePass" +
            ".value\").getValue(frame) if getParent().getNode().getChild(str(getParent().getChildren()[2]))." +
            "getParameter(\"args.renderPass.enablePass.enable\").getValue(frame) else " +
            "{default_value}").format(
                default_value=self.pass_data["enablePass"]["default"]
            ), True)

        for param_name in self.pass_data["definition"].keys():
            '''getParent().getNode().getChild(str(getParent().getChildren()[2])).getParameter(
                "args.renderPass.definition.label.value").getValue(frame) if getParent().getNode().getChild(
                str(getParent().getChildren()[2])).getParameter("args.renderPass.definition.label.enable").getValue(
                frame) else "label" '''
            opscript_node.getParameter("user.{param_name}".format(param_name=param_name)).setExpression(
                ("getParent().getNode().getChild(str(getParent().getChildren()[2])).getParameter(\"args.renderPass.definition" +
                ".{param_name}.value\").getValue(frame) if getParent().getNode().getChild(str(getParent().getChildren()[2]))." +
                "getParameter(\"args.renderPass.definition.{param_name}.enable\").getValue(frame) else " +
                "\"{default_value}\"").format(
                    param_name=param_name,
                    default_value=self.pass_data["definition"][param_name]["default"]
                ), True)

        opscript_node.getParameter("applyWhen").setValue("immediate", 0)
        opscript_node.getParameter("applyWhere").setValue("at all locations", 0)
        opscript_node.getParameter("inputBehavior").setValue("only valid", 0)

    def update_pass_data(self, render_pass_ga_node):

        # TODO
        self.pass_data["enablePass"] = {}
        self.pass_data["enablePass"]["value"] = render_pass_ga_node.getParameter(
            "args.renderPass.enablePass.value"
        ).getValue(0)
        self.pass_data["enablePass"]["enable"] = render_pass_ga_node.getParameter(
            "args.renderPass.enablePass.enable"
        ).getValue(0)

        if not self.pass_data["enablePass"].get("default"):
            self.pass_data["enablePass"]["default"] = render_pass_ga_node.getParameter(
                "args.renderPass.enablePass.default"
            ).getValue(0)

        # TODO
        self.pass_data["definition"] = {}
        for child in render_pass_ga_node.getParameter("args.renderPass.definition").getChildren():
            child_param_name = child.getName()

            if child_param_name == "__hints":
                continue

            self.pass_data["definition"][child_param_name] = {}
            self.pass_data["definition"][child_param_name]["value"] = render_pass_ga_node.getParameter(
                "args.renderPass.definition.{param_name}.value".format(
                    param_name=child_param_name
                )
            ).getValue(0)
            self.pass_data["definition"][child_param_name]["enable"] = render_pass_ga_node.getParameter(
                "args.renderPass.definition.{param_name}.enable".format(
                    param_name=child_param_name
                )
            ).getValue(0)

            if not self.pass_data["definition"][child_param_name].get("default"):
                self.pass_data["definition"][child_param_name]["default"] = render_pass_ga_node.getParameter(
                    "args.renderPass.definition.{param_name}.default".format(
                        param_name=child_param_name
                    )
                ).getValue(0)

    def update_pass_location(self, render_pass_ga_node):
        return

        # TODO: Use the correct frame time instead
        self.pass_root_location = self.getParameter("passRootLocation").getValue(0)
        self.pass_name = "{prefix}_{label}_{layer}_{type}".format(
            prefix=(self.pass_data["definition"]["prefix"]["value"]
                if self.pass_data["definition"]["prefix"]["enable"]
                else self.pass_data["definition"]["prefix"]["default"]),
            label=(self.pass_data["definition"]["label"]["value"]
                if self.pass_data["definition"]["label"]["enable"]
                else self.pass_data["definition"]["label"]["default"]),
            layer=(self.pass_data["definition"]["layer"]["value"]
                if self.pass_data["definition"]["layer"]["enable"]
                else self.pass_data["definition"]["layer"]["default"]),
            type=(self.pass_data["definition"]["type"]["value"]
                if self.pass_data["definition"]["type"]["enable"]
                else self.pass_data["definition"]["type"]["default"])
        )
        self.pass_location = "{pass_root_location}/{pass_name}".format(
            pass_root_location=self.pass_root_location,
            pass_name=self.pass_name
        )

        render_pass_ga_node.getParameters().getChild("CEL").setExpression(
            ("\"{pass_location}\"").format(
                pass_location=self.pass_location
            )
        )

    def clear_pass_data(self):

        self.pass_data = {}
        self.pass_root_location = ""
        self.pass_name = ""
        self.pass_location = ""

    def reset_node_network(self):

        for child_node in self.getChildren():
            child_node.delete()

        self.setup_nodes()

    def upgrade(self):
        if not self.isLocked():
            Upgrade(self)
        else:
            log.warning("Cannot upgrade locked node: {}".format(self.getName()))


_node_fields_hints = {
    "RenderPass.passRootLocation": {
        "label": "Pass Root Location",
        "help": "Define under which location the \"pass\" location type should be created.",
        "widget": "scenegraphLocation"
    }
}