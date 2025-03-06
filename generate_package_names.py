from transformers import AutoModelForCausalLM, AutoTokenizer
import pandas as pd
import json
from tqdm import tqdm

def generate_packages(mode, infile, outfile, model_path, language="Python", temperature=.01, top_k=20, top_p=0.9):
    tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)
    model = AutoModelForCausalLM.from_pretrained(model_path,
                                                 device_map="cuda",
                                                 trust_remote_code=True)

    with open(infile, 'r') as file:
        df = pd.read_json(file, lines=True)
        code = []
        if mode == 1:
            for index, row in df.iterrows():
                code.append(row['Answers'])
        else:
            for index, row in df.iterrows():
                code.append(row[0])

    with open(outfile, 'w', newline='', encoding='utf-8') as output:

        if mode == 1:
            system_message = f"You are a coding assistant that determines {language} packages necessary to execute code. Respond with only a list of {language} packages, separated by commas and no additional text or formatting. Your response must begin with the name of a {language} package."
            prefix = f"Which {language} packages are required to run this code: "
        elif mode == 2:
            system_message = f"You are a coding assistant that recommends {language} packages that would be helpful to solve given problems. Respond with only a list of {language} packages, separated by commas and no additional text or formatting. Your response must begin with the name of a {language} package."
            prefix = f"What {language} packages would be useful in solving the following coding problem: "

        for sample in tqdm(code, desc="Generating package names", unit="sample"):
            messages = [{"role": "system", "content": system_message},
                       {"role": "user", "content": prefix + sample.strip()}]

            inputs = tokenizer.apply_chat_template(messages, add_generation_prompt=True, return_tensors="pt").to(model.device)

            outputs = model.generate(inputs,
                                    temperature=temperature,
                                    top_p=top_p,
                                    typical_p=1,
                                    epsilon_cutoff=0,
                                    eta_cutoff=0,
                                    top_k=top_k,
                                    do_sample=True,
                                    guidance_scale=1,
                                    max_new_tokens=64,
                                    num_return_sequences=1,
                                    eos_token_id=tokenizer.eos_token_id,
                                    pad_token_id=tokenizer.eos_token_id,
                                    return_dict_in_generate=True)

            generated_code = tokenizer.decode(outputs.sequences[0, inputs.shape[1]:], skip_special_tokens=True)
            json.dump(generated_code, output)
            output.write('\n')