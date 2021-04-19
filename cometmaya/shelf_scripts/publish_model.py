from cometpublish.ui import ui_version_publisher as uvp
from cometqt.widgets.ui_screengrab import ScreenShotTool
from mongorm import util as mgutil
import shutil
import mongorm
import maya.cmds as mc
import os


def publish_model(**kwargs):

    publishGroup = mc.ls(sl=True)[0]

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

    mc.select(publishGroup)

    abcExportCommand = "-frameRange {currentFrame} {currentFrame} -uvWrite -worldSpace -writeUVSets -dataFormat ogawa -root {rootObject} -file {filePath}".format(
        rootObject=str(mc.ls(sl=True)[0]),
        filePath=alembicContentObject.get("path"),
        currentFrame=int(mc.currentTime(query=True))
    )

    mc.AbcExport(j=abcExportCommand)
    mc.file(mayaBinaryContentObject.get("path"), type="mayaBinary", ea=True)

    mc.select(d=True)
    screenShotTool = ScreenShotTool(format='png', parent=None)
    screenShotTool.squareAspectRatio.setDisabled(True)
    result = screenShotTool.exec_()

    src = screenShotTool.outputPath
    dest = "{}/_thumbnail/{}.png".format(entity.get("path"), version.get("label"))
    shutil.move(src, dest)

    version.thumbnail = dest
    version.save()

    return True


class ModelPublishValidator(uvp.ValidationDialog):
    def __init__(self, *args, **kwargs):
        super(ModelPublishValidator, self).__init__(*args, **kwargs)

    def validation_001(self):
        errorMsg = ""
        result = True
        sel = mc.ls(sl=True, dag=True, type=['mesh', 'nurbsSurface'])

        affectedItems = []

        for shape in sel:
            if not str(shape).endswith("_geoShape"):
                affectedItems.append(shape)

        if affectedItems:
            result = False
            errorMsg = "The following geometry do not satisfy the validation:\n{}".format("\n".join(affectedItems))

        return result, errorMsg

    def validation_002(self):
        result = True
        errorMsg = ""
        sel = mc.ls(sl=True, dag=True, type=['mesh', 'nurbsSurface'])

        affectedItems = []

        for shape in sel:
            if not mc.attributeQuery("materialTag", node=shape, exists=True):
                affectedItems.append(shape)

        if affectedItems:
            result = False
            errorMsg = "The following geometry do not satisfy the validation:\n{}".format("\n".join(affectedItems))

        return result, errorMsg

    def validation_003(self):
        result = True
        errorMsg = ""
        sel = mc.ls(sl=True, dag=True, type=['mesh'])

        affectedItems = []

        for shape in sel:
            u, v = mc.polyEvaluate(shape, b2=True)
            un, ux = u
            vn, vx = v
            if (float(un), float(ux), float(vn), float(vx)) == (0.0, 0.0, 0.0, 0.0):
                affectedItems.append(shape)

        if affectedItems:
            result = False
            errorMsg = "The following geometry do not satisfy the validation:\n{}".format("\n".join(affectedItems))

        return result, errorMsg

    def fixer_001(self):
        sel = mc.ls(sl=True, dag=True, type=['mesh', 'nurbsSurface'])

        for shape in sel:
            if not str(shape).endswith("_geoShape"):
                tform = mc.listRelatives(shape, p=True)[0]
                if str(tform).endswith("_geo"):
                    mc.rename(shape, "{}Shape".format(str(tform)))
                else:
                    mc.rename(tform, "{}_geo".format(tform))

    def fixer_003(self):
        sel = mc.ls(sl=True, dag=True, type=['mesh'])

        for shape in sel:
            u, v = mc.polyEvaluate(shape, b2=True)
            un, ux = u
            vn, vx = v
            if (float(un), float(ux), float(vn), float(vx)) == (0.0, 0.0, 0.0, 0.0):
                faceMax = mc.polyEvaluate(shape, face=True) - 1
                mc.polyProjection("{}.f[0:{}]".format(shape, faceMax), ch=True, ibd=True, md="x")

    def setupValidators(self):

        self.installValidator(
            name='Each shape geometry ends withs with "_geo"',
            description='Rename each geo so that it ends with "_geo", the shape should also end with "_geoShape"',
            validator=self.validation_001,
            fixer=self.fixer_001
        )
        self.installValidator(
            name='Each shape has the "CMT_materialTag" attribute',
            description='Each shape should have an attribute titled "CMT_materialTag". If this returns invalid you should open the Material Tag Manager to automate the process on the entire model.',
            validator=self.validation_002
        )
        self.installValidator(
            name='Each shape has proper UVs',
            description="Each shape is required to have valid UV's, even if they are just a simple planar projection.",
            validator=self.validation_003,
            fixer=self.fixer_003
        )


def run_publish_model():
    sel = mc.ls(sl=True)
    if not sel or len(sel) > 1 or mc.listRelatives(sel[0], p=True):
        raise RuntimeError("Please select 1 valid group object to publish")

    win = uvp.VersionPublisher(postProcess=publish_model, validationDialog=ModelPublishValidator)
    win.setCurrentType("MODEL")
    win.setFixedType(True)
    win.setWindowTitle("Publish Model")
    win.show()
