import os
import re
from docx import Document
import pandas as pd

def get_prompt(text,prompt):
    return prompt.replace('xxxxxx',text)

def get_prompt_baichuan(text,prompt):
    messages = []
    messages.append({"role": "user", "content": get_prompt(text,prompt)})
    return messages

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
            matches[0] = matches[0].replace('\n','')
            if matches:
                extracted_contents.extend(matches)
            name_list.append(file.replace(".docx",""))
    return extracted_contents, name_list

def get_answer_from_docx(extracted_contents,prompt1,name_list,model,tokenizer):
    df_dic = {
        "私募名称":name_list,
        "因子组成":[],
    }
    temporary_list = []
    for text in extracted_contents:
        response, his = model.chat(tokenizer, get_prompt(text,prompt1), history=[],temperature=0.1)
        temporary_list.append(response)
        df_dic['因子组成'].append(response)
    return pd.DataFrame(df_dic),temporary_list

def get_answer_from_docx_baichuan(extracted_contents,prompt,name_list,model):
    df_dic = {
        "私募名称":name_list,
        "因子组成":[],
    }
    for text in extracted_contents:
        response = model(get_prompt_baichuan(text,prompt))
        df_dic['因子组成'].append(response['response'])
    return pd.DataFrame(df_dic)

