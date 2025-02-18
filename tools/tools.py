from loguru import logger
import spacy
from scipy.spatial.distance import cosine
import numpy as np


logger.info("开始加载nlp：spacy zh_core_web_sm")
NLP = spacy.load("zh_core_web_sm")
# 设置相似度阈值
THRESHOLD = 0.7  # 你可以根据实际情况调整这个值
logger.info(f"相似度阈值：{ THRESHOLD}")

def get_vector(text):
    doc = NLP(text)
    return doc.vector  # 返回句子的平均词向量

def get_best_match_response(input_msg,response_vectors,response_list):
    input_msg_vector = get_vector(input_msg)
    similarities = [1 - cosine(input_msg_vector, response_vector) for response_vector in response_vectors]
    
    # 找到最匹配的固定回复
    best_match_index = np.argmax(similarities)
    best_match_response = list(response_list)[best_match_index]
    best_match_similarity = similarities[best_match_index]
    # 判断是否满足阈值
    if best_match_similarity >= THRESHOLD:
        logger.info(f"Matched Response: {best_match_response} (Similarity: {best_match_similarity:.2f})")
        return best_match_response
    else:
        return None