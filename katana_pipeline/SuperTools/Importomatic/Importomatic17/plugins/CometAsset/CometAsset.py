from Katana import NodegraphAPI, Plugins, Utils, AssetAPI
import logging, os, random, xml.etree.ElementTree as ET

LOG_LEVEL = logging.INFO
log = logging.getLogger('CometAsset')
log.setLevel(LOG_LEVEL)
ImportomaticAPI = Plugins.ImportomaticAPI
g_iconBasePath = os.path.dirname(__file__)
g_iconPath = os.path.dirname(__file__) + '/assembly16.png'


def Register():
    ImportomaticAPI.AssetModule.RegisterCreateCallback('Add Comet Asset', FindAndAddAlembicGeometry)
    ImportomaticAPI.AssetModule.RegisterBatchCreateCallback('CometAsset', AddAlembicGeometry)
    ImportomaticAPI.AssetModule.RegisterType('CometAsset', AlembicModule())


AddLookFileAction = None
AddAttributeFileAction = None


def RegisterGUI():
    global AddAttributeFileAction
    global AddLookFileAction
    from Katana import QtGui, QtCore, QtWidgets

    class AddLookFileAction(QtWidgets.QAction):

        def __init__(self, parent, itemClass):
            QtWidgets.QAction.__init__(self, 'Assign Look File', parent)
            self.__itemClass = itemClass
            self.triggered.connect(self.__go)

        def __go(self, checked=False):
            from Katana import UI4
            lookFile = UI4.Util.AssetId.BrowseForAsset('', 'Select file', False, {'fileTypes': 'klf', 'acceptDir': True,
                                                                                  'context': AssetAPI.kAssetContextLookFile})
            if not lookFile:
                return
            self.__itemClass.appendLookFile(lookFile)

    class AddAttributeFileAction(QtWidgets.QAction):

        def __init__(self, parent, itemClass):
            QtWidgets.QAction.__init__(self, 'Assign Attribute File', parent)
            self.__itemClass = itemClass
            self.triggered.connect(self.__go)

        def __go(self, checked=False):
            from Katana import UI4
            attributeFile = UI4.Util.AssetId.BrowseForAsset('', 'Select file', False, {'fileTypes': 'xml',
                                                                                       'context': AssetAPI.kAssetContextAttributeFile})
            if not attributeFile:
                return
            self.__itemClass.appendAttributeFile(attributeFile)


def getHashValue(node):
    return str(hash(repr(node)))


def connectAndPlaceNodes(groupNode):
    noNodes = groupNode.getNumChildren()
    stepSize = -80
    counter = 0
    lastNode = groupNode.getChildByIndex(0)
    for n in groupNode.getChildren():
        if n.getType() == 'Alembic_In':
            pass
        else:
            counter = counter + 1
            NodegraphAPI.SetNodePosition(n, (0, stepSize * counter))
            lastNode.getOutputPortByIndex(0).connect(n.getInputPortByIndex(0))
            lastNode = n

    lastNode.getOutputPortByIndex(0).connect(groupNode.getReturnPort('out'))


def addLookFileNodes(groupNode, lookRef, lookCel, ignore='False'):
    noAssigns = 0
    assignNodes = []
    for childNode in groupNode.getChildren():
        if childNode.getType() == 'LookFileAssign':
            assignNodes.append(childNode)

    nodeKstdAssign = NodegraphAPI.CreateNode('LookFileAssign')
    nodeKstdAssign.setParent(groupNode)
    nodeKstdAssign.getParameter('CEL').setExpressionFlag(True)
    nodeKstdAssign.getParameter('CEL').setExpression(lookCel)
    nodeKstdAssign.getParameter('args.lookfile.asset.enable').setValue(1, 0)
    nodeKstdAssign.getParameter('args.lookfile.asset.value').setValue(lookRef, 0)
    assignNodes.append(nodeKstdAssign)
    if ignore == 'True':
        nodeKstdAssign.setBypassed(True)
    return nodeKstdAssign


def addAttributeFileNodes(groupNode, attrRef, attrCel, attrCustomBrowser='', groupName='attributeFile', ignore='False'):
    attrFileIn = NodegraphAPI.CreateNode('AttributeFile_In')
    attrFileIn.setParent(groupNode)
    attrFileIn.getParameter('CEL').setExpressionFlag(True)
    attrFileIn.getParameter('CEL').setExpression(attrCel)
    attrFileIn.getParameter('filepath').setValue(attrRef, 0)
    attrFileIn.getParameter('sofilepath').setValue(attrCustomBrowser, 0)
    if groupName is not None and groupName != '':
        attrFileIn.getParameter('groupAttr').setValue(groupName, 0)
    if ignore == 'True':
        attrFileIn.setBypassed(True)
    return attrFileIn


