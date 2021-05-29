from cometqt.widgets.ui_entity_viewer import EntityPickerDialog
from qtpy import QtWidgets
import qdarkstyle
import os


def entityPickerRun():
    ent = EntityPickerDialog()
    ent.setStyleSheet(qdarkstyle.load_stylesheet_pyside2())
    ent.resize(450, 600)
    result = ent.exec_()

    if result == QtWidgets.QDialog.Rejected:
        return

    jobObject = ent.entityViewer.currentJob()
    entityObject = ent.getSelection()

    if entityObject and len(entityObject) > 0:
        entityObject = entityObject[0]
    else:
        entityObject = None

    if jobObject:
        os.environ['SHOW'] = jobObject.get("label")
    if entityObject:
        os.environ['SHOT'] = entityObject.get("label")

    if jobObject and entityObject:
        from cometmaya.scripts import configure_scene_for_entity
        configure_scene_for_entity(jobObject, entityObject)