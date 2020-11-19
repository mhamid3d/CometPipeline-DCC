def pass_location_script():
    return """local passRootLocation = Interface.GetOpArg("user.passRootLocation"):getValue()
local enablePass = tonumber(Interface.GetOpArg("user.enablePass"):getValue())
local prefix = Interface.GetOpArg("user.prefix"):getValue()
local label = Interface.GetOpArg("user.label"):getValue()
local layer = Interface.GetOpArg("user.layer"):getValue()
local type = Interface.GetOpArg("user.type"):getValue()

local passLocation = passRootLocation .. "/" .. prefix .. "_" .. label .. "_" .. layer .. "_" .. type

if Interface.GetInputLocationPath() == "/root" then
    local sscb = OpArgsBuilders.StaticSceneCreate(true)
    sscb:createEmptyLocation(passLocation, "pass")
    sscb:setAttrAtLocation(passLocation, "visible", IntAttribute(enablePass, 1))

    Interface.ExecOp("StaticSceneCreate", sscb:build())
end
"""