def traverseHierarchy(node, hierarchy):
    if node.getName() != 'Alembic':
        hierarchy.append(node.getName())
    parent = node.getParent()
    if parent is not None:
        traverseHierarchy(parent, hierarchy)
    return


def findParentHierarchy(node):
    flatString = ''
    hierarchy = []
    traverseHierarchy(node, hierarchy)
    for item in reversed(hierarchy):
        flatString = flatString + item + '.'

    return flatString


def placeAtTop(assetParam, extensionName):
    extensionParam = assetParam.getChild(extensionName)
    if extensionParam is not None:
        assetParam.reorderChild(extensionParam, 0)
    return


def reorderExtensions(assetParam):
    placeAtTop(assetParam, 'modifiers')
    placeAtTop(assetParam, 'looks')


def addAttributeFileParams(assetParam, attrRef, attrCel, attrCustomBrowser='', groupName='attributeFile',
                           allowDelete=True):
    assetAttributesParam = assetParam.getChild('modifiers')
    if not assetAttributesParam:
        assetAttributesParam = assetParam.createChildGroup('modifiers')
    assetAttr = assetAttributesParam.createChildGroup('modifier')
    name = attrRef[attrRef.rfind('/') + 1:]
    assetAttr.createChildString('name', name)
    assetAttr.createChildString('path', attrRef)
    assetAttr.createChildString('cel', attrCel)
    assetAttr.createChildString('customBrowser', attrCustomBrowser)
    assetAttr.createChildString('groupName', groupName)
    assetAttr.createChildString('_type', 'attributeFile')
    assetAttr.createChildString('_allowDelete', str(allowDelete))
    assetAttr.createChildString('_ignore', 'False')
    reorderExtensions(assetParam)


def addLookFileParams(assetParam, lookRef, lookCel, allowDelete=True):
    assetLooksParam = assetParam.getChild('looks')
    if not assetLooksParam:
        assetLooksParam = assetParam.createChildGroup('looks')
    assetLook = assetLooksParam.createChildGroup('look')
    lookName = lookRef[lookRef.rfind('/') + 1:]
    assetLook.createChildString('name', lookName)
    assetLook.createChildString('path', lookRef)
    assetLook.createChildString('cel', lookCel)
    assetLook.createChildString('_allowDelete', str(allowDelete))
    assetLook.createChildString('_ignore', 'False')
    reorderExtensions(assetParam)


def getXmlAttrib(node, attrName, notFoundIsNone=False):
    try:
        attr = node.attrib[attrName]
        return attr
    except:
        if notFoundIsNone:
            return
        else:
            return ''

    return


def findInstances(rootName, paramNode, sgPath):
    sgExtendedPath = sgPath + '/' + rootName
    asmbParam = paramNode.getChild(rootName)
    if not asmbParam:
        asmbParam = paramNode.createChildGroup(rootName)
        asmbParam.createChildString('_ignore', 'False')
        asmbParam.createChildString('_sgPath', sgExtendedPath)


def FindAndAddAlembicGeometry(importomaticNode):
    return
    assetId = UI4.Util.AssetId.BrowseForAsset('', 'Select file', False,
                                              {'fileTypes': 'abc', 'context': AssetAPI.kAssetContextAlembic})
    if not assetId:
        return
    return AddAlembicGeometry(importomaticNode, assetId)


def AddAlembicGeometry(importomaticNode, assetId, locationExpression=None):
    assetPlugin = AssetAPI.GetDefaultAssetPlugin()
    rootInstanceName = assetPlugin.getAssetDisplayName(assetId)
    node = NodegraphAPI.CreateNode('Group')
    node.setName(rootInstanceName)
    uniqueRootName = node.getName()
    node.setName(uniqueRootName)
    node.setType('Alembic')
    node.addOutputPort('out')
    alembicInNode = NodegraphAPI.CreateNode('Alembic_In', node)
    alembicInNode.getOutputPortByIndex(0).connect(node.getReturnPort('out'))
    if locationExpression:
        alembicInNode.getParameter('name').setExpression(locationExpression, True)
    else:
        baseLocation = '/root/world/geo'
        location = baseLocation + '/' + uniqueRootName
        alembicInNode.getParameter('name').setValue(location, 0)
    alembicInNode.getParameter('abcAsset').setValue(assetId, 0)
    assetInfoParam = node.getParameters().createChildGroup('assetInfo')
    findInstances(uniqueRootName, assetInfoParam, '')
    BuildScenegraph(node)
    return node


def CleanScenegraph(node):
    for childNode in node.getChildren():
        if childNode.getType() != 'Alembic_In':
            childNode.delete()


