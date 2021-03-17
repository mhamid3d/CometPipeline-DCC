import nuke
import mongorm
import os

# Configure Default Values
nuke.knobDefault("Root.colorManagement", "OCIO")
nuke.knobDefault("Root.lock_range", "1")


def resolution_and_range_startup():
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
    outValue = 1101
    resolutionValue = None

    if entityObject:
        if entityObject.get("framerange"):
            inValue = entityObject.get("framerange")[0]
            outValue = entityObject.get("framerange")[1]
        resolutionValue = jobObject.get("resolution")


    # Setup Default Project Settings
    nuke.knobDefault('Root.first_frame', str(inValue))
    nuke.knobDefault('Root.last_frame', str(outValue))
    nuke.frame(inValue)
    cometDefaultFormat = '2560 1440 Comet Default Working'
    nuke.addFormat(cometDefaultFormat)
    nuke.knobDefault('Root.format', 'Comet Default Working')

    if resolutionValue and jobObject:
        formatName = "{} Working".format(jobObject.get("label"))
        showDefaultFormat = '{} {} {} {}'.format(resolutionValue[0], resolutionValue[1], resolutionValue[2], formatName)
        nuke.addFormat(showDefaultFormat)
        nuke.knobDefault('Root.format', formatName)

resolution_and_range_startup()