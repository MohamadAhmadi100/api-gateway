def add_attribute_to_assignee(item: dict, attr_name: str):
    return {
            "attribute": {
                "action": "add_attribute_to_assignee",
                "body": {
                    "item": item,
                    "attr_name": attr_name
                }
            }
        }


def get_all_attributes_by_assignee(name: str):
    return {
            "attribute": {
                "action": "get_all_attributes_by_assignee",
                "body": {
                    "name": name,
                }
            }
        }


def delete_attribute_from_assignee(attr_name: str, name: str):
    return {
            "attribute": {
                "action": "delete_attribute_from_assignee",
                "body": {
                    "attr_name": attr_name,
                    "name": name
                }
            }
        }


def get_all_assignees():
    return {
            "attribute": {
                "action": "get_all_assignees",
                "body": {
                }
            }
        }


