import pandas as pd
from sqlalchemy import create_engine
import yaml


class LLMAnalyzer:
    def __init__(self):
        # 初始化数据库连接配置
        self.db_username = 'paipai'
        self.db_password = 'qweyang77'
        self.db_host = '192.168.0.98:1215'  # 数据库服务器IP和端口
        self.db_name = 'paipai'
        # 创建数据库引擎
        self.engine = create_engine(
            f'mysql+pymysql://{self.db_username}:{self.db_password}@{self.db_host}/{self.db_name}')

        # 配置字段映射字典，用于将提问类型映射到数据库字段
        self.prompts_match_dic = {
            '因子组成': '配置逻辑',
            '因子挖掘': '配置逻辑',
            '模型种类': '配置逻辑',
            '选股范围': '配置逻辑+持仓特征',
            '交易频率': '交易风格',
            '持股数量': '持仓特征'
        }

        # 配置内容提取字典，指定如何从数据库表中提取内容
        self.dic_content_extraction = {
            '配置逻辑': '配置逻辑',
            '公司概况': '公司概况',
            '交易风格': '交易风格',
            '持仓特征': '持仓特征',
            '配置逻辑+持仓特征': '配置逻辑, 持仓特征'
        }

    @staticmethod
    def get_prompt_configs(prompt_class):
        # 读取并解析 prompts.yaml 配置文件
        with open('configs/prompts.yaml', 'r', encoding='utf-8') as file:
            config = yaml.safe_load(file)
        return config[prompt_class].replace('\n', '')

    @staticmethod
    def get_text_configs(text_class):
        # 读取并解析 content_extraction.yaml 配置文件
        with open('configs/content_extraction.yaml', 'r', encoding='utf-8') as file:
            config = yaml.safe_load(file)
        return config[text_class].replace('\n', '').replace('"', '')

    @staticmethod
    def get_prompt(text, prompt):
        # 替换 prompt 中的占位符xxxxxx为实际文本
        return prompt.replace('xxxxxx', text)

    def get_prompt_baichuan(self, text, prompt):
        # 构造百川需要的消息格式
        messages = [{"role": "user", "content": self.get_prompt(text, prompt)}]
        return messages

    def extract_content_from_mysql(self, prompt_key):
        # 根据指定的键，从数据库中提取相应的列
        columns = self.dic_content_extraction[prompt_key]
        query = f"SELECT `公司名称`, {columns} FROM report_info"
        return pd.read_sql(query, self.engine)

    def get_answer_from_mysql(self, yaml_list, model):
        # 从数据库中获取公司名称列表
        name_list = pd.read_sql("SELECT DISTINCT `公司名称` FROM report_info", self.engine)['公司名称'].tolist()
        df_dic = {"公司名称": name_list}

        # 遍历 yaml 列表，提取和处理数据，然后使用模型生成回应
        for prompt_class in yaml_list:
            df_dic[prompt_class] = []
            prompt = self.get_prompt_configs(prompt_class)
            prompt_key = self.prompts_match_dic[prompt_class]
            extracted_df = self.extract_content_from_mysql(prompt_key)
            responses = []
            for _, row in extracted_df.iterrows():
                prompt_text = ', '.join(
                    [str(row[col]) for col in row.index[1:] if col in self.dic_content_extraction[prompt_key]])
                response = model(self.get_prompt_baichuan(prompt_text, prompt))
                responses.append(response['response'])
            df_dic[prompt_class] = responses

        return pd.DataFrame(df_dic)
