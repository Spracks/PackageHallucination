import re
import csv
import os

def refine_package_list(lst, data_path):
    with open(os.path.join(f"{data_path}", "options.csv"), 'r') as csvfile:
        reader = csv.reader(csvfile)
        option_like = [row[0] for row in reader]

    with open(os.path.join(data_path, "core_modules.csv"), 'r') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            core_modules = row

    new_list = lst

    for item in new_list:
        # remove local packages
        if "./" in item:
            new_list.remove(item)

        # remove faulty detects
        elif '\n' in item:
            new_list.remove(item)

        elif ' ' in item:
            new_list.remove(item)

        # check for options
        elif len(item) > 2:
            if item[:2] == "--":
                if item not in option_like:
                    new_list.remove(item)

    # remove nodejs core modules
    for core_item in core_modules:
        if core_item in new_list:
            new_list.remove(core_item)
    
    new_list = [x for x in new_list if len(x)>0 ]
    final_list = []
    for item in new_list:
        if "(" in item or ")" in item: continue
        item = item.replace('"','').replace(";","").replace('`','').replace("\"","").replace("'","").strip().strip("\n")
        if item == 'nan': continue
        # if len(item)>0:
        if item[0:1]=="\n":
            item = item[1:]
        if "https://" not in item:
            final_list.append(item.lower())

    return final_list

def extract_npm_packages(js_response, data_path):
    matches = []
    matches2 = []
    js_code = []

    # Get only the code
    code_pattern = r"```([\s\S]+?)```"
    if type(js_response)==str:
        js_code = re.findall(code_pattern, js_response)

    # Define the regex pattern to match all types of npm package imports
    pattern1 = r'\brequire\s*\(\s*[\'"]([^\'"]+)[\'"]\s*\)'
    pattern2 = r'\bimport\s*(?:[^\'"\n]*\s*)?[\'"]([^\'"]+)[\'"]'
    pattern3 = r'<script(?:\s[^>]*?)?src\s*=\s*[\'"]([^\'"]+)[\'"](?:\s[^>]*?)?>'
    #pattern4 = r"npm install\s+((?!@)(?:-g|--save-dev|-D)?[\s]+)?([\w\-/@.]+)"
    pattern5 = r"npx install\s+((?!@)(?:-g|--save-dev|-D)?[\s]+)?([\w\-/@.]+)"
    pattern6 = r"yarn add\s+([\w\-/@.]+)"

    for sample in js_code:
        lines = sample.split('\n')
        for line in lines:
            if 'import' in line:
                if 'from' in line:
                    matches2 = re.findall(r"\bfrom\s+([^\s]+)",line)
                else:
                    matches2 = re.findall(pattern2, line)
        
        # Find all types of imports in the JavaScript code
        matches1 = re.findall(pattern1, sample)

        matches3 = re.findall(pattern3, sample)
        matches3 = [pkg.split("/")[-1].split(".")[0] for pkg in matches3]

        #matches4 = re.findall(pattern4, sample, flags=re.IGNORECASE)
        #matches4 = [name[1] for name in matches4]

        matches5 = re.findall(pattern5, sample, flags=re.IGNORECASE)
        matches5 = [name[1] for name in matches5]

        matches6 = re.findall(pattern6, sample)

        matches.extend(matches1)
        matches.extend(matches2)
        matches.extend(matches3)
        #matches.extend(matches4)
        matches.extend(matches5)
        matches.extend(matches6)

    with open(os.path.join(f"{data_path}", "options.csv"), 'r') as csvfile:
        reader = csv.reader(csvfile)
        option_like = [row[0] for row in reader]

    with open(os.path.join(data_path, "core_modules.csv"), 'r') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            core_modules = row

    new_list = list(set(matches))

    for item in new_list:
        # remove local packages
        if item[0:2] == "./":
            new_list.remove(item)

        # remove faulty detects
        elif '\n' in item:
            new_list.remove(item)

        elif ' ' in item:
            new_list.remove(item)

        # check for options
        if len(item) > 2:
            if item[:2] == "--":
                if item not in option_like:
                    new_list.remove(item)

    # remove nodejs core modules
    for core_item in core_modules:
        if core_item in new_list:
            new_list.remove(core_item)
    new_list = [x for x in new_list if len(x)>0 ]
    return new_list

