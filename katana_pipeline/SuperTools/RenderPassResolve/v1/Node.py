from Katana import NodegraphAPI, UniqueName
from Upgrade import Upgrade
import ScriptActions as SA
import logging
import OpScripts

log = logging.getLogger("RenderPassResolve")


class RenderPassResolveNode(NodegraphAPI.SuperTool):

    def __init__(self):
        self.hideNodegraphGroupControls()
        self.addInputPort('in')
        self.addOutputPort('out')
        self.setup_parameters()
        self.setup_nodes()

    def setup_parameters(self):
        paramRenderPass = self.getParameters().createChildString("renderPass", "")
        paramBuildRenderNode = self.getParameters().createChildString("buildRenderNode", "")

        paramRenderPass.setExpression(
            '"/root/passes/" + project.variables.renderPass.value'
        )

    def setup_nodes(self):
        opScriptNode = NodegraphAPI.CreateNode("OpScript", self)
        opScriptNode.setName("Collection_Setup_OpScript")
        opScriptUserGroup = opScriptNode.getParameters().createChildGroup("user")
        renderPassParam = opScriptUserGroup.createChildString("renderPass", "")
        renderPassParam.setExpression("getParent().renderPass")
        opScriptNode.getParameter('applyWhere').setValue('at specific location', 0)
        opScriptNode.getParameter('location').setValue('/root', 0)
        opScriptNode.getParameter('script.lua').setValue(OpScripts.collection_create_script(), 0)

        pruneObjectsNode = NodegraphAPI.CreateNode("Prune", self)
        pruneObjectsNode.setName("PruneObjects_Prune")
        pruneObjectsNode.getParameter("cel").setValue("/$prune_objects/*", 0)

        lightObjectsASNode = NodegraphAPI.CreateNode("AttributeSet", self)
        lightObjectsASNode.setName("LightObjects_AttributeSet")
        lightObjectsASNode.getParameter("mode").setValue("CEL", 0)
        lightObjectsASNode.getParameter("celSelection").setValue("/root/world/lgt//* - /$light_objects/*", 0)
        lightObjectsASNode.getParameter("attributeName").setValue("visible", 0)
        lightObjectsASNode.getParameter("attributeType").setValue("integer", 0)
        lightObjectsASNode.getParameter("numberValue.i0").setValue(0, 0)

        aosTraceObjectsNode = NodegraphAPI.CreateNode("ArnoldObjectSettings", self)
        aosTraceObjectsNode.setName("TraceObjects_AOS")
        aosTraceObjectsNode.getParameter("CEL").setValue("/$trace_objects/*", 0)
        aosTraceObjectsNode.getParameter("args.arnoldStatements.visibility.AI_RAY_CAMERA.enable").setValue(1, 0)
        aosTraceObjectsNode.getParameter("args.arnoldStatements.visibility.AI_RAY_CAMERA.value").setValue(0, 0)

        aosCameraObjectsNode = NodegraphAPI.CreateNode("ArnoldObjectSettings", self)
        aosCameraObjectsNode.setName("CameraObjects_AOS")
        aosCameraObjectsNode.getParameter("CEL").setValue("/$camera_objects/*", 0)
        aosCameraObjectsNode.getParameter("args.arnoldStatements.visibility.AI_RAY_CAMERA.enable").setValue(1, 0)
        aosCameraObjectsNode.getParameter("args.arnoldStatements.visibility.AI_RAY_CAMERA.value").setValue(1, 0)

        aosMatteObjectsNode = NodegraphAPI.CreateNode("ArnoldObjectSettings", self)
        aosMatteObjectsNode.setName("MatteObjects_AOS")
        aosMatteObjectsNode.getParameter("CEL").setValue("/$matte_objects/*", 0)
        aosMatteObjectsNode.getParameter("args.arnoldStatements.visibility.AI_RAY_CAMERA.enable").setValue(1, 0)
        aosMatteObjectsNode.getParameter("args.arnoldStatements.visibility.AI_RAY_CAMERA.value").setValue(1, 0)
        aosMatteObjectsNode.getParameter("args.arnoldStatements.matte.enable").setValue(1, 0)
        aosMatteObjectsNode.getParameter("args.arnoldStatements.matte.value").setValue(1, 0)

        # Visibility Marking
        visibilityMarkingASNode = NodegraphAPI.CreateNode("AttributeSet", self)
        visibilityMarkingASNode.setName("VisibilitySet_AS")
        visibilityMarkingASNode.getParameter("mode").setValue("CEL", 0)
        visibilityMarkingASNode.getParameter("celSelection").setValue("/$camera_objects/* + /$light_objects/* + /$trace_objects/* + /$matte_objects/*", 0)
        visibilityMarkingASNode.getParameter("attributeName").setValue("visible", 0)
        visibilityMarkingASNode.getParameter("attributeType").setValue("integer", 0)
        visibilityMarkingASNode.getParameter("numberValue.i0").setValue(1, 0)

        opScriptNode.getInputPortByIndex(0).connect(self.getSendPort(self.getInputPortByIndex(0).getName()))
        pruneObjectsNode.getInputPortByIndex(0).connect(opScriptNode.getOutputPortByIndex(0))
        lightObjectsASNode.getInputPortByIndex(0).connect(pruneObjectsNode.getOutputPortByIndex(0))
        aosTraceObjectsNode.getInputPortByIndex(0).connect(lightObjectsASNode.getOutputPortByIndex(0))
        aosCameraObjectsNode.getInputPortByIndex(0).connect(aosTraceObjectsNode.getOutputPortByIndex(0))
        aosMatteObjectsNode.getInputPortByIndex(0).connect(aosCameraObjectsNode.getOutputPortByIndex(0))
        visibilityMarkingASNode.getInputPortByIndex(0).connect(aosMatteObjectsNode.getOutputPortByIndex(0))
        self.getReturnPort(self.getOutputPortByIndex(0).getName()).connect(visibilityMarkingASNode.getOutputPortByIndex(0))

        NodegraphAPI.SetNodePosition(pruneObjectsNode, (0, -50))
        NodegraphAPI.SetNodePosition(lightObjectsASNode, (0, -100))
        NodegraphAPI.SetNodePosition(aosTraceObjectsNode, (0, -150))
        NodegraphAPI.SetNodePosition(aosCameraObjectsNode, (0, -200))
        NodegraphAPI.SetNodePosition(aosMatteObjectsNode, (0, -250))

    def addParameterHints(self, attrName, inputDict):

        inputDict.update(_node_fields_hints.get(attrName, {}))

    def upgrade(self):
        if not self.isLocked():
            Upgrade(self)
        else:
            log.warning("Cannot upgrade locked node: {}".format(self.getName()))

    def setup_render_node(self):

        node = NodegraphAPI.CreateNode("Render", NodegraphAPI.GetRootNode())
        node.getInputPortByIndex(0).connect(self.getOutputPortByIndex(0))

        SA.add_node_reference_param(node, "node_render_pass_resolve", self)

        node.getParameter("passName").setExpression(
            "str(getNode(str(node_render_pass_resolve)).renderPass).split('/')[-1]"
        )

        pos = NodegraphAPI.GetNodePosition(self)

        NodegraphAPI.SetNodePosition(node, (pos[0], pos[1] - 100))


_node_fields_hints = {
    "RenderPassResolve.renderPass": {
        "label": "Render Pass",
        "help": "The current evaluated pass",
        "widget": "scenegraphLocation"
    },
    "RenderPassResolve.buildRenderNode": {
        "label": "Build Render Node",
        "help": "Create a render node corresponding to the active render pass",
        "widget": "scriptButton",
        "buttonText": "Build Render Node",
        "scriptText": """node.setup_render_node()"""
    }
}