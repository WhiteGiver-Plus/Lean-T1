1. scripts\data_process\nq_search.py进行nswer the given question. \
You must conduct reasoning inside <think> and </think> first every time you get new information. \
After reasoning, if you find you lack some knowledge, you can call a search engine by <search> query </search> and it will return the top searched results between <information> and </information>. \
You can search as many times as your want. \
If you find no further external knowledge needed, you can directly provide the answer inside <answer> and </answer>, without detailed illustrations. For example, <answer> Beijing </answer>. Question: {question}\n

2. search_r1\llm_agent\generation.py 进行工具调用生成
execute_predictions进行工具调用生成
self.batch_search进行batch搜索
3. verl\trainer\main_ppo.py 
class RewardManager()负责奖励函数
data_source = data_item.non_tensor_batch['data_source']
            compute_score_fn = _select_rm_score_fn(data_source)
from verl.utils.reward_score import qa_em
def _select_rm_score_fn(data_source):
    if "nq" in data_source:
        return qa_em.compute_score_em
    else:
        raise NotImplementedError

4. verl\utils\reward_score\qa_em.py
   实现最终奖励判定 改为lean.py