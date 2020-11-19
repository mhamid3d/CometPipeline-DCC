from cometqt.widgets.ui_entity_viewer import EntityPickerDialog
from qtpy import QtWidgets
import os


def entityPickerRun():
    ent = EntityPickerDialog()
    ent.resize(450, 600)
    result = ent.exec_()

    if result == QtWidgets.QDialog.Rejected:
        return

    selection = ent.getSelection()
    if selection:
        entityObject = selection[0].dataObject
        jobObject = ent.entityViewer.currentJob()

        if jobObject:
            os.environ['SHOW'] = jobObject.get("label")
        if entityObject:
            os.environ['SHOT'] = entityObject.get("label")

        if jobObject and entityObject:
            from cometmaya.scripts import configure_scene_for_entity
            configure_scene_for_entity(jobObject, entityObject)