import os
from Node import ImportomaticNode
import logging

log = logging.getLogger('Importomatic.__init__')


def GetImportomaticEditor():
    from Editor import ImportomaticEditor
    return ImportomaticEditor


from Katana import Plugins, ResourceFiles, Utils


def _ParseVersion(version):
    try:
        return tuple(map(int, version.split('.')))
    except (ValueError, AttributeError):
        return (0, 0, 0)


def _PickHighestPlugins(plugins, appVersion):
    outPlugins = []
    versionedPlugins = {}
    zeros = (0, 0)
    for p in plugins:
        kVer = _ParseVersion(p.apinum)
        splitName = p.name.split('#')
        name = splitName[0]
        try:
            pVer = int(splitName[(-1)])
        except ValueError:
            pVer = 0

        if kVer <= appVersion:
            if versionedPlugins.get(name, zeros)[0] <= pVer:
                versionedPlugins[name] = (
                    pVer, p)

    for name, (pVer, plugin) in versionedPlugins.iteritems():
        plugin.fullname = plugin.name
        plugin.name = name
        outPlugins.append(plugin)

    return outPlugins


from Katana import Plugins
import Katana
import os


def InitializePlugin():
    try:
        from Katana import QtWidgets
        guiMode = not QtWidgets.QApplication.startingUp() and isinstance(QtWidgets.QApplication.instance(),
                                                                         QtWidgets.QApplication)
    except ImportError:
        guiMode = False

    if not hasattr(Plugins, 'ImportomaticAPI'):
        import ImportomaticAPI
        Plugins.ImportomaticAPI = ImportomaticAPI
    searchPath = ResourceFiles.GetSearchPaths('Importomatic')
    searchPathOld = ResourceFiles.GetSearchPaths('ImportomaticModules2')
    if searchPathOld:
        searchPath.extend(searchPathOld)
    searchPath.reverse()
    searchPath.append(os.path.abspath(os.path.join(__file__, os.pardir, "plugins")))
    plugins = _PickHighestPlugins(Utils.Plugins.Load('ImportomaticModule', None, searchPath), Katana.version)
    for plugin in plugins:
        try:
            data = plugin.data
            if isinstance(data, tuple):
                if len(data) == 2:
                    if guiMode:
                        data[0]()
                        data[1]()
                    else:
                        data[0]()
            elif guiMode:
                data()
        except Exception as e:
            log.warning("ImportomaticPlugin Error For '%s' %s" % (plugin.name, e), exc_info=True)

    return


InitializePlugin()
