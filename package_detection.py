import custom_parse_python
import custom_parse_javascript
import aggregate_results
import pandas as pd
import re
import logging
import os

def normalize_python(name):
    if pd.isnull(name):
        return name
    if not isinstance(name, str):
        name = str(name)
    name = re.sub(r'\d\. ', '', name)
    name = re.sub(r'(?<=.)\n(?=.)', ' ', name)
    name = re.sub(r'\n', '', name)
    return re.sub(r'[-_.]+', '-', name).strip(' `.-').lower()

def normalize_javascript(name):
    if pd.isnull(name):
        return name
    if not isinstance(name, str):
        name = str(name)
    name = re.sub(r"[`]", "", name)
    return name

def normalize_pip(name):
    if pd.isnull(name):
        return name
    if not isinstance(name, str):
        name = str(name)

    name = re.sub(r'[()\'\"]', '', name)
    return re.sub(r'[-_.]+', '-', name).strip(' "`.-').lower()

def check_packages(package_list, package_names, false_positives):
    in_set = []
    not_in_set = []
    for item in package_list:
        if ' ' in item or item == 'None' or item == 'nan':
            continue
        if item in package_names:
            in_set.append(item)
        else:
            if item not in false_positives:
                not_in_set.append(item)

    return in_set, not_in_set

def check_npms(npm_list, npm_names):
    in_set = []
    not_in_set = []
    for item in npm_list:
        if ' ' in item or item == 'None' or item == 'nan':
            continue
        if item in npm_names:
            in_set.append(item)
        else:
            not_in_set.append(item)

    return in_set, not_in_set

def package_search_python(df, data_path, pre, post, style):
    package_names = pd.read_csv(f"{data_path}/pypi_package_names.csv", header=None)
    package_names[0] = package_names[0].apply(normalize_python)
    package_names_set = set(package_names[0])
    false_positives = pd.read_csv(f"{data_path}/false_positive_packages.csv", header=None)
    false_positives_set = set(false_positives[1])

    df['Test_1'] = df['Test_1'].astype(str)
    df['Test_2'] = df['Test_2'].astype(str)

    if pre:
        func_pre = getattr(custom_parse_python, style)
        df['Test_1'] = df['Test_1'].apply(func_pre)
        df['Test_2'] = df['Test_2'].apply(func_pre)

    df['Test_1'] = df['Test_1'].str.split(',').apply(lambda x: [item for item in (normalize_python(entry) for entry in x) if len(item.split()) == 1])
    df['Test_2'] = df['Test_2'].str.split(',').apply(lambda x: [item for item in (normalize_python(entry) for entry in x) if len(item.split()) == 1])

    if post:
        func_post = getattr(custom_parse_python, f"{style}_Post")
        df['Test_1'] = df['Test_1'].apply(lambda x: [item for item in (func_post(entry) for entry in x)])
        df['Test_2'] = df['Test_2'].apply(lambda x: [item for item in (func_post(entry) for entry in x)])

    df['Test_1'] = df['Test_1'].apply(custom_parse_python.delete_dupes_and_empty)
    df['Test_2'] = df['Test_2'].apply(custom_parse_python.delete_dupes_and_empty)

    df[['valid_1', 'hallucinated_1']] = df['Test_1'].apply(lambda x: check_packages(x, package_names_set, false_positives_set)).apply(pd.Series)
    df[['valid_2', 'hallucinated_2']] = df['Test_2'].apply(lambda x: check_packages(x, package_names_set, false_positives_set)).apply(pd.Series)

    return df