def extract_npm_install(js_response, data_path):
    matches = []
    js_code = []

    code_pattern = r"```([\s\S]+?)```"
    if type(js_response)==str:
        js_code = re.findall(code_pattern, str(js_response))

    pattern = r"npm install\s+((?!@)(?:-g|--save-dev|-D)?[\s]+)?([\w\-/@.]+)"

    for sample in js_code:
        matches = re.findall(pattern, sample, flags=re.IGNORECASE)
        matches = [name[1] for name in matches]

        matches.extend(matches)

    with open(os.path.join(f"{data_path}", "options.csv"), 'r') as csvfile:
        reader = csv.reader(csvfile)
        option_like = [row[0] for row in reader]

    with open(os.path.join(data_path, "core_modules.csv"), 'r') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            core_modules = row

    new_list = list(set(matches))

    for item in new_list:
        # remove local packages
        if item[0:2] == "./":
            new_list.remove(item)

        # remove faulty detects
        elif '\n' in item:
            new_list.remove(item)

        elif ' ' in item:
            new_list.remove(item)

        # check for options
        if len(item) > 2:
            if item[:2] == "--":
                if item not in option_like:
                    new_list.remove(item)

    # remove nodejs core modules
    for core_item in core_modules:
        if core_item in new_list:
            new_list.remove(core_item)
    new_list = [x for x in new_list if len(x)>0 ]

    final_list = []
    for item in new_list:
        item = item.replace('"','').replace(";","")
        if item[0:1]=="\n":
            item = item[1:]
        final_list.append(item)

    return final_list

def delete_dupes_and_empty(packages):
    no_dupes = list(set(packages))
    no_dupes = [i for i in no_dupes if len(i) > 2]
    return [x for x in no_dupes if x]

def CodeLlama(text, path):
    a_list = []
    final_list = []

    for bal in ["None","no additional", "any additional","does not require", "no packages are required",
                "no external","C#", "Perl", "not Javascript", "nopackagesarerequired",
                " php ", " PHP ", " java ", " Java ","C++", "any external", ".NET Maui"]:
        if bal in text:
            return []

    a_list = [part for part in text.split("###") if part]
    a_list = [part for part in a_list if 'Explanation' not in part]

    c_list=[]
    d_list = []
    for item in a_list:
        if 'Code:' in item:
            c_list.extend(extract_npm_packages(item, path))

        elif ':' in item: continue
        elif '!' in item: continue
        else:
            for it in ['js\n', ' ', '`','None', '"',"'"]:
                item = item.replace(it,'')
            c_list.append(item)

    for item in c_list:
        temp_list = item.split(',')
        d_list.extend(temp_list)

    for item in d_list:
        temp = item.strip('\n').strip("./")
        if "\n" not in temp and "Error" not in temp: 
            final_list.append(temp)
        # final_list.append("test_string")

    return refine_package_list(final_list, path)

def Mistral(text, path):

    for bal in ["None","no additional", "any additional","does not require",
                "no external","C#", "Perl","not Javascript", "built in", "built-in"
                " php ", " PHP ", " java ", " Java ","C++", "any external", ".NET Maui" ]:
        if bal in text:
            return []
    
    a_list = []
    # b_list = []
    final_list = []

    avoid_list = []

    avoid_list.extend(re.findall(r" `([^`]+)` object",text))
    avoid_list.extend(re.findall(r" `([^`]+)` method",text))
    avoid_list.extend(re.findall(r" `([^`]+)` function",text))
    avoid_list.extend(re.findall(r" `([^`]+)` module",text))

    avoid_list = list(set(avoid_list))

    a_list = re.findall(r" `([^`]+)`",text)
    for item in a_list:
        if item not in avoid_list:
            temp = item.replace("'","").replace('"','').strip().strip("\n")
            final_list.append(temp)
    
    return refine_package_list(final_list, path)
    
def Magicoder(text, path):
    for bal in ["None","built-in","no additional", "any additional","no external", 
                "built in","Perl","not Javascript","does not require",
                " php ", " PHP ", " java ", " Java ","C++", "any external","C#" ,".NET Maui"]:
        if bal in text:
            return []
    
    final_list = []

    if ":" in text:
        final_list = re.findall(r"`([^`]+)`:", text)
        # final_list = [x[1:-2] for x in a_list]
    else:
        text = re.sub(r'\n\d{1}','',text)
        # text = re.sub(r'\n', '', text)
        text = text.replace("`","").replace("\\","").replace('"','').replace("\n","")

        if text.strip().count(" ")==0:
            final_list = text.split(",")
        elif text.strip().count(",")==text.count(" "):
            final_list = text.replace(" ","").split(",")
    
    return refine_package_list(final_list, path)
    
def Mixtral(text, path):
    final_list = []
    a_list = []
    for item in [" php ", " PHP ", " java ", " Java ","C++", "does not require",
                 " no external ", "C#","Perl",".NET Maui","not Javascript",
                 " any external ", " no additional ", "built in", "built-in", "any additional"]:
        if item in text:
            return []


    avoid_list = []

    avoid_list.extend(re.findall(r" `([^`]+)` object",text))
    avoid_list.extend(re.findall(r" `([^`]+)` method",text))
    avoid_list.extend(re.findall(r" `([^`]+)` function",text))
    avoid_list.extend(re.findall(r" `([^`]+)` module",text))

    avoid_list = list(set(avoid_list))

    a_list = re.findall(r" `([^`]+)`",text)

    for item in a_list:
        if item not in avoid_list:
            if "(" not in item: 
                final_list.append(item.strip())

    return refine_package_list(final_list, path)

