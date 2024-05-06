import pandas as pd
from sqlalchemy import create_engine
import yaml
import logging
from modelscope import Model
import torch

# 配置日志系统，设置日志级别和格式
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class LLMAnalyzer:
    def __init__(self, model_path):
        logging.info("Initializing the LLMAnalyzer")
        # 初始化数据库连接配置，这些信息用于创建数据库引擎
        self.db_username = 'paipai'
        self.db_password = 'qweyang77'
        self.db_host = '192.168.0.98:1215'
        self.db_name = 'paipai'
        self.engine = create_engine(
            f'mysql+pymysql://{self.db_username}:{self.db_password}@{self.db_host}/{self.db_name}')

        # 字典匹配提问类型与数据库字段
        self.prompts_match_dic = {
            '因子组成': '配置逻辑',
            '因子挖掘': '配置逻辑',
            '模型种类': '配置逻辑',
            '选股范围': '配置逻辑+持仓特征',
            '交易频率': '交易风格',
            '持股数量': '持仓特征'
        }

        # 内容提取字典定义从数据库表中提取哪些列
        self.dic_content_extraction = {
            '配置逻辑': '配置逻辑',
            '公司概况': '公司概况',
            '交易风格': '交易风格',
            '持仓特征': '持仓特征',
            '配置逻辑+持仓特征': '配置逻辑, 持仓特征'
        }
        logging.info("LLMAnalyzer initialized successfully")

        self.model = Model.from_pretrained(model_path, device_map="auto", trust_remote_code=True,
                                           torch_dtype=torch.float16)

    @staticmethod
    def get_prompt_configs(prompt_class):
        # 从YAML配置文件中读取并返回对应的提示配置
        try:
            with open('configs/prompts.yaml', 'r', encoding='utf-8') as file:
                config = yaml.safe_load(file)
            return config[prompt_class].replace('\n', '')
        except Exception as e:
            logging.error(f"Error reading prompt configs: {e}")
            return None

    @staticmethod
    def get_text_configs(text_class):
        # 从YAML配置文件中读取并返回对应的文本提取配置
        try:
            with open('configs/content_extraction.yaml', 'r', encoding='utf-8') as file:
                config = yaml.safe_load(file)
            return config[text_class].replace('\n', '').replace('"', '')
        except Exception as e:
            logging.error(f"Error reading text configs: {e}")
            return None

    @staticmethod
    def get_prompt(text, prompt):
        # 使用给定的文本替换提示中的占位符
        return prompt.replace('xxxxxx', text)

    def get_prompt_baichuan(self, text, prompt):
        # 为百川平台构造特定格式的消息
        messages = [{"role": "user", "content": self.get_prompt(text, prompt)}]
        return messages

    def extract_content_from_mysql(self, prompt_key):
        # 根据提供的键从数据库表中提取指定的列
        columns = self.dic_content_extraction[prompt_key]
        query = f"SELECT `公司名称`, {columns} FROM report_info"
        return pd.read_sql(query, self.engine)

    def get_answer_from_mysql(self, yaml_list):
        # 从数据库中获取不重复的公司名称列表
        name_list = pd.read_sql("SELECT DISTINCT `公司名称` FROM report_info", self.engine)['公司名称'].tolist()
        df_dic = {"公司名称": name_list}

        # 遍历yaml列表，执行数据提取和处理，捕捉并记录任何异常
        for prompt_class in yaml_list:
            df_dic[prompt_class] = []
            prompt = self.get_prompt_configs(prompt_class)
            prompt_key = self.prompts_match_dic[prompt_class]
            try:
                extracted_df = self.extract_content_from_mysql(prompt_key)
                responses = []
                for _, row in extracted_df.iterrows():
                    try:
                        prompt_text = ', '.join(
                            [str(row[col]) for col in row.index[1:] if col in self.dic_content_extraction[prompt_key]])
                        response = self.model(self.get_prompt_baichuan(prompt_text, prompt))
                        responses.append(response['response'])
                    except Exception as e:
                        logging.error(f"Error processing row: {e}")
                        continue
                df_dic[prompt_class] = responses
            except Exception as e:
                logging.error(f"Error extracting or processing data for {prompt_class}: {e}")
                continue
        logging.info("Data extraction and processing completed successfully")
        return pd.DataFrame(df_dic)