def package_search_javascript(df, data_path, pre, post, style):
    package_names = pd.read_csv(f"{data_path}/npm_package_names.csv", header=None)
    package_names_set = set(package_names[0])
    false_positives = pd.read_csv(f"{data_path}/false_positive_packages.csv", header=None)
    false_positives_set = set(false_positives[1])

    df['Test_1'] = df['Test_1'].astype(str)
    df['Test_2'] = df['Test_2'].astype(str)

    func_pre = getattr(custom_parse_javascript, style)
    df['Test_1'] = df['Test_1'].apply(func_pre, args=(data_path,))
    df['Test_2'] = df['Test_2'].apply(func_pre, args=(data_path,))

    df['Test_1'] = df['Test_1'].apply(custom_parse_javascript.delete_dupes_and_empty)
    df['Test_2'] = df['Test_2'].apply(custom_parse_javascript.delete_dupes_and_empty)

    df[['valid_1', 'hallucinated_1']] = df['Test_1'].apply(lambda x: check_packages(x, package_names_set, false_positives_set)).apply(pd.Series)
    df[['valid_2', 'hallucinated_2']] = df['Test_2'].apply(lambda x: check_packages(x, package_names_set, false_positives_set)).apply(pd.Series)

    return df

def parse_pip_install(text):
    if not isinstance(text, (str, bytes)):
        return []
    matches = re.findall(r'pip\s+install\s+(?P<package_name>\S+)', text)
    packages = [match for match in matches if not match.startswith('-')]
    return packages if packages else []

def pip_numbers(df, data_path):
    df['pip'] = df['Answers'].apply(parse_pip_install)
    df['pip'] = df['pip'].apply(lambda x: [item for item in (normalize_pip(entry) for entry in x)])

    pypi = pd.read_csv(f"{data_path}/pypi_package_names.csv", header=None)
    pypi[0] = pypi[0].apply(normalize_python)
    pips = set(pypi[0])

    df[['pip_valid', 'pip_hallucinated']] = df['pip'].apply(lambda x: check_pips(x, pips)).apply(pd.Series)
    df['pip_hallucinated'] = df['pip_hallucinated'].apply(custom_parse_python.delete_dupes_and_empty)

    return df

def npm_numbers(df, data_path):
    npm = pd.read_csv(f"{data_path}/npm_package_names.csv", header=None)
    npm[0] = npm[0].apply(normalize_javascript)
    npms = set(npm[0])

    df['npm'] = df['Answers'].apply(custom_parse_javascript.extract_npm_install, args=(data_path,))
    df['npm'] = df['npm'].apply(custom_parse_javascript.refine_package_list, args=(data_path,))
    df[['npm_valid', 'npm_hallucinated']] = df['npm'].apply(lambda x: check_npms(x, npms)).apply(pd.Series)
    df['npm_hallucinated'] = df['npm_hallucinated'].apply(custom_parse_javascript.delete_dupes_and_empty)

    return df

def check_pips(pip_list, pip_names):
    in_set = []
    not_in_set = []
    translation_table = str.maketrans('','','()[]`')
    version_pattern = re.compile(r"([^=<>!~]+)([=<>!~]{1,2}[\d\.]+)?")

    if pip_list:
        for item in pip_list:
            text = item.translate(translation_table)
            #text = re.sub(r"[+@:\"\',{}/\*]", "", text)
            if bool(re.search(r"[+@:\"\',{}/\*]", text)):
                continue
            for part in text.split():
                if part.startswith('--'):
                    continue
                match = version_pattern.match(part)
                if match:
                    #text = re.sub(r"\n", '', text)
                    text = match.group(1).strip()
                    text = normalize_python(text)
                    if text.startswith('--') or "requirements" in text:
                        continue
                    if text in pip_names:
                        in_set.append(text)
                    else:
                        not_in_set.append(text)

    return in_set, not_in_set

def get_pre_post_info(model, language):
    pre = False
    post = False
    style = ""
    if model == "CodeLlama_34B_Python":
        style = "CodeLlama"
    elif model == "Mistral_7B" or model == "Mixtral_7B":
        if language == "Python":
            pre = True
            post = True
        style = "Mistral"
    elif "Deep" in model or "deep" in model:
        if language == "Javascript":
                if model == "DeepSeek_1B":
                    style = model
                elif model == "DeepSeek_6B":
                    style = model
                elif model == "DeepSeek_33B":
                    style = model
        else:
            pre = True
            post = True
            style = "DeepSeek"
    elif model == "WizardCoder_33B" or model == "WizardCoder_Python_7B":
        if language == "Python":
            pre = True
            post = True
        style = "WizardCoder"
    elif model == "Openchat_7B":
        if language == "Python":
            post = True
        style = "Openchat"

    return pre, post, style

