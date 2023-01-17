def get_link_request(request_service, service_data, link, user_list, method_list):
    return {
        "uis": {
            "action": "get_link_request",
            "body": {
                "request_service": request_service,
                "service_data": service_data,
                "link": link,
                "user_list": user_list,
                "method_list": method_list
            }
        }
    }


def find_links(hashed_link):
    return {
        "uis": {
            "action": "find_links",
            "body": {
                "hashed_link": hashed_link,
            }
        }
    }


def get_data(page, per_page):
    return {
        "uis": {
            "action": "get_data",
            "body": {
                "page": page,
                "per_page": per_page
            }
        }
    }


def hashed_generator(link, customer_type):
    return {
        "uis": {
            "action": "hashed_generator",
            "body": {
                "link": link,
                "customer_type": customer_type
            }
        }
    }
