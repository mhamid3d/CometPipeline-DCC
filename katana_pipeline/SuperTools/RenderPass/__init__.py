import logging
log = logging.getLogger("RenderPass")


try:
    import v1 as RenderPass
except Exception as exception:
    log.exception("Error importing Super Tool Python package: {}".format(str(exception)))
else:
    PluginRegistry = [
        ('SuperTool', 2, 'RenderPass', (
            RenderPass.RenderPassNode,
            RenderPass.GetEditor
        ))
    ]