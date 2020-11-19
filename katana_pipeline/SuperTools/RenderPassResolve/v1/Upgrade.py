__all__ = ['Upgrade']


from Katana import NodegraphAPI, Utils
import logging

log = logging.getLogger("RenderPassResolve")


def Upgrade(node):
    Utils.UndoStack.DisableCapture()
    try:
        pass
        # This is where you would detect an out-of-date version:
        #    node.getParameter('version')
        # and upgrade the internal network.
    except Exception as exception:
        log.exception('Error upgrading RenderPassResolve node "%s": %s'
                      % (node.getName(), str(exception)))
    finally:
        Utils.UndoStack.EnableCapture()
