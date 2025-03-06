import pandas as pd
import re

def delete_dupes_and_empty(packages):
    no_dupes = list(set(packages))
    no_dupes = [i for i in no_dupes if len(i) > 2]
    return [x for x in no_dupes if x]

# OpenChat = OpenChat() -> normalize() -> no_dupes()
def Openchat_Post(name):
    if pd.isnull(name):
        return name
    name = re.sub(r'gpt4', '', name)
    name = re.sub(r'(g{3,})', '', name)

    if re.search(r'git|gpt', name):
        return ""
    else:
        return name

#Wizard_Coder_7B = Wizard_Coder_P -> normalize() -> Wizard_Coder_P_Post() -> no_dupes()
#Wizard_Coder_33B = DeepSeek -> normalize() -> Wizard_Coder_P_Post() -> no_dupes()

#Applied before normalize
def WizardCoder(text):
    better_text = re.sub(r'\\r\\n-|\\r\\n\d\.|\\r\\n', ',', text)
    better_text = re.sub(r'`(\w+)`', r',\1,', better_text)
    return(better_text)

#Applied after normalize
def WizardCoder_Post(name):
    name = re.sub('[()\'\"]', '', name)
    delete_words = {'and','the','optional','it\''}
    if name in delete_words:
        return ""
    else:
        return name

# DeepSeek 33B = Deepseek() -> normalize() -> no_dupes()
# DeepSeek 1B = Deepseek() -> normalize() -> DeepSeek_Post -> no_dupes()
def DeepSeek(text):
    better_text = re.sub(r'\\n|\\n\d\.', ',', text)
    better_text = re.sub(r'`(\w+)`', r',\1,', better_text)
    return (better_text)

# Applied after normalize
def DeepSeek_Post(name):
    delete_words = {'and', 'the', 'optional', 'it\''}
    name = re.sub(r'[:\"\'()]', '', name)
    if name in delete_words:
        return ""
    else:
        return name


# CodeLlama_34B_Python = CodeLlama() -> normalize() -> CodeLlama_Post() -> no_dupes()
# Applied before normalize
def CodeLlama(text):
    better_text = re.sub(r'\\n', ',', text)
    return (better_text)


# Applied after normalize
def CodeLlama_Post(name):
    name = re.sub(r'\":\(', '', name)
    delete_words = {'python', 'nan'}

    if name in delete_words:
        return ""
    else:
        return name

# Mistral = Mistral() -> normalize() -> Mistral_Post() -> no_dupes()
# Mixtral = Mistral() -> normalize() -> Mistral_Post() -> no_dupes()
def Mistral(text):
    better_text = re.sub(r'\\n|\\n\d\.', ',', text)
    better_text = re.sub(r'`(\w+)`', r',\1,', better_text)
    return (better_text)

def Mistral_Post(name):
    name = re.sub(r'[:\(\)]', '', name)
    name = re.sub(r'```', '', name)
    delete_words = {'run', 'with', 'additionally', 'the', 'and', 'bash', 'pip', 'make', 'module',
                    'package', 'import-module', 'using', 'however', 'python', 'for'}

    if name in delete_words:
        return ""
    else:
            return name