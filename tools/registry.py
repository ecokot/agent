# tools/registry.py
TOOL_REGISTRY = {}


def register_tool(function, schema):
    TOOL_REGISTRY[function.__name__] = {
        "schema": schema,
        "function": function,
    }


def get_tools(names):
    tools = []
    functions = {}

    for name in names:
        item = TOOL_REGISTRY.get(name)
        if item is None:
            raise ValueError(f"Инструмент не найден: {name}")

        tools.append(item["schema"])
        functions[name] = item["function"]

    return tools, functions