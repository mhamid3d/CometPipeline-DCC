from cometpublish.ui import ui_version_publisher as uvp
from mongorm import util as mgutil
import mongorm
import maya.cmds as mc
import os


def publish_model(**kwargs):
    package = kwargs.get("packageObject")
    version = kwargs.get("versionObject")
    entity = kwargs.get("entityObject")

    handler = mongorm.getHandler()

    alembicContentObject = handler['content'].create(
        label="alembic",
        created_by=mgutil.getCurrentUser().getUuid(),
        parent_uuid=version.getUuid(),
        job=version.get("job"),
        path=os.path.abspath(os.path.join(version.get("path"), "{}.abc".format(version.get("label")))),
        format="abc"
    )

    mayaBinaryContentObject = handler['content'].create(
        label="main",
        created_by=mgutil.getCurrentUser().getUuid(),
        parent_uuid=version.getUuid(),
        job=version.get("job"),
        path=os.path.abspath(os.path.join(version.get("path"), "{}.mb".format(version.get("label")))),
        format="mb"
    )

    alembicContentObject.save()
    mayaBinaryContentObject.save()

    abcExportCommand = "-frameRange {currentFrame} {currentFrame} -uvWrite -worldSpace -writeUVSets -dataFormat ogawa -root {rootObject} -file {filePath}".format(
        rootObject=str(mc.ls(sl=True)[0]),
        filePath=alembicContentObject.get("path"),
        currentFrame=int(mc.currentTime(query=True))
    )

    mc.AbcExport(j=abcExportCommand)
    mc.file(mayaBinaryContentObject.get("path"), type="mayaBinary", ea=True)

    return True


def run_publish_model():
    sel = mc.ls(sl=True)
    if not sel or len(sel) > 1 or mc.listRelatives(sel[0], p=True):
        raise RuntimeError("Please select 1 valid group object to publish")

    win = uvp.VersionPublisher()
    win.setCurrentType("MODEL")
    win.setFixedType(True)
    win.setWindowTitle("Publish Model")
    win.post_process = publish_model
    win.show()