def TraverseAndBuildNodes(node, param):
    if param.getName() == 'modifiers':
        modifierList = param.getChildren()
        for modParam in modifierList:
            modifierType = modParam.getChild('_type').getValue(0)
            if modifierType == 'attributeFile':
                attrRef = modParam.getChild('path').getValue(0)
                attrCel = modParam.getChild('cel').getValue(0)
                attrCustomBrowser = modParam.getChild('customBrowser').getValue(0)
                groupName = modParam.getChild('groupName').getValue(0)
                ignore = modParam.getChild('_ignore').getValue(0)
                afNode = addAttributeFileNodes(node, attrRef, attrCel, attrCustomBrowser, groupName, ignore)
                nodeHash = getHashValue(afNode)
                if modParam.getChild('_hash'):
                    modParam.getChild('_hash').setValue(nodeHash, 0)
                else:
                    modParam.createChildString('_hash', nodeHash)

    elif param.getName() == 'looks':
        lookList = param.getChildren()
        for lookParam in lookList:
            lookRef = lookParam.getChild('path').getValue(0)
            lookCel = lookParam.getChild('cel').getValue(0)
            ignore = lookParam.getChild('_ignore').getValue(0)
            lfNode = addLookFileNodes(node, lookRef, lookCel, ignore)
            nodeHash = getHashValue(lfNode)
            if lookParam.getChild('_hash'):
                lookParam.getChild('_hash').setValue(nodeHash, 0)
            else:
                lookParam.createChildString('_hash', nodeHash)

    if param.getNumChildren() > 0:
        connector = '-'
        for p in param.getChildren():
            TraverseAndBuildNodes(node, p)


def BuildScenegraph(node):
    CleanScenegraph(node)
    assetParam = node.getParameter('assetInfo')
    if assetParam is not None:
        TraverseAndBuildNodes(node, assetParam)
    connectAndPlaceNodes(node)
    return


def findNodeTypeByHash(groupNode, hashValue, searchType):
    for childNode in groupNode.getChildren():
        if childNode.getType() == searchType and getHashValue(childNode) == hashValue:
            return childNode

    BuildScenegraph(groupNode)
    from Katana import UI4
    UI4.Widgets.MessageBox.Warning('Message',
                                   'The Importomatic node has been rebuilt due to data inconsistency. Please try again.')
    return


class AlembicModule(ImportomaticAPI.AssetModule):

    def getAssetTreeRoot(self, node):
        return AlembicTreeRoot(node)


class AlembicTreeRoot(ImportomaticAPI.AssetTreeChild):

    def __init__(self, node):
        self.__node = node
        self.__assetParam = self.__node.getParameter('assetInfo')
        self.__param = self.__assetParam.getChild(self.__node.getName())

    def _getAlembicNode(self):
        alembicNode = self.__node.getChildByIndex(0)
        return alembicNode

    def getAssetId(self):
        alembicNode = self._getAlembicNode()
        assetId = alembicNode.getParameterValue('abcAsset', 0)
        return assetId

    def setAssetId(self, assetId):
        alembicNode = self._getAlembicNode()
        assetParam = alembicNode.getParameter('abcAsset')
        assetParam.setValue(assetId, 0)

    def setItemState(self, item):
        from Katana import UI4
        ScenegraphIconManager = UI4.Util.ScenegraphIconManager
        IconManager = UI4.Util.IconManager
        item.setText(ImportomaticAPI.NAME_COLUMN, self.__node.getName())
        item.setIcon(ImportomaticAPI.NAME_COLUMN, IconManager.GetIcon(g_iconPath))

    def getChildren(self):
        children = []
        if self.__assetParam.getNumChildren() > 0:
            for p in self.__assetParam.getChildren():
                if p.getName() == 'looks':
                    for look in p.getChildren():
                        children.append(LookFileTreeHandler(self.__node, look))

                elif p.getName() == 'modifiers':
                    children.append(ModifierRootHandler(self.__node, p))

        return children

    def getItemKey(self):
        return self.__node

    def getEditor(self, widgetParent):
        handler = ImportomaticAPI.AssetModule.GetHandlerForType(self.__node)
        alembicNode = self._getAlembicNode()
        return handler.getEditor(alembicNode, widgetParent)

    def isDeletable(self):
        return True

    def isSelectable(self):
        return True

    def delete(self):
        self.__node.delete()

    def isIgnorable(self):
        return True

    def isIgnored(self):
        return self.__node.isBypassed()

    def setIgnored(self, state):
        self.__node.setBypassed(state)

    def addNodeObservers(self, callback):
        callback(self.__node)

    def addToContextMenu(self, menu, importomaticNode):
        menu.addSeparator()
        menu.addAction(AddLookFileAction(menu, self))
        menu.addAction(AddAttributeFileAction(menu, self))

    def appendLookFile(self, lookFileName):
        celValue = "getNode('%s').name" % self._getAlembicNode().getName()
        addLookFileParams(self.__assetParam, lookFileName, celValue)
        BuildScenegraph(self.__node)

    def appendAttributeFile(self, attributeRef):
        celValue = "getNode('%s').name" % self._getAlembicNode().getName() + " + '//*'"
        addAttributeFileParams(self.__assetParam, attributeRef, celValue)
        BuildScenegraph(self.__node)


