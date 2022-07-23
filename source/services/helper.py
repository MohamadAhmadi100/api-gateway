import os
import ast
import sys


def helper():
    path = os.getcwd() + "/source/services"
    folders = [f for f in os.listdir(path)]
    folders.remove("helper.py")
    folders.remove("__init__.py")
    folders.remove("__pycache__")

    for folder in folders:
        new_files = dict()
        current_path = path + "/" + folder
        files = [current_path + "/" + f for f in os.listdir(path + "/" + folder) if f.endswith(".py")]
        if current_path + "/" + "__init__.py" in files:
            files.remove(current_path + "/" + "__init__.py")
        for file in files:
            with open(file) as f:
                text = f.read()
                parsed_file = ast.parse(text)
                # class_name = [node.name for node in ast.walk(parsed_file) if isinstance(node, ast.ClassDef)][0]
                methods = [node for node in ast.walk(parsed_file) if isinstance(node, ast.FunctionDef)]
                text = ""
                for method in methods:
                    method_name = method.name
                    method_argument = [a.arg for a in method.args.args]
                    method_types = [a.annotation.id if a.annotation else None for a in method.args.args]
                    text += f"def {method_name}("
                    for i in range(len(method_argument)):
                        text += f"{method_argument[i]}"
                        text += f": {method_types[i]}, " if method_types[i] is not None else ", "
                    text = text[:-2] if len(method_argument) > 0 else text
                    text += "):\n    "
                    text += 'return {\n            "' + folder + '": {\n                "action": "'
                    text += method_name + '",\n                "body": {'
                    for i in range(0, len(method_argument)):
                        text += '\n                    "' + method_argument[i] + '": ' + method_argument[i] + ','
                    text = text[:-1] if len(method_argument) > 1 else text
                    text += "\n                }\n            }\n        }\n"
                    text += "\n\n"
                new_files[file] = text
        for key, value in new_files.items():
            with open(key, 'w') as f:
                f.write(value)


gettrace = getattr(sys, 'gettrace', None)
print(os.path.abspath(""))
try:
    helper()
except Exception as e:
    print(f"helper doesn't work...{e}")
# if gettrace is None:
#     helper()
