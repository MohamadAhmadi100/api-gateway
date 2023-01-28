def insert_log(data):
    return {
            "log": {
                "action": "insert_log",
                "body": {
                    "data": data,
                }
            }
        }


def get_log(filter_dict, page, per_page):
    return {
            "log": {
                "action": "get_log",
                "body": {
                    "filter_dict": filter_dict,
                    "page": page,
                    "per_page": per_page
                }
            }
        }


def insert_service_names(name, label):
    return {
            "log": {
                "action": "insert_service_names",
                "body": {
                    "name": name,
                    "label": label
                }
            }
        }


def get_service(filter_dict, page, per_page):
    return {
            "log": {
                "action": "get_service",
                "body": {
                    "filter_dict": filter_dict,
                    "page": page,
                    "per_page": per_page
                }
            }
        }