class AlembicTreeHandlerBase(ImportomaticAPI.AssetTreeChild):

    def isSelectable(self):
        return True


class ModifierRootHandler(AlembicTreeHandlerBase):

    def __init__(self, node, param):
        self.__node = node
        self.__param = param

    def setItemState(self, item):
        from Katana import UI4
        ScenegraphIconManager = UI4.Util.ScenegraphIconManager
        item.setText(ImportomaticAPI.NAME_COLUMN, 'modifiers')
        item.setText(ImportomaticAPI.TYPE_COLUMN, '')

    def getChildren(self):
        children = []
        for attr in self.__param.getChildren():
            children.append(AttributeFileTreeHandler(self.__node, attr))

        return children


class LookFileTreeHandler(AlembicTreeHandlerBase):

    def __init__(self, node, lookParam):
        self.__node = node
        self.__lookParam = lookParam
        self.__lookName = lookParam.getChild('name').getValue(0)
        self.__hash = lookParam.getChild('_hash').getValue(0)
        self.__allowDelete = self.__lookParam.getChild('_allowDelete').getValue(0)

    def setItemState(self, item):
        from Katana import UI4
        item.setText(ImportomaticAPI.NAME_COLUMN, self.__lookName)
        if self.__allowDelete == 'True':
            item.setText(ImportomaticAPI.TYPE_COLUMN, 'look file override')
        else:
            item.setText(ImportomaticAPI.TYPE_COLUMN, 'look file')
        item.setText(ImportomaticAPI.STATUS_COLUMN, '')

    def getEditor(self, widgetParent):
        handler = ImportomaticAPI.AssetModule.GetHandlerForType(self.__node)
        lookFileAssignNode = findNodeTypeByHash(self.__node, self.__hash, 'LookFileAssign')
        if lookFileAssignNode is None:
            return
        else:
            editor = handler.getEditor(lookFileAssignNode, widgetParent)
            return editor

    def isDeletable(self):
        return self.__allowDelete == 'True'

    def delete(self):
        parent = self.__lookParam.getParent()
        parent.deleteChild(self.__lookParam)
        BuildScenegraph(self.__node)

    def isIgnorable(self):
        return True

    def isIgnored(self):
        return self.__lookParam.getChild('_ignore').getValue(0) == 'True'

    def setIgnored(self, state):
        if state:
            self.__lookParam.getChild('_ignore').setValue('True', 0)
        else:
            self.__lookParam.getChild('_ignore').setValue('False', 0)
        BuildScenegraph(self.__node)


class AttributeFileTreeHandler(AlembicTreeHandlerBase):

    def __init__(self, node, attrParam):
        self.__node = node
        self.__attrParam = attrParam
        self.__attrName = attrParam.getChild('name').getValue(0)
        self.__hash = attrParam.getChild('_hash').getValue(0)
        self.__allowDelete = self.__attrParam.getChild('_allowDelete').getValue(0)

    def setItemState(self, item):
        from Katana import UI4
        ScenegraphIconManager = UI4.Util.ScenegraphIconManager
        IconManager = UI4.Util.IconManager
        item.setText(ImportomaticAPI.NAME_COLUMN, self.__attrName)
        if self.__allowDelete == 'True':
            item.setText(ImportomaticAPI.TYPE_COLUMN, 'attribute file override')
        else:
            item.setText(ImportomaticAPI.TYPE_COLUMN, 'attribute file')
        item.setText(ImportomaticAPI.STATUS_COLUMN, '')

    def getEditor(self, widgetParent):
        handler = ImportomaticAPI.AssetModule.GetHandlerForType(self.__node)
        attrFileInNode = findNodeTypeByHash(self.__node, self.__hash, 'AttributeFile_In')
        if attrFileInNode is None:
            return
        else:
            editor = handler.getEditor(attrFileInNode, widgetParent)
            return editor

    def isDeletable(self):
        return self.__allowDelete == 'True'

    def delete(self):
        modifiersParam = self.__attrParam.getParent()
        modifiersParam.deleteChild(self.__attrParam)
        if modifiersParam.getNumChildren() == 0:
            modifiersParam.getParent().deleteChild(modifiersParam)
        BuildScenegraph(self.__node)

    def isIgnorable(self):
        return True

    def isIgnored(self):
        return self.__attrParam.getChild('_ignore').getValue(0) == 'True'

    def setIgnored(self, state):
        if state:
            self.__attrParam.getChild('_ignore').setValue('True', 0)
        else:
            self.__attrParam.getChild('_ignore').setValue('False', 0)
        BuildScenegraph(self.__node)
