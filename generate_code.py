from transformers import AutoModelForCausalLM, AutoTokenizer
import pandas as pd
import json
from tqdm import tqdm

def generate_code(infile, outfile, model_path, language="Python", temperature=.7, top_k=20, top_p=0.9):
    tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)
    model = AutoModelForCausalLM.from_pretrained(model_path,
                                                 device_map="cuda",
                                                 trust_remote_code=True)

    ##### File should be "package_prompts_master" if generating prompts
    ##### "generated_prompts_cleaned" if generating code
    with open(infile, 'r') as file:
        df = pd.read_json(file, lines=True)
        prompts = []
        for index, row in df.iterrows():
            prompts.append(row[0])

    system_message = f"You are a coding assistant that generates {language} code. Provide only the {language} code and add additional explanatory text only when absolutely necessary. If no code is required to answer the question, simply reply 'None'"

    with open(outfile, 'w', newline='', encoding='utf-8') as output:
        for prompt in tqdm(prompts, desc="Generating code", unit="prompt"):
            messages = [
                {'role': 'user', 'content': system_message + prompt}
            ]

            inputs = tokenizer.apply_chat_template(messages, add_generation_prompt=True, return_tensors="pt").to(model.device)

            outputs = model.generate(inputs,
                                     max_new_tokens=2048,
                                     do_sample=True,
                                     top_k=top_k,
                                     top_p=top_p,
                                     num_return_sequences=1,
                                     temperature=temperature,
                                     eos_token_id=tokenizer.eos_token_id,
                                     pad_token_id=tokenizer.eos_token_id,
                                     return_dict_in_generate=True)

            generated_code = tokenizer.decode(outputs.sequences[0, inputs.shape[1]:], skip_special_tokens=True)
            #print(generated_code)

            json.dump(generated_code, output)
            output.write('\n')
