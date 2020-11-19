from Katana import (
    NodegraphAPI
)


def add_node_reference_param(dest_node, dest_node_param_name, node):
    """
    """
    # Get or create the parameter on the given node
    dest_node_param = dest_node.getParameter(dest_node_param_name)

    if not dest_node_param:
        dest_node_param = dest_node.getParameters().createChildString(dest_node_param_name, "")

    # Set the expression to point to the node name
    dest_node_param.setExpression("getNode('{node_name}').getNodeName()".format(node_name=node.getName()))


def get_reference_node(node, key):
    """
    """
    parameter = node.getParameter("node_" + key)

    if not parameter:
        return None

    return NodegraphAPI.GetNode(parameter.getValue(0))
