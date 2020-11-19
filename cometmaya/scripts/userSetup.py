from cometmaya.ui.base_shelf import BaseShelf
from pipeicon import icon_paths
from pipeicon.util import fullIconPath
import maya.cmds as mc
import os

# Shelf script imports
from cometmaya.shelf_scripts.entity_picker import entityPickerRun
from cometmaya.shelf_scripts.model_create import run as model_create_run


mc.evalDeferred('initialize_maya()')
mc.evalDeferred('CometShelf()')


def initialize_maya():
    import mongorm
    from cometmaya.scripts import configure_scene_for_entity

    handler = mongorm.getHandler()
    filt = mongorm.getFilter()
    job, entity = os.getenv("SHOW"), os.getenv("SHOT")
    filt.search(handler['entity'], job=job, label=entity)
    entityObject = handler['entity'].one(filt)
    filt.clear()

    filt.search(handler['job'], label=job)
    jobObject = handler['job'].one(filt)
    filt.clear()

    configure_scene_for_entity(jobObject, entityObject)


class CometShelf(BaseShelf):
    def __init__(self, name='Comet'):
        BaseShelf.__init__(self, name)

    def build(self):
        self.addButton(label='Set Entity', icon=fullIconPath(icon_paths.ICON_SHOT_LRG), command='entityPickerRun()')
        self.addSeparator()
        self.addButton(label='Create Model', icon=fullIconPath(icon_paths.ICON_ASSET_LRG), command='mcr = model_create_run()')
