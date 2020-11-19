import logging
log = logging.getLogger("RenderPassResolve")


try:
    import v1 as RenderPassResolve
except Exception as exception:
    log.exception("Error importing Super Tool Python package: {}".format(str(exception)))
else:
    PluginRegistry = [
        ('SuperTool', 2, 'RenderPassResolve', (
            RenderPassResolve.RenderPassResolveNode,
            RenderPassResolve.GetEditor
        ))
    ]