def WizardCoder(text, path):
    final_list = []
    a_list = []
    b_list = []
    o_list = []

    for item in ["None", "php", "PHP", "Java ", "C++", "does not require",
                 "C#","Perl",".NET Maui","not Javascript",
                  "java ", "no external", "any external", "no additional", "any additional"]:
        if item in text: return []
    
    avoid_list = []

    avoid_list.extend(re.findall(r" `([^`]+)` object",text))
    avoid_list.extend(re.findall(r" `([^`]+)` method",text))
    avoid_list.extend(re.findall(r" `([^`]+)` function",text))
    avoid_list.extend(re.findall(r" `([^`]+)` module",text))

    avoid_list = list(set(avoid_list))

    o_list = text.strip().split(".")
    for sstr in o_list:
        if "built in" not in text or "built-in" not in text:
            a_list.extend(re.findall(r" `([^`]+)`",sstr))
            b_list.extend(re.findall(r"'([^']+)'", sstr))

    b_list = [x for x in b_list if " " not in x]
    a_list.extend(b_list)

    for item in a_list:
        if item not in avoid_list:
            if "(" not in item: 
                final_list.append(item.strip())

    return refine_package_list(final_list, path)

def GPT(text, path):
    final_list = []
    # a_list = []
    for item in ["No packages", "No additional", "no additional", "does not pertain","nan",
                 "C++", "C#","Perl", ".NET Maui","not Javascript","does not require",
                 "any additional", "None", "PHP", "Java ", "No Javascript packages"]:
        if item in text: return []
    if text == "": return []
    text = text.replace('`','').replace('"','').replace("'","")

    final_list = text.strip("'").strip('"').strip(".").strip("/").split(",")

    return refine_package_list(final_list, path)

def DeepSeek_1B(text, path):
    final_list = []
    final_list_2 = []

    avoid_list = []

    avoid_list.extend(re.findall(r" `([^`]+)` object",text))
    avoid_list.extend(re.findall(r" `([^`]+)` method",text))
    avoid_list.extend(re.findall(r" `([^`]+)` function",text))
    avoid_list.extend(re.findall(r" `([^`]+)` module",text))

    avoid_list = list(set(avoid_list))
    
    if "```" in text:
        final_list.extend(extract_npm_packages(text, path))

    if "`" not in text:
        if  ":" in text:
            a_list = text.strip().split(":")
            if len(a_list)==2:
                bal = a_list[1]
                bal = re.sub(r'\n\d{1}\.', '', bal)
                bal = re.sub(r'\n\d{1}', '', bal)
                bal = re.sub(r'\n', '', bal)
                bal = bal.replace('"','')

                b_list = bal.strip("\n").split(" ")
                for item in b_list:
                    final_list.append(item.strip())
    else:
        final_list = re.findall(r" `([^`]+)`",text)

    for item in final_list:
        item = item.replace('"','').replace(";","")
        if "(" in item or ")" in item: continue
        if item=='nan': continue
        if len(item)>0:
            if item[0:1]=="\n":
                item = item[1:]
        
        if item not in avoid_list:
            final_list_2.append(item)       

    return refine_package_list(final_list_2, path)

def DeepSeek_6B(text, path):
    for item in ["No packages", "No additional", "no additional", "does not pertain",
                 "C++", "C#","Perl", ".NET Maui","not Javascript","does not require",
                 "any additional", "None", "PHP", "Java ", "No Javascript packages"]:
        if item in text: return []

    final_list = []

    if "\n1" not in text:
        a_list = text.strip().split(",")

        for item in a_list:
            item = item.replace('`','').replace("\"","").replace('"','').strip()
            if " " in item: continue
            if "(" in item: continue
            if ")" in item: continue
            if item=='nan': continue
            final_list.append(item)
    else:
        a_list = re.findall(r"`([^`]+)`",text)

        for item in a_list:
            if " " in item: continue
            if "(" in item: continue
            if ")" in item: continue
            item = item.replace('`','').replace("\"","").replace('"','').strip()
            if item=='nan': continue
            final_list.append(item)
    
    return refine_package_list(final_list, path)

def DeepSeek_33B(text, path):
    a_list = []
    final_list = []
    for item in ["No packages", "No additional", "no additional", "does not pertain","no specific JavaScript packages",
                 "C++", "C#","Perl", ".NET Maui","not Javascript","does not require",
                 "any additional", "None", "PHP", "Java ", "No Javascript packages"]:
        if item in text: return []

    if ":" not in text:
        # print("1")
        if (text.count(" ")-text.count(","))>3:
            # print("2")
            pass
        else:
            a_list = text.split(",")
    else:
        # print("3")
        if "\n1." in text:
            # print("4")
            a_list = re.findall(r'\n\d{1}\. \w+(?!\\)',text)
        
            # print("no \n1.")
    # print(a_list)
    for item in a_list:
        temp = re.sub(r'\n\d{1}.', '', item)
        temp = temp.strip("\n")
        if "(" in temp or ")" in temp: continue
        if 'nan' in item: continue 
        final_list.append(temp.replace("\"","").replace("`","").replace("'","").replace('"','').strip())
    # for item in final_list:
        # if '"' in item: print(item)

    return refine_package_list(final_list, path)