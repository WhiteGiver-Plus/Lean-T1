# Copyright 2024 Bytedance Ltd. and/or its affiliates
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""
Preprocess the nq dataset to parquet format
"""

import re
import os
import datasets

from verl.utils.hdfs_io import copy, makedirs
import argparse


def make_prefix(dp, template_type):
    question = dp['question']

    # NOTE: also need to change reward_score/countdown.py
    if template_type == 'base':
        """This works for any base model"""
        verify_text = ""
        if hasattr(args, 'verify') and args.verify:
            verify_text = "You can also verify your proof by using <verify> your_code </verify> and it will return error messages and 'sorry' information if there are issues. "
            
        prefix = f"""Finish the given Lean4 proof. \
You must conduct reasoning inside <think> and </think> first every time you get new information. \
After reasoning, if you find you need to use a theorem, you can search mathlib4 by <search> math_statement </search> and it will return relevant theorems between <information> and </information>. \
You can search as many times as your want. \
{verify_text}\
If you find no further theorems needed, you can directly provide the completed proof inside <answer> and </answer>. Question: {question}\n"""
    else:
        raise NotImplementedError
    return prefix


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--local_dir', default='./data/lean_tool')
    parser.add_argument('--hdfs_dir', default=None)
    parser.add_argument('--template_type', type=str, default='base')
    parser.add_argument('--verify', action='store_true', help='Enable verification of Lean4 proofs')

    args = parser.parse_args()

    data_source = 'lean_tool'

    # TODO: 修改数据集
    dataset = datasets.load_dataset('RUC-NLPIR/FlashRAG_datasets', 'nq')

    train_dataset = dataset['train']
    test_dataset = dataset['test']

    # add a row to each data item that represents a unique id
    def make_map_fn(split):

        def process_fn(example, idx):
            example['question'] = example['question'].strip()
            if example['question'][-1] != '?':
                example['question'] += '?'
            question = make_prefix(example, template_type=args.template_type)
            solution = {
                "target": example['golden_answers'],
            }

            data = {
                "data_source": data_source,
                "prompt": [{
                    "role": "user",
                    "content": question,
                }],
                "ability": "math",
                "reward_model": {
                    "style": "rule",
                    "ground_truth": solution
                },
                "extra_info": {
                    'split': split,
                    'index': idx,
                }
            }
            return data

        return process_fn

    train_dataset = train_dataset.map(function=make_map_fn('train'), with_indices=True)
    test_dataset = test_dataset.map(function=make_map_fn('test'), with_indices=True)

    local_dir = args.local_dir
    hdfs_dir = args.hdfs_dir

    train_dataset.to_parquet(os.path.join(local_dir, 'train.parquet'))
    test_dataset.to_parquet(os.path.join(local_dir, 'test.parquet'))

    if hdfs_dir is not None:
        makedirs(hdfs_dir)

        copy(src=local_dir, dst=hdfs_dir)
