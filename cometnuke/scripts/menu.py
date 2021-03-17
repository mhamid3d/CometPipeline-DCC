from cometnuke.panels.shot_set import ShotSetWidget
from nukescripts import panels
import nuke


def configure_panels():
    panels.registerWidgetAsPanel('ShotSetWidget', 'Shot Set', 'cometnuke.panels.shot_set.ShotSetWidget')


configure_panels()