import requests

def query_API(package, ip, port):
    language = "Python"

    url = f"http://{ip}:{port}/v1/chat/completions"

    headers = {
        "Content-Type": "application/json"
    }

    system_message = f"Your answers should be a single binary word, Yes or No. Do not provide answers more than one word. Your first word must be Yes or No."
    #prefix = "Which Python packages are required to run this code: "

    data = {
        "messages": [{"role": "system", "content": system_message},
                     {"role": "user", "content": f"Is {package} a valid Python package?"}],
        "mode": "instruct",
        "temperature": .01,
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

    response = requests.post(url, headers=headers, json=data, verify=False)

    if response.status_code == 200:
        text = response.json()

        choices_data = text['choices'][0].get('message', {}).get('content',{}).strip()
        return choices_data

    return ''