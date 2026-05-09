"""
方案解析脚本 - 从MD文件中提取JSON方案数据
已修复括号不平衡问题
"""
import json
import re
import os

def parse_md_file(filepath):
    """解析MD文件，提取所有方案"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    runs = re.split(r'## 运行结果 \d+:', content)[1:]
    results = []
    
    for run_text in runs:
        run_id_match = re.search(r'(RUN_\d+_\w+)', run_text)
        run_id = run_id_match.group(1) if run_id_match else 'Unknown'
        
        json_match = re.search(r'"final_proposal":\s*(\{.*\})', run_text, re.DOTALL)
        
        if json_match:
            json_str = json_match.group(1).rstrip(',').strip()
            
            # 修复括号不平衡
            brace_count = 0
            for char in json_str:
                if char == '{':
                    brace_count += 1
                elif char == '}':
                    brace_count -= 1
            
            if brace_count > 0:
                json_str = json_str + '}' * brace_count
            
            try:
                proposal = json.loads(json_str)
                results.append({
                    'run_id': run_id,
                    'proposal': proposal
                })
            except json.JSONDecodeError as e:
                print(f"  ✗ {run_id} JSON解析失败: {e}")
    
    return results

# 解析所有组
groups = ['A', 'B', 'C', 'D', 'E', 'F']
base_dir = 'c:/Users/15995/.qoder/test'
output_dir = 'c:/Users/15995/.qoder/test/scoring_project/03_schemes_data'

for group in groups:
    print(f"\n解析 {group}.md...")
    filepath = os.path.join(base_dir, f'{group}.md')
    
    if os.path.exists(filepath):
        schemes = parse_md_file(filepath)
        print(f"  ✓ 成功解析 {len(schemes)} 个方案")
        
        # 保存
        output_file = os.path.join(output_dir, f'{group}_schemes.json')
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(schemes, f, ensure_ascii=False, indent=2)
        print(f"  ✓ 已保存到 {output_file}")
    else:
        print(f"  ✗ 文件不存在: {filepath}")

print("\n✅ 所有方案解析完成！")
