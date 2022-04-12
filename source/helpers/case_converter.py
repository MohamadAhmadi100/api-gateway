import re


# convert snake_case to camelCase
def snake_to_camel(snake_str):
    components = snake_str.split('_')
    return components[0] + ''.join(x.title() for x in components[1:])


# convert camelCase to snake_case
def camel_to_snake(camel_str):
    return re.sub(r'(?<!^)(?=[A-Z])', '_', camel_str).lower()


# converting all keys of dict to camelCase or sanke_case
def convert_case(dict_data, action):
    function = camel_to_snake if action == 'snake' else snake_to_camel
    new_dict = {}
    if isinstance(dict_data, dict):
        for key, value in dict_data.items():
            if isinstance(value, dict):
                new_value = convert_case(value, action)
                new_key = function(key) if key not in ['B2B', 'B2C', 'B2G'] else key
                new_dict[new_key] = new_value
            elif isinstance(value, list):
                new_list = []
                for item in value:
                    new_value = convert_case(item, action)
                    new_list.append(new_value)
                new_key = function(key)
                new_dict[new_key] = new_list
            else:
                new_key = function(key)
                new_dict[new_key] = value
        return new_dict
    if isinstance(dict_data, list):
        new_list = []
        for item in dict_data:
            new_value = convert_case(item, action)
            new_list.append(new_value)
        return new_list
    return dict_data

