from Katana import Callbacks
import logging


global customNewFile
global setDefaultSettings
global replaceNewAction


def customNewFile():
    import KatanaFile
    KatanaFile.New()
    setDefaultSettings()


def replaceNewAction():
    from UI4.App import MainWindow, MainMenu
    from Katana import QtWidgets, QtGui, QtCore
    window = MainWindow.CurrentMainWindow()
    if not window:
        return

    mainMenu = window.findChild(MainMenu.MainMenu)

    fileMenu = None

    menus = mainMenu.findChildren(QtWidgets.QMenu)

    for menu in menus:
        if menu.title() == "File":
            fileMenu = menu
            break

    if not fileMenu:
        return

    newAction = fileMenu.actions()[0]
    beforeAction = fileMenu.actions()[1]
    fileMenu.removeAction(newAction)
    newAction.deleteLater()

    cmtNewAction = fileMenu.addAction("New")
    fileMenu.removeAction(cmtNewAction)
    fileMenu.insertAction(beforeAction, cmtNewAction)
    cmtNewAction.triggered.connect(customNewFile)


def setDefaultSettings():
    import NodegraphAPI

    # Setup Default Graph State Variables
    for var in ['job', 'seq', 'shot', 'renderPass']:
        options = ('',)

        variablesGroup = NodegraphAPI.GetRootNode().getParameter('variables')
        variableParam = variablesGroup.createChildGroup(var)
        variableParam.createChildNumber('enable', 1)
        variableParam.createChildString('value', options[0])
        optionsParam = variableParam.createChildStringArray('options', len(options))
        for optionParam, optionValue in zip(optionsParam.getChildren(), options):
                optionParam.setValue(optionValue, 0)

    # Setup Default Project Settings
    rootNode = NodegraphAPI.GetRootNode()
    inTime, outTime = rootNode.getParameter('inTime'), rootNode.getParameter('outTime')
    workingInTime, workingOutTime = rootNode.getParameter('workingInTime'), rootNode.getParameter('workingOutTime')
    currentTime = rootNode.getParameter('currentTime')
    resolution = rootNode.getParameter('resolution')

    inValue = 1001
    outValue = 1100
    inTime.setValue(inValue, 0)
    outTime.setValue(outValue, 0)
    workingInTime.setValue(inValue, 0)
    workingOutTime.setValue(outValue, 0)
    currentTime.setValue(inValue, 0)
    resolution.setValue("2560x1440", 0)


def onStartupComplete(**kwargs):

    log = logging.getLogger("Comet Startup")

    # setDefaultSettings()
    # replaceNewAction()


log = logging.getLogger("Startup Example")
log.info("Registering onStartupComplete callback...")
Callbacks.addCallback(Callbacks.Type.onStartupComplete, onStartupComplete)