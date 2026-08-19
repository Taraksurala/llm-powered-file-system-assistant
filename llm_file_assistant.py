from fs_tools import (
    read_file,
    list_files,
    write_file,
    search_in_file
)

import json
import os
from openai import OpenAI 
from dotenv import load_dotenv

load_dotenv()
MAX_ITERATIONS = 10
read_file_tool_definition = {
    "type": "function",
    "function": {
        "name": "read_file",
        "description": (
            "Read a PDF, TXT, or DOCX file and extract its text and metadata"
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "filepath": {
                    "type":"string"
                }
            },
            "required":["filepath"]
        }
    },
}

list_files_tool_definition = {
       "type": "function",
        "function": {
            "name": "list_files",
            "description": (
                "List files directly inside a directory and "
                "optionally filter them by file extension."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "filepath": {
                        "type":"string"
                    },
                    "extension": {
                        "type":"string"
                    }
                },
                "required":["filepath"]
            }
        },
}


search_in_file_tool_definition = {
        "type": "function",
        "function": {
            "name": "search_in_file",
            "description": (
                "Search for a keyword inside a PDF, DOCX, or TXT file and return matching occurrences with surrounding context."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "filepath": {
                        "type":"string"
                    },
                    "keyword": {
                        "type":"string"
                    }
                },
                "required":["filepath", "keyword"]
            }
        },
}


write_file_tool_definition = {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": (
                "Creates and Writes content into a new file and also created parent directory if required."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "filepath": {
                        "type":"string"
                    },
                    "content": {
                        "type":"string"
                    }
                },
                "required":["filepath", "content"]
            }
        },
}


tools = [
    read_file_tool_definition,
    list_files_tool_definition,
    search_in_file_tool_definition,
    write_file_tool_definition,
]

tool_map = {
    "read_file": read_file,
    "list_files": list_files,
    "search_in_file": search_in_file,
    "write_file": write_file,
}

def execute_tool(tool_name: str, raw_arguments: str) -> dict:
    tool_function = tool_map.get(tool_name)

    
    if not tool_function:
        return {"success": False, "message": 'Tool does not exist'}
    else:
        try:
            args = json.loads(raw_arguments)

            result = tool_function(**args)

            return result

        except json.JSONDecodeError as jerror:
            return {"success": False, "message": f"Unable to decode the JSON {jerror}"}
        except Exception as e:
            return {"success": False, "message": f"Unexpected error while calling tool: {str(e)}"}


def ask_llm_file_assistant(question: str):

    MODEL_NAME = "openai/gpt-4o-mini"

    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=os.environ["OPENROUTER_API_KEY"],
    )


    print(f"✅ Client initialized with model: {MODEL_NAME}")

    system_message = """
        You are a file-system AI assistant.

        Read the user's request and choose the appropriate available tool.

        When the user asks you to search across files in a directory:
        1. First list the files in the directory.
        2. Use the actual file paths returned by the list_files tool.
        3. Then search the relevant files.
        4. Never invent file names or paths.

        Use tools to list, read, search, or write files.
        If no tool is required, respond directly to the user.
        """

    messages_ = [
        {
            "role": "system",
            "content": system_message,
        },
        {
            "role": "user",
            "content": question,
        },
    ]


    while True:

        basic_response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages_,
            tools=tools,
            tool_choice="auto",
            temperature=0.2,
            top_p=0.9,
            max_tokens=300
        )

        assistant_message = basic_response.choices[0].message

        if not assistant_message.tool_calls:
            return assistant_message.content 
        

        # tool_results = []

        messages_.append(assistant_message)

        for tool_call in assistant_message.tool_calls:

            # tool_call_current = tool_call

            tool_name = tool_call.function.name
            raw_arguments = tool_call.function.arguments

            tool_result = execute_tool(
                tool_name=tool_name, 
                raw_arguments=raw_arguments
            )

            # print(f"Tool name: {tool_name}")
            # print(f"raw_arguments: {raw_arguments}")
            # print(f"Tool result: {tool_result}")


            # tool_results.append(tool_result)

            # Add the tool result
            messages_.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps(tool_result),
                }
            )

    # print(assistant_message)
    # print(tool_result)
        
    # Second LLM call to generate a human-readable answer
    # final_response = client.chat.completions.create(
    #     model=MODEL_NAME,
    #     messages=messages_,
    #     tools=tools,
    #     tool_choice="auto",
    #     temperature=0.2,
    #     top_p=0.9,
    #     max_tokens=300
    # )

    # print(final_response.choices[0].message)

    # return final_response.choices[0].message.content
    

# print(execute_tool(
#     "read_file",
#     '{"filepath": "sample.txt"'
# ))


# ask_llm_file_assistant("Hello, what can you do?")
# ask_llm_file_assistant(
#     "Read sample.txt and tell me what is inside it."
# )

print(ask_llm_file_assistant(
    "Search the resumes for Express."
)) 