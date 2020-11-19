aovList = [
    {'AA_inv_density': {'filter': 'heatmap', 'data': 'float'}},
    {'albedo': {'filter': 'None', 'data': 'rgb'}},
    {'background': {'filter': 'None', 'data': 'rgb'}},
    {'coat': {'filter': 'None', 'data': 'rgb'}},
    {'coat_albedo': {'filter': 'None', 'data': 'rgb'}},
    {'coat_direct': {'filter': 'None', 'data': 'rgb'}},
    {'coat_indirect': {'filter': 'None', 'data': 'rgb'}},
    {'cputime': {'filter': 'None', 'data': 'float'}},
    {'crypto_asset': {'filter': 'None', 'data': 'rgb'}},
    {'crypto_material': {'filter': 'None', 'data': 'rgb'}},
    {'crypto_object': {'filter': 'None', 'data': 'rgb'}},
    {'deep': {'filter': 'None', 'data': 'rgb'}},
    {'diffuse': {'filter': 'None', 'data': 'rgb'}},
    {'diffuse_albedo': {'filter': 'None', 'data': 'rgb'}},
    {'diffuse_direct': {'filter': 'None', 'data': 'rgb'}},
    {'diffuse_indirect': {'filter': 'None', 'data': 'rgb'}},
    {'direct': {'filter': 'None', 'data': 'rgb'}},
    {'emission': {'filter': 'None', 'data': 'rgb'}},
    {'highlight': {'filter': 'None', 'data': 'rgb'}},
    {'ID': {'filter': 'closest', 'data': 'uint'}},
    {'indirect': {'filter': 'None', 'data': 'rgb'}},
    {'motionvector': {'filter': 'None', 'data': 'rgb'}},
    {'N': {'filter': 'closest', 'data': 'vector'}},
    {'opacity': {'filter': 'None', 'data': 'rgb'}},
    {'P': {'filter': 'closest', 'data': 'vector'}},
    {'Pref': {'filter': 'closest', 'data': 'rgb'}},
    {'raycount': {'filter': 'None', 'data': 'float'}},
    {'RGBA': {'filter': 'None', 'data': 'rgba'}},
    {'rim_light': {'filter': 'None', 'data': 'rgb'}},
    {'shadow': {'filter': 'None', 'data': 'rgb'}},
    {'shadow_diff': {'filter': 'None', 'data': 'rgb'}},
    {'shadow_mask': {'filter': 'None', 'data': 'rgb'}},
    {'shadow_matte': {'filter': 'None', 'data': 'rgba'}},
    {'sheen': {'filter': 'None', 'data': 'rgb'}},
    {'sheen_albedo': {'filter': 'None', 'data': 'rgb'}},
    {'sheen_direct': {'filter': 'None', 'data': 'rgb'}},
    {'sheen_indirect': {'filter': 'None', 'data': 'rgb'}},
    {'specular': {'filter': 'None', 'data': 'rgb'}},
    {'specular_albedo': {'filter': 'None', 'data': 'rgb'}},
    {'specular_direct': {'filter': 'None', 'data': 'rgb'}},
    {'specular_indirect': {'filter': 'None', 'data': 'rgb'}},
    {'sss': {'filter': 'None', 'data': 'rgb'}},
    {'sss_albedo': {'filter': 'None', 'data': 'rgb'}},
    {'sss_direct': {'filter': 'None', 'data': 'rgb'}},
    {'sss_indirect': {'filter': 'None', 'data': 'rgb'}},
    {'transmission': {'filter': 'None', 'data': 'rgb'}},
    {'transmission_albedo': {'filter': 'None', 'data': 'rgb'}},
    {'transmission_direct': {'filter': 'None', 'data': 'rgb'}},
    {'transmission_indirect': {'filter': 'None', 'data': 'rgb'}},
    {'volume': {'filter': 'None', 'data': 'rgb'}},
    {'volume_albedo': {'filter': 'None', 'data': 'rgb'}},
    {'volume_direct': {'filter': 'None', 'data': 'rgb'}},
    {'volume_indirect': {'filter': 'None', 'data': 'rgb'}},
    {'volume_opacity': {'filter': 'None', 'data': 'rgb'}},
    {'volume_Z': {'filter': 'closest', 'data': 'float'}},
    {'Z': {'filter': 'closest', 'data': 'float'}},
    {'light_grp0': {'filter': 'None', 'data': 'rgb', 'lpe': "C.*<L.'0'>"}},
    {'light_grp1': {'filter': 'None', 'data': 'rgb', 'lpe': "C.*<L.'1'>"}},
    {'light_grp2': {'filter': 'None', 'data': 'rgb', 'lpe': "C.*<L.'2'>"}},
    {'light_grp3': {'filter': 'None', 'data': 'rgb', 'lpe': "C.*<L.'3'>"}},
    {'light_grp4': {'filter': 'None', 'data': 'rgb', 'lpe': "C.*<L.'4'>"}},
    {'light_grp5': {'filter': 'None', 'data': 'rgb', 'lpe': "C.*<L.'5'>"}},
    {'light_grp6': {'filter': 'None', 'data': 'rgb', 'lpe': "C.*<L.'6'>"}},
    {'light_grp7': {'filter': 'None', 'data': 'rgb', 'lpe': "C.*<L.'7'>"}},
    {'light_grp8': {'filter': 'None', 'data': 'rgb', 'lpe': "C.*<L.'8'>"}},
    {'light_grp9': {'filter': 'None', 'data': 'rgb', 'lpe': "C.*<L.'9'>"}},
    {'matte_grp0': {'filter': 'None', 'data': 'rgb'}},
    {'matte_grp1': {'filter': 'None', 'data': 'rgb'}},
    {'matte_grp2': {'filter': 'None', 'data': 'rgb'}},
    {'matte_grp3': {'filter': 'None', 'data': 'rgb'}},
    {'matte_grp4': {'filter': 'None', 'data': 'rgb'}},
    {'matte_grp5': {'filter': 'None', 'data': 'rgb'}},
    {'matte_grp6': {'filter': 'None', 'data': 'rgb'}},
    {'matte_grp7': {'filter': 'None', 'data': 'rgb'}},
    {'matte_grp8': {'filter': 'None', 'data': 'rgb'}},
    {'matte_grp9': {'filter': 'None', 'data': 'rgb'}}
]


def deleteNode(node):

    nodeParent = node.getParent()

    nodeInput = node.getInputPortByIndex(0).getConnectedPort(0)
    nodeOutput = node.getOutputPortByIndex(0).getConnectedPort(0)

    if nodeInput and nodeOutput:
        in_node = nodeInput.getNode()
        out_node = nodeOutput.getNode()

        nodeInput.connect(nodeOutput)

    node.delete()