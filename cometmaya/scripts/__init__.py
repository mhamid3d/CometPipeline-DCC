import os
import maya.cmds as mc


def configure_scene_for_entity(jobObject, entityObject):
    inValue = 1001
    outValue = 1101
    resXValue = 1920
    resYValue = 1080
    pixelAspectValue = 1.0

    if entityObject:
        framerange = entityObject.get("framerange")
        if framerange:
            inValue = framerange[0]
            outValue = framerange[1]

    if jobObject:
        res = jobObject.get("resolution")
        resXValue = res[0]
        resYValue = res[1]
        pixelAspectValue = res[2]

    mc.playbackOptions(min=inValue, max=outValue, ast=inValue, aet=outValue)
    mc.currentTime(inValue)

    mc.setAttr("defaultResolution.width", resXValue)
    mc.setAttr("defaultResolution.height", resYValue)
    mc.setAttr("defaultResolution.pixelAspect", pixelAspectValue)