def detect_packages(data_path, save_path, model_name, log_level, language):
    if log_level != 'off':
        logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

    def process_python_dataset(master_file, package_files, result_file_prefix):
        merged_results = aggregate_results.merge_prompts_and_packages(os.path.join(save_path, master_file),
                                                                                   *[os.path.join(save_path, file) for file in package_files])
        merged_results.to_csv(os.path.join(save_path, f"{result_file_prefix}_results.csv"), index=False)
        logging.info(f"{result_file_prefix} responses merged into dataframe")

        results = pd.read_csv(os.path.join(save_path, f"{result_file_prefix}_results.csv"))
        results_tested = package_search_python(results, data_path, pre, post, style)
        results_final = pip_numbers(results_tested, data_path)
        results_final.to_csv(os.path.join(save_path, f"{result_file_prefix}_results.csv"), index=False)
        totals = aggregate_results.sum_columns(results_final, result_file_prefix, language)
        return results_final, totals

    def process_javascript_dataset(master_file, package_files, result_file_prefix):
        merged_results = aggregate_results.merge_prompts_and_packages(os.path.join(save_path, master_file),
                                                                                   *[os.path.join(save_path, file) for file in package_files])
        merged_results.to_csv(os.path.join(save_path, f"{result_file_prefix}_results.csv"), index=False)
        logging.info(f"{result_file_prefix} responses merged into dataframe")

        results = pd.read_csv(os.path.join(save_path, f"{result_file_prefix}_results.csv"))
        results_tested = package_search_javascript(results, data_path, pre, post, style)
        results_final = npm_numbers(results_tested, data_path)
        results_final.to_csv(os.path.join(save_path, f"{result_file_prefix}_results.csv"), index=False)
        totals = aggregate_results.sum_columns(results_final, result_file_prefix, language)
        return results_final, totals

    pre, post, style = get_pre_post_info(model_name, language)

    datasets = {
        "LLM_LY": ["LLM_Recent_Master.json", ["LLM_Recent_packages_1.json", "LLM_Recent_packages_2.json"]],
        "LLM_AT": ["LLM_All_Time_Master.json", ["LLM_All_Time_packages_1.json", "LLM_All_Time_packages_2.json"]],
        "SO_LY": ["Stack_Overflow_Recent_Master.json", ["Stack_Overflow_Recent_packages_1.json", "Stack_Overflow_Recent_packages_2.json"]],
        "SO_AT": ["Stack_Overflow_All_Time_Master.json", ["Stack_Overflow_All_Time_packages_1.json", "Stack_Overflow_All_Time_packages_2.json"]],
    }

    all_results = []
    all_totals = []
    for dataset_name, (master_file, package_files) in datasets.items():
        logging.info(f"Processing dataset: {dataset_name}")
        if language == "Python":
            results, totals = process_python_dataset(master_file, package_files, dataset_name)
        else:
            results, totals = process_javascript_dataset(master_file, package_files, dataset_name)
        all_results.append(results)
        all_totals.append(totals)

    logging.info("Merging all datasets")
    package_names_final = pd.concat(all_results)
    final_totals = pd.concat(all_totals)

    totals_sum = final_totals.sum()
    totals_df = pd.DataFrame([totals_sum], index=["Totals"])
    final_totals = pd.concat([final_totals, totals_df])

    logging.info("Saving final results")
    final_totals.to_csv(os.path.join(save_path, "FINAL_RESULTS.csv"))
    package_names_final.drop(["Prompts", "Answers", "Test_1", "Test_2", "Questions"], axis=1, inplace=True)
    package_names_final.to_csv(os.path.join(save_path, "PACKAGE_NAMES.csv"), index=False)

    logging.info("Package detection complete. Results saved.")
    logging.info(f"Final Totals: \n {final_totals}")