from langgraph.prebuilt import create_react_agent

from file_manager import (get_file_path_from_user, read_python_files,
                          write_test_python_module)
from helper import clean_python_code, get_relative_source_path
from models import bedrock_model as model
from prompts import system_prompt, user_prompt
from tools import validation_tools


def main() -> None:
    graph = create_react_agent(
        model, tools=validation_tools, state_modifier=system_prompt, debug=True
    )

    python_module_path = get_file_path_from_user("Enter the path to the Python modules: ")
    test_module_path = get_file_path_from_user(
        "Enter the path where the test modules should be stored: "
    )

    python_modules = read_python_files(python_module_path)
    relative_source_path = get_relative_source_path(python_module_path, test_module_path)
    for module_name, code in python_modules.items():
        response = graph.invoke(
            {"messages": [("user", user_prompt(relative_source_path, module_name, code))]}
        )
        write_test_python_module(
            clean_python_code(response["messages"][-1].content),
            f"{test_module_path}/test_{module_name}.py",
        )

if __name__ == "__main__":
    main()
