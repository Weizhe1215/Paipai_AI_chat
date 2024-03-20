import os
import re
from docx import Document
import pandas as pd
import yaml


# 把prompt中的xxxxxx替换成尽调报告中的对应内容
def get_prompt(text, prompt):
    return prompt.replace('xxxxxx', text)


# 生成百川所需的特定的prompt
def get_prompt_baichuan(text, prompt):
    messages = []
    messages.append({"role": "user", "content": get_prompt(text, prompt)})
    return messages


# 从指定目录中获取尽调报告的docx文档，然后提取出“配置逻辑”的内容
def extract_content_from_docx(folder_path, regex_pattern):
    extracted_contents = []
    name_list = []
    # 遍历文件夹中的所有文件
    for file in os.listdir(folder_path):
        if file.endswith(".docx"):
            # 构造完整的文件路径
            file_path = os.path.join(folder_path, file)
            # 打开Word文档
            doc = Document(file_path)
            # 读取文档中的所有段落
            full_text = '\n'.join([para.text for para in doc.paragraphs])
            # 使用正则表达式匹配内容
            matches = re.findall(regex_pattern, full_text, re.DOTALL)
            matches[0] = matches[0].replace('\n', '')
            if matches:
                extracted_contents.extend(matches)
            name_list.append(file.replace(".docx", ""))
    return extracted_contents, name_list


def get_answer_from_docx_glm(extracted_contents, prompt1, name_list, model, tokenizer):
    df_dic = {
        "私募名称": name_list,
        "因子组成": [],
    }
    temporary_list = []
    for text in extracted_contents:
        response, his = model.chat(tokenizer, get_prompt(text, prompt1), history=[], temperature=0.1)
        temporary_list.append(response)
        df_dic['因子组成'].append(response)
    return pd.DataFrame(df_dic), temporary_list


def get_answer_from_docx_baichuan(extracted_contents, yaml_list, name_list, model):
    # 读取 n 个yaml_list中的元素，并创建字典
    df_dic = {
        "私募名称": name_list
    }
    for prompt_class in yaml_list:
        df_dic[prompt_class] = []

    # 按照 yaml_list中的要求，提取prompt并使用大语言模型
    for text in extracted_contents:
        for prompt_class in yaml_list:
            prompt = get_prompt_configs(prompt_class)
            response = model(get_prompt_baichuan(text, prompt))
            df_dic[prompt_class].append(response['response'])
    return pd.DataFrame(df_dic)


def get_prompt_configs(prompt_class):
    with open('configs/prompts.yaml', 'r', encoding='utf-8') as file:
        config = yaml.safe_load(file)
    return config[prompt_class].replace('\n', '')


def get_text_configs(text_class):
    with open('configs/content_extraction.yaml', 'r', encoding='utf-8') as file:
        config = yaml.safe_load(file)
    return config[text_class].replace('\n', '').replace('"', '')
