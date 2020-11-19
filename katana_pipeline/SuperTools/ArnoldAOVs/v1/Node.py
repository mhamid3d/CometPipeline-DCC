from Katana import NodegraphAPI, Utils, UniqueName

from Upgrade import Upgrade
import ScriptActions as SA
import logging
import colorsys

log = logging.getLogger("ArnoldAOVs")


class ArnoldAOVsNode(NodegraphAPI.SuperTool):

    def __init__(self):
        self.hideNodegraphGroupControls()
        self.addInputPort('in')
        self.addOutputPort('out')
        self.color_incr = 0.0

        # Parameters
        paramOpHint = repr({
            'options__order': ['Append', 'Replace', 'Remove'],
            'widget': 'mapper',
            'options': {'Append': 'append', 'Replace': 'replace', 'Remove': 'remove'}
        })
        paramOperationMode = self.getParameters().createChildString('operation', 'append')
        paramOperationMode.setHintString(paramOpHint)

        paramActiveAOVsGroup = self.getParameters().createChildGroup('activeAOVs')
        paramHideDisabled = self.getParameters().createChildNumber('hideDisabled', 0)

        self.buildDefaultNetwork()

    def buildDefaultNetwork(self):
        opNode = NodegraphAPI.CreateNode("OpScript", self)
        opNode.setName("Replace_OpScript")

        opNode.getParameter("applyWhere").setValue("at specific location", 0)
        opNode.getParameter("location").setValue("/root", 0)

        script = """
        -- AOCD DELETION
        local aocd_aovs = Interface.GetAttr("arnoldGlobalStatements.outputChannels")
        local aocd_count = aocd_aovs:getNumberOfChildren()
        for i=0, aocd_count-1 do
            aovName = aocd_aovs:getChildName(i)
            attr = "arnoldGlobalStatements.outputChannels." .. aovName
            Interface.DeleteAttr(attr)
        end

        -- ROD DELETION
        local rod_aovs = Interface.GetAttr("renderSettings.outputs")
        local rod_count = rod_aovs:getNumberOfChildren()
        for i=0, rod_count-1 do
            aovName = rod_aovs:getChildName(i)
            attr = "renderSettings.outputs." .. aovName
            if aovName ~= "primary" then
                Interface.DeleteAttr(attr)
            end
        end
        """

        opNode.getParameter("script.lua").setValue(script, 0)
        opNode.getInputPortByIndex(0).connect(self.getSendPort(self.getInputPortByIndex(0).getName()))

        opDisableParam = opNode.getParameters().createChildNumber('disable', 0)
        opDisableParam.setHintString('{"widget": "checkBox"}')
        opDisableParam.setExpression("0 if getParent().operation == 'replace' else 1")

        cryptoGroup = NodegraphAPI.CreateNode("Group", self)
        cryptoGroup.setName("Cryptomatte_Setup")
        cryptoGroup.addInputPort('in')
        cryptoGroup.addOutputPort('out')
        cryptoGroup.getInputPortByIndex(0).connect(opNode.getOutputPortByIndex(0))
        NodegraphAPI.SetNodePosition(cryptoGroup, (0, -50))

        cryptoNode = NodegraphAPI.CreateNode("Material", cryptoGroup)
        cryptoNode.setName("Cryptomatte_Material")
        cryptoNode.getParameter('name').setValue('cryptomatte', 0)
        shaderParam = cryptoNode.addShaderType("arnoldSurface")
        cryptoNode.checkDynamicParameters()
        shaderParam.getChild('enable').setValue(1, 0)
        shaderParam.getChild('value').setValue('cryptomatte', 0)

        cryptoAS = NodegraphAPI.CreateNode('AttributeSet', cryptoGroup)
        cryptoAS.getParameter('paths.i0').setValue('/root', 0)
        cryptoAS.getParameter('attributeName').setValue('arnoldGlobalStatements.aov_shaders', 0)
        cryptoAS.getParameter('attributeType').setValue('string', 0)
        cryptoAS.getParameter('stringValue.i0').setValue('/root/materials/cryptomatte', 0)
        NodegraphAPI.SetNodePosition(cryptoAS, (0, -50))

        cryptoNode.getInputPortByIndex(0).connect(cryptoGroup.getSendPort(cryptoGroup.getInputPortByIndex(0).getName()))
        cryptoAS.getInputPortByIndex(0).connect(cryptoNode.getOutputPortByIndex(0))
        cryptoAS.getOutputPortByIndex(0).connect(cryptoGroup.getReturnPort(cryptoGroup.getOutputPortByIndex(0).getName()))

        cryptoGroup.getOutputPortByIndex(0).connect(self.getReturnPort(self.getOutputPortByIndex(0).getName()))

    def addAov(self, aovName):

        aovName = str(aovName)

        grp = NodegraphAPI.CreateNode("Group", self)
        grp.addInputPort('in')
        grp.addOutputPort('out')
        grp.setName("_AOV_{}".format(aovName))
        grp.getParameters().createChildString('aov', aovName)

        returnPort = self.getReturnPort(self.getOutputPortByIndex(0).getName())
        lastPort = returnPort.getConnectedPort(0)

        if lastPort and not lastPort.getNode() == self:
            node = lastPort.getNode()
            grp.getInputPortByIndex(0).connect(node.getOutputPortByIndex(0))
            pos = NodegraphAPI.GetNodePosition(node)
            NodegraphAPI.SetNodePosition(grp, (0, pos[1] - 80))
        else:
            grp.getInputPortByIndex(0).connect(self.getSendPort(self.getInputPortByIndex(0).getName()))

        grp.getOutputPortByIndex(0).connect(self.getReturnPort(self.getOutputPortByIndex(0).getName()))

        aocd = NodegraphAPI.CreateNode("ArnoldOutputChannelDefine", grp)
        rod = NodegraphAPI.CreateNode("RenderOutputDefine", grp)
        asgs = NodegraphAPI.CreateNode("GroupStack", grp)
        asgsParam = asgs.getParameters().createChildNumber('disable', 0)
        asgsParam.setHintString('{"widget": "checkBox"}')
        asgsParam.setExpression("0 if getParent().getParent().operation == 'remove' else 1")
        asgs.setName("_ASGS_{}".format(aovName))
        asgs.setChildNodeType("AttributeSet")
        aocd_as = asgs.buildChildNode()
        rod_as = asgs.buildChildNode()
        aocd_as.setName("_AS_AOCD_{}".format(aovName))
        rod_as.setName("_AS_ROD_{}".format(aovName))
        aocd.setName("_AOCD_{}".format(aovName))
        rod.setName("_ROD_{}".format(aovName))
        aocd_as.getParameter("paths.i0").setValue("/root", 0)
        rod_as.getParameter("paths.i0").setValue("/root", 0)
        aocd_as.getParameter("action").setValue("Delete", 0)
        rod_as.getParameter("action").setValue("Delete", 0)
        aocd_as.getParameter("attributeName").setValue("arnoldGlobalStatements.outputChannels.{}".format(aovName), 0)
        rod_as.getParameter("attributeName").setValue("renderSettings.outputs.{}".format(aovName), 0)
        NodegraphAPI.SetNodePosition(rod, (0, -50))
        NodegraphAPI.SetNodePosition(asgs, (0, -100))

        aocd.getInputPortByIndex(0).connect(grp.getSendPort(grp.getInputPortByIndex(0).getName()))
        aocd.getOutputPortByIndex(0).connect(rod.getInputPortByIndex(0))
        asgs.getInputPortByIndex(0).connect(rod.getOutputPortByIndex(0))
        asgs.getOutputPortByIndex(0).connect(grp.getReturnPort(grp.getOutputPortByIndex(0).getName()))

        aocd.getParameter('name').setValue(aovName, 0)
        aocd.getParameter('channel').setValue(aovName, 0)

        driver = aocd.getParameter('nodes').createChildGroup('driverParameters')

        parameter = driver.createChildGroup('tiled')
        parameter.createChildNumber('enable', 1)
        parameter.createChildNumber('value', 0)
        parameter.createChildString('type', 'IntAttr')

        parameter = driver.createChildGroup('autocrop')
        parameter.createChildNumber('enable', 1)
        parameter.createChildNumber('value', 1)
        parameter.createChildString('type', 'IntAttr')

        for aov in SA.aovList:
            if aov.keys()[0] == aovName:
                data = aov.values()[0]
                aocd.getParameter('type').setValue(data['data'].upper(), 0)
                filt = data['filter']
                if not filt == 'None':
                    aocd.getParameter('filter').setValue(filt + "_filter", 0)
                else:
                    pass
                    # aocd.getParameter('filter').setValue('<inherit>', 0)
                if 'lpe' in data.keys():
                    lpe = data['lpe']
                    aocd.getParameter('lightPathExpression').setValue(lpe, 0)

        parameter = rod.getParameter('args.renderSettings.outputs.outputName.locationSettings').createChildGroup(
            'renderLocation')
        parameter.createChildNumber('enable', 1)
        paramFile = parameter.createChildString('value', '')
        parameter.createChildString('type', 'StringAttr')
        paramFile.setExpression("""getenv('COMET_RENDER_LOCATION', '') + '/' + str(outputName) + '/primary.####.' + str(args.renderSettings.outputs.outputName.rendererSettings.fileExtension.value)""")

        rod.checkDynamicParameters()
        rod.getParameter('outputName').setValue(aovName, 0)
        rod.getParameter('args.renderSettings.outputs.outputName.rendererSettings.channel.enable').setValue(1, 0)
        rod.getParameter('args.renderSettings.outputs.outputName.rendererSettings.channel.value').setValue(aovName, 0)
        rod.getParameter('args.renderSettings.outputs.outputName.locationType.enable').setValue(1, 0)
        rod.getParameter('args.renderSettings.outputs.outputName.locationType.value').setValue('file', 0)

        if aovName == 'deep':
            aocd.getParameter('driver').setValue('driver_deepexr', 0)
            rod.getParameter('args.renderSettings.outputs.outputName.type.enable').setValue(1, 0)
            rod.getParameter('args.renderSettings.outputs.outputName.type.value').setValue('deep', 0)
        elif aovName in ["crypto_object", "crypto_material", "crypto_asset"]:
            rod.getParameter('args.renderSettings.outputs.outputName.rendererSettings.lightAgnostic.enable').setValue(1, 0)
            rod.getParameter('args.renderSettings.outputs.outputName.rendererSettings.lightAgnostic.value').setValue(1, 0)

        return grp

    def removeAov(self, aovName):
        for node in self.getChildren():
            param = node.getParameter('aov')
            if param and param.getValue(0) == aovName:
                SA.deleteNode(node)

    def upgrade(self):
        if not self.isLocked():
            Upgrade(self)
        else:
            log.warning("Cannot upgrade locked node: {}".format(self.getName()))