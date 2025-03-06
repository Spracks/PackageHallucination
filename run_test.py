import generate_code
import aggregate_results
import generate_package_names
import package_detection
import argparse
import os
import logging

# Runs an entire experiment for a single model
# Given a specific model name in ./Models:
#   4 files need to be in the "./Data" directory:
#       1. json of LLM generated prompts from all-time popular packages named "./LLM_AT.json"
#       2. json of LLM generated prompts from 2023 (last year) most popular packages named"./LLM_LY.json"
#       3. json of Stack Overflow questions from all-time named "./SO_AT.json.json"
#       4. json of Stack Overflow questions from last year named "./SO_LY.json.json"

parser = argparse.ArgumentParser()
parser.add_argument("model_name", type=str, help="File name, without extension, of the model being tested")
parser.add_argument("--language", default="Python", choices=["Python", "Javascript"], type=str, help="Programming language to be tested. Only supports Python or JavaScript currently")
parser.add_argument("--logging", type=str, default='verbose', help="Logging level. Set to 'off' to disable logging")
parser.add_argument("--code_temp", default=0.7, type=int, help="Model temperature")
parser.add_argument("--package_temp", default=0.01, type=int, help="Model temperature")
parser.add_argument("--top_k", default=20, type=int, help="Top-K parameter")
parser.add_argument("--top_p", default=0.9, type=float, help="Top-P parameter")

args = parser.parse_args()
MODEL_NAME = args.model_name
LANGUAGE = args.language
CODE_TEMPERATURE = args.code_temp
PACKAGE_TEMPERATURE = args.package_temp
TOP_K = args.top_k
TOP_P = args.top_p
logs = args.logging

if logs != "off":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

if LANGUAGE == "Python":
    DATA_PATH = os.path.join(os.getcwd(), "Data", "Python")
else:
    DATA_PATH = os.path.join(os.getcwd(), "Data", "Javascript")

MODEL_PATH = os.path.join(os.getcwd(), "Models", MODEL_NAME)
SAVE_PATH = os.path.join(os.getcwd(), "Tests", f"{MODEL_NAME}_{LANGUAGE}")

DATASETS = {
    "LLM_Recent": "LLM_LY.json",
    "LLM_All_Time": 'LLM_AT.json',
    "Stack_Overflow_Recent": "SO_LY.json",
    "Stack_Overflow_All_Time": "SO_AT.json"
}

def generate_and_process_code():
    for key, file_name in DATASETS.items():
        input_path = os.path.join(DATA_PATH, file_name)
        output_code = os.path.join(SAVE_PATH, f"{key}_code.json")
        master_output = os.path.join(SAVE_PATH, f"{key}_Master.json")

        if os.path.exists(master_output):
            logging.info(f"Master files already exists for {key}. Skipping...")
            continue

        if not os.path.exists(output_code):
            logging.info(f"Generating code for {key}...")
            generate_code.generate_code(input_path, output_code, MODEL_PATH, LANGUAGE, CODE_TEMPERATURE, TOP_K, TOP_P)
            logging.info(f"Code generation for {key} complete.")
        else:
            logging.info(f"Code files already exist for {key}. Skipping generation.")

        logging.info(f"Merging code with prompts for {key}...")
        if "LLM" in key:
            aggregate_results.combine_code_and_prompt(input_path, output_code, master_output)
        else:
            aggregate_results.combine_SO_prompt_and_code(input_path, output_code, master_output)

        logging.info(f"Merged code with prompts for {key}.")

def query_package_names():
    #Query the LLM to recommend packages based on the generated code and original prompt
    for mode in range(1,3):
        for key, _ in DATASETS.items():
            master_path = os.path.join(SAVE_PATH, f"{key}_Master.json")
            output = os.path.join(SAVE_PATH, f"{key}_packages_{mode}.json")

            if os.path.exists(output):
                logging.info(f"Query outputs already exist for {key}, Query {mode}. Skipping...")
                continue

            logging.info(f"Querying {key} with Query {mode}...")
            generate_package_names.generate_packages(mode, master_path, output, MODEL_PATH, LANGUAGE, PACKAGE_TEMPERATURE, TOP_K, TOP_P)
            logging.info(f"Query {mode} for {key} complete.")

def main():
    os.makedirs(os.path.join(SAVE_PATH), exist_ok=True)
    logging.info("Starting experiment...")
    #generate_and_process_code()
    #query_package_names()
    package_detection.detect_packages(DATA_PATH, SAVE_PATH, MODEL_NAME, logs, LANGUAGE)
    logging.info("Experiment complete")

if __name__ == "__main__":
    main()



