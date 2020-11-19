import logging
log = logging.getLogger("ArnoldAOVs")


try:
    import v1 as ArnoldAOVs
except Exception as exception:
    log.exception("Error importing Super Tool Python package: {}".format(str(exception)))
else:
    PluginRegistry = [
        ('SuperTool', 2, 'ArnoldAOVs', (
            ArnoldAOVs.ArnoldAOVsNode,
            ArnoldAOVs.GetEditor
        ))
    ]