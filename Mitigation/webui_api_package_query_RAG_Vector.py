from langchain_chroma import Chroma
from langchain_community.embeddings.sentence_transformer import SentenceTransformerEmbeddings
import pandas as pd
import requests
import json
import time

def query_API(mode, infile, outfile_response_only, ip, port):
    language = "Python"

    embedding_function = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
    db = Chroma(persist_directory="./db", embedding_function=embedding_function)

    x = 0
    with open(infile, 'r') as file:
        df = pd.read_json(file, lines=True)
        code = []
        if mode == 1:
            for index, row in df.iterrows():
                code.append(row['Answers'])
        else:
            for index, row in df.iterrows():
                code.append(row[0])

    url = f"http://{ip}:{port}/v1/chat/completions"

    headers = {
        "Content-Type": "application/json"
    }

    with open(outfile_response_only, 'w', newline='', encoding='utf-8') as prompts_only:
        if mode == 2:
            system_message = f"You are a coding assistant that recommends Python packages to help answer questions. Use the provided statements to help form your response, but do not limit your response to those statement. Respond with only a list of {language} packages, separated by commas and no additional text or formatting. Your response must begin with the name of a {language} package."
        else:
            system_message = f"Provide the {language} package names that are required to run the provided code and no additional text or formatting. Multiple packages should be separated by commas. If the input does not contain code, reply 'None'"

        for i in code:
            time.sleep(1)
            if mode == 2:
                result = db.similarity_search_with_score(i, 5)
                quote = " ".join(item[0].page_content for item in result)
                prompt = f"What {language} packages would be useful in solving the following coding question: {i.strip()}. Here are some statements that may help answer the question: {quote}"
            else:
                prompt = f"Which {language} packages are required to run this code: "
            data = {
                "messages": [{"role": "system", "content": system_message},
                             {"role": "user", "content": prompt}],
                "mode": "instruct",
                "temperature": 0.01,
                "top_p": 0.9,
                "repetition_penalty": 1.15,
                "repetition_penalty_range": 1024,
                "typical_p": 1,
                "tfs": 1,
                "top_a": 0,
                "epsilon_cutoff": 0,
                "eta_cutoff": 0,
                "top_k": 20,
                "min_p": 0,
                "do_sample": True,
                "repetition_penalty": 1,
                "guidance_scale": 1,
                "add_bos_token": True,
                "skip_special_tokens": True,
                # Changed max_tokens to lower value
                "max_tokens": 64,
            }

            response = requests.post(url, headers=headers, json=data, verify=False)

            if response.status_code == 200:
                text = response.json()

                choices_data = text['choices'][0].get('message', {}).get('content',{}).strip()
                json.dump(choices_data, prompts_only)
                prompts_only.write('\n')

            x += 1
            if x % 500 == 0:
                print(x)