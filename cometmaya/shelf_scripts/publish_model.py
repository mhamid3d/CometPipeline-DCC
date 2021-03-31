from cometpublish.ui import ui_version_publisher as uvp
from mongorm import util as mgutil
from qtpy import QtWidgets, QtGui, QtCore
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


class ModelPublishValidator(uvp.ValidationDialog):
    def __init__(self, *args, **kwargs):
        super(ModelPublishValidator, self).__init__(*args, **kwargs)

    def validation_001(self):
        sel = mc.ls(sl=True, dag=True, type=['mesh', 'nurbsSurface'])

        for shape in sel:
            if not str(shape).endswith("_geoShape"):
                return False

        return True

    def validation_002(self):
        sel = mc.ls(sl=True, dag=True, type=['mesh', 'nurbsSurface'])

        for shape in sel:
            if not mc.attributeQuery("materialTag", node=shape, exists=True):
                return False

        return True

    def validation_003(self):
        sel = mc.ls(sl=True, dag=True, type=['mesh'])

        for shape in sel:
            u, v = mc.polyEvaluate(shape, b2=True)
            un, ux = u
            vn, vx = v
            if (float(un), float(ux), float(vn), float(vx)) == (0.0, 0.0, 0.0, 0.0):
                return False

        return True

    def setupValidators(self):

        self.validatorMap = {
            'Each shape geometry ends withs with "_geo"': {
                'result': False,
                'treeItem': None,
                'errorMsg': None,
                'description': None,
                'validator': self.validation_001
            },
            'Each shape has the "materialTag" attribute': {
                'result': False,
                'treeItem': None,
                'errorMsg': None,
                'description': None,
                'validator': self.validation_002
            },
            'Each shape has proper UVs': {
                'result': False,
                'treeItem': None,
                'errorMsg': None,
                'description': None,
                'validator': self.validation_003
            }
        }

        for validationTask, payload in self.validatorMap.items():
            item = QtWidgets.QTreeWidgetItem(self.validationTree)
            item.setText(0, validationTask)
            self.validatorMap[validationTask]['treeItem'] = item

def run_publish_model():
    sel = mc.ls(sl=True)
    if not sel or len(sel) > 1 or mc.listRelatives(sel[0], p=True):
        raise RuntimeError("Please select 1 valid group object to publish")

    win = uvp.VersionPublisher(postProcess=publish_model, validationDialog=ModelPublishValidator)
    win.setCurrentType("MODEL")
    win.setFixedType(True)
    win.setWindowTitle("Publish Model")
    win.show()
