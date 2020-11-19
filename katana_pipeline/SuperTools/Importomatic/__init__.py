import Katana

Importomatic = None
import Importomatic17 as Importomatic

if Importomatic:
    PluginRegistry = [
        ('SuperTool', 2, 'Importomatic',
         (
             Importomatic.ImportomaticNode, Importomatic.GetImportomaticEditor))]
