import pandas as pd
import requests
import json
import re
import Hallucination_Detection_Query
from langchain_chroma import Chroma
from langchain_community.embeddings.sentence_transformer import SentenceTransformerEmbeddings
import time

def normalize(name):
    if pd.isnull(name):
        return name
    if not isinstance(name, str):
        name = str(name)
    name = re.sub(r'\d\. ', '', name)
    name = re.sub(r'(?<=.)\n(?=.)', ' ', name)
    name = re.sub(r'\n', '', name)
    return re.sub(r'[-_.]+', '-', name).strip(' `.-').lower()

def DeepSeek(text):
    better_text = re.sub(r'\\n|\\n\d\.', ',', text)
    better_text = re.sub(r'`(\w+)`', r',\1,', better_text)
    return (better_text)

def DeepSeek_Post(name):
    delete_words = {'and', 'the', 'optional', 'it\''}
    name = re.sub(r'[:\"\'()]', '', name)
    if name in delete_words:
        return ""
    else:
        return name

def delete_dupes_and_empty(packages):
    no_dupes = list(set(packages))
    no_dupes = [i for i in no_dupes if len(i) > 2]
    return [x for x in no_dupes if x]

def detectHallucination(line, ip, port):
    #line = line.astype(str)
    text = DeepSeek(line)
    processed_text = text.split(',')
    processed_text = [normalize(item) for item in processed_text if len(normalize(item).split()) == 1]
    processed_text = [DeepSeek_Post(item) for item in processed_text]

    no_dupes = list(set(processed_text))
    no_dupes = [i for i in no_dupes if len(i) > 2]

    for item in no_dupes:
        #print(item)
        if ' ' in item or item == 'None' or item == 'nan':
            continue
        answer = Hallucination_Detection_Query.query_API(item, ip, port)
        normalized = re.sub(r'[^\w\s]', '', answer).strip().upper()
        words = normalized.split()
        #print(words)
        if words:
            if words[0] != 'YES':
                return False, item
        continue
    return True, ""

def query_API(mode, infile, outfile_response_only, ip, port):
    ###### Need to insert path to prompt library here!
    data_path = ""

    embedding_function = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
    db = Chroma(persist_directory="./db", embedding_function=embedding_function)

    language = "Python"

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
        system_message = f"You are a coding assistant that recommends Python packages to help answer questions. Respond with only a list of {language} packages, separated by commas and no additional text or formatting. Your response must begin with the name of a {language} package."

        for i in code:
            time.sleep(1)
            bad_packages = []
            if mode == 1:
                prompt = f"What {language} packages are required to run this code: {i.strip()}"
            else:
                result = db.similarity_search_with_score(i, 5)
                quote = " ".join(item[0].page_content for item in result)
                prompt = f"What {language} packages would be useful in solving the following coding question: {i.strip()}. Here are some statements that may help answer the question: {quote}"

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
                "max_tokens": 64,
            }

            for _ in range(5):
                test = False
                response = requests.post(url, headers=headers, json=data, verify=False)
                if response.status_code == 200:
                    text = response.json()
                    choices_data = text['choices'][0].get('message', {}).get('content',{}).strip()
                    test, package = detectHallucination(choices_data, ip, port)
                    bad_packages.append(package)
                if test == True:
                    break
                else:
                    data["messages"][1]["content"] = f"{prompt}.\n Do not include the following packages in your answer: {', '.join(bad_packages)}"

            json.dump(choices_data, prompts_only)
            prompts_only.write('\n')

            x += 1
            if x % 500 == 0:
                print(x)