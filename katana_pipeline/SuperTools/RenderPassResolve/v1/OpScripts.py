def collection_create_script():
    return """local renderPassLocation = Interface.GetOpArg("user.renderPass"):getValue()
local attrList = {'camera_objects', 'trace_objects', 'light_objects', 'matte_objects', 'prune_objects'}
for attrCount = 1, 5 do
    attrName = 'renderPass.visibility.' .. attrList[attrCount]
    attr = Interface.GetGlobalAttr(attrName, renderPassLocation)
    if attr == nil then
        attr = StringAttribute("")
    end
    Interface.SetAttr('collections.' .. attrList[attrCount] .. '.cel', attr)
end
"""