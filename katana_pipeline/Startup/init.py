from Katana import Callbacks


def onStartupComplete(**kwargs):
    import mongorm
    import NodegraphAPI
    import os

    handler = mongorm.getHandler()
    filt = mongorm.getFilter()
    job, entity = os.getenv("SHOW"), os.getenv("SHOT")
    filt.search(handler['entity'], job=job, label=entity)
    entityObject = handler['entity'].one(filt)
    filt.clear()

    filt.search(handler['job'], label=job)
    jobObject = handler['job'].one(filt)
    filt.clear()

    inValue = 1001
    outValue = 1100
    resolutionValue = "2560x1440"
    entityName = ""

    if entityObject:
        if entityObject.get("framerange"):
            inValue = entityObject.get("framerange")[0]
            outValue = entityObject.get("framerange")[1]
        resolutionValue = "{}x{}".format(jobObject.get("resolution")[0], jobObject.get("resolution")[1])
        entityName = str(entityObject.get("label"))

    # Setup Default Graph State Variables
    for var in ['shot', 'renderPass']:
        options = ('',)

        if entityName and var == 'shot':
            options = (entityName,)

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

    inTime.setValue(inValue, 0)
    outTime.setValue(outValue, 0)
    workingInTime.setValue(inValue, 0)
    workingOutTime.setValue(outValue, 0)
    currentTime.setValue(inValue, 0)
    resolution.setValue(resolutionValue, 0)


Callbacks.addCallback(Callbacks.Type.onStartupComplete, onStartupComplete)
