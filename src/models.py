from langchain_aws import ChatBedrock
from langchain_community.llms import LlamaCpp

MAX_TOKENS = 40000
TEMPERATURE = 0.2

BEDROCK_MODEL_ID = "anthropic.claude-3-5-sonnet-20240620-v1:0"
LLAMA_CPP_MODEL_PATH = ""  # Path to your local LlamaCpp model.

bedrock_model = ChatBedrock(
    model_id=BEDROCK_MODEL_ID,
    model_kwargs={"temperature": TEMPERATURE, "max_tokens": MAX_TOKENS},
)

llama_cpp_model = None
if LLAMA_CPP_MODEL_PATH:
    try:
        llama_cpp_model = LlamaCpp(
            model_path=LLAMA_CPP_MODEL_PATH,
            temperature=TEMPERATURE,
            max_tokens=MAX_TOKENS,
            seed=42,
        )
    except Exception as e:
        print(f"Warning: Could not initialize LlamaCpp model: {e}")
