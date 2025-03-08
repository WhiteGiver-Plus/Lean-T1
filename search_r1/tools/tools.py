import requests
from typing import List
def search_mathlib4(query: List[str], num_results: int = 6):
    url = 'https://console.siflow.cn/siflow/draco/ai4math/zhqin/leansearchif-v1/get_relate_theorems'
    params = {
        'query': query,
        'num': num_results
    }
    response = requests.post(url, json=params)
    
    if response.status_code == 200:
        return response.json()
    else:
        raise RuntimeError(f"Failed to get theorems, status code: {response.status_code}, response: {response.text}")

# Lean4 验证函数
def verify_lean4_code(code: str, timeout: int = 300):
    """Verify Lean4 code."""
    try:
        headers = {
            "Content-Type": "application/json"
        }
        url = "https://console.siflow.cn/siflow/draco/ai4math/zhqin/repl-v1/verify"
        response = requests.post(
            url=url,
            json={"code": code},
            headers=headers,
            timeout=timeout
        )
        if response.status_code == 200:
            result = response.json()
            
            # Process error positions if there are errors

            code_lines = code.split('\n')
            for error in result['errors']:
                if 'pos' in error and 'endPos' in error:
                    start_line = error['pos']['line'] - 1  # 0-indexed
                    start_col = error['pos']['column']
                    end_line = error['endPos']['line'] - 1
                    end_col = error['endPos']['column']
                    
                    # Extract the error context
                    if start_line == end_line:
                        line = code_lines[start_line] if start_line < len(code_lines) else ""
                        if end_col - start_col <= 80:
                            # Show the entire segment if it's short enough
                            error_context = line[start_col:end_col]
                        else:
                            # Show 40 chars before and after
                            start_idx = max(0, start_col)
                            end_idx = min(len(line), end_col)
                            error_context = line[start_idx:start_idx+40] + "..." + line[end_idx-40:end_idx]
                        
                        # Add the error context to the error object
                        error['error_pos'] = error_context
            
            return result
        else:
            return {
                "pass": False,
                "complete": False,
                "system_errors": f"HTTP {response.status_code}: {response.text}"
            }
    except Exception as e:
        return {
            "pass": False,
            "complete": False,
            "system_errors": str(e)
        }

# 测试 search_mathlib4 函数
def test_search_mathlib4():
    # 示例查询关键词
    query = ["continuous function", "derivative"]
    try:
        results = search_mathlib4(query, num_results=5)
        print(f"搜索结果: {results}")
    except Exception as e:
        print(f"搜索失败: {e}")

# 测试 verify_lean4_code 函数
def test_verify_lean4_code():
    # 示例Lean4代码
    lean_code = """

import Mathlib
theorem add_comm (a b : Nat) : a + b = b + a := by
  induction a with
  | zero => simp
  | succ n ih => simp [add_succ, ih]
"""
    try:
        result = verify_lean4_code(lean_code, timeout=60)
        print(f"验证结果: {result}")
        print(f"通过验证: {result.get('pass', False)}")
        if 'errors' in result:
            print(f"错误数量: {len(result['errors'])}")
            for i, error in enumerate(result['errors']):
                print(f"错误 {i+1}: {error}")
    except Exception as e:
        print(f"验证失败: {e}")

# 运行测试
if __name__ == "__main__":
    print("测试 search_mathlib4 函数:")
    test_search_mathlib4()
    
    print("\n测试 verify_lean4_code 函数:")
    test_verify_lean4_code()