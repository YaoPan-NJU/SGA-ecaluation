"""
API评分脚本 - 调用小米mimo-v2.5-pro进行深度化学推理评分
"""
import json
import os
import time
import requests
from typing import Dict, Any
from dotenv import load_dotenv

# 加载.env文件（如果存在）
load_dotenv()

# API配置
API_BASE_URL = os.environ.get("MIMO_API_BASE_URL", "https://token-plan-ams.xiaomimimo.com/v1")
API_MODEL = os.environ.get("MIMO_API_MODEL", "mimo-v2.5-pro")
API_KEY = os.environ.get("MIMO_API_KEY", "")  # 从环境变量或.env文件读取

def build_scoring_prompt(scheme_data: Dict[str, Any], scheme_id: str) -> str:
    """
    构建详细的化学推理评分prompt
    
    Args:
        scheme_data: 方案的JSON数据
        scheme_id: 方案ID (如 "D-03")
    
    Returns:
        完整的prompt文本
    """
    proposal = scheme_data['proposal']
    run_id = scheme_data['run_id']
    
    # 提取关键信息
    steps = proposal.get('steps', [])
    raw_materials = proposal.get('raw_materials', [])
    key_parameters = proposal.get('key_parameters', {})
    equipment = proposal.get('equipment', [])
    safety_notes = proposal.get('safety_notes', [])
    rationale = proposal.get('rationale', '')
    
    # 构建步骤描述
    steps_text = "\n".join([
        f"Step {s['step']}: {s['description'][:200]}{'...' if len(s['description']) > 200 else ''} (温度: {s.get('temperature', 'N/A')}, 时间: {s.get('duration', 'N/A')})"
        for s in steps
    ])
    
    # 构建关键参数
    params_text = ", ".join([f"{k}: {v}" for k, v in key_parameters.items()]) if key_parameters else "无"
    
    prompt = f"""你是一个专业的材料化学专家，请对以下材料合成方案进行严格的李克特量表评分（v1版本，6维度加权评分）。

## 方案信息
**方案ID**: {scheme_id}
**Run ID**: {run_id}

## 合成路线设计理由
{rationale[:500] if rationale else '无'}

## 合成步骤
{steps_text}

## 原料清单
{', '.join(raw_materials) if raw_materials else '无'}

## 关键参数
{params_text}

## 安全注意事项
{'; '.join(safety_notes) if safety_notes else '无'}

## 评分任务

请严格按照以下6个维度进行**深度化学推理**评分，每个维度1-10分：

### D1: 设计到合成的转化准确性 (权重25%)
**评估标准**：
- 9-10分：载体、复合组分、活性位点、形貌、表面特征都有明确合成来源
- 7-8分：主要载体和官能团位点可达；次要结构细节需确认
- 5-6分：可获得相关材料，但几个设计特征缺乏明确的形成路径
- 3-4分：仅能获得大致相似的材料；关键设计特征缺失
- 1-2分：设计与方案明显不匹配

**推理要求**：
1. 识别方案声称要合成的材料（从rationale和步骤推断）
2. 对每个设计特征（载体、复合组分、官能团、形貌），在steps中找到对应的合成路径
3. 评估每个步骤是否真正能生成目标结构（化学上合理吗？）
4. 检查是否所有设计特征都有形成路径

### D2: 反应和工艺参数可行性 (权重25%)
**评估标准**：
- 9-10分：反应化学成熟；前驱体兼容性、工艺参数、后处理条件均有充分论证
- 7-8分：主要反应可能成功，只需有限的条件优化
- 5-6分：化学有合理基础，但接枝效率、副反应或固定稳定性不确定
- 3-4分：关键反应或工艺条件存疑，实验失败风险高
- 1-2分：关键反应内在不一致或基本不可行

**推理要求**：
1. 识别所有关键化学反应（共沉淀、酯化、酰胺化、环氧化、季铵化等）
2. 分析每个反应的条件是否支持该反应机理：
   - pH值是否合理？（如季铵化需要碱性使氨基去质子化）
   - 温度是否合适？（如Fe3O4共沉淀通常70-90°C）
   - 试剂添加顺序正确吗？
3. 评估副反应风险（如ECH在强碱下易水解）
4. 检查前驱体兼容性（不同步骤的试剂会相互干扰吗？）

### D3: 结构控制和质量控制完整性 (权重20%)
**评估标准**：
- 9-10分：结构控制明确，并有适当的表征方法和定量验收标准支撑
- 7-8分：主要结构特征有控制策略和表征方法；部分标准未定量
- 5-6分：提供了一些结构控制逻辑，但QC指标仍为通用描述
- 3-4分：结构声明大多未经可验证的控制路线证实
- 1-2分：目标结构、路线和表征计划脱节

**推理要求**：
1. 列出方案声称的结构特征
2. 检查表征方法是否适合验证所声称的结构：
   - FTIR能检测什么官能团？
   - XRD能验证什么结晶相？
   - BET能确认什么孔隙特征？
3. 评估验收标准的定量性（如"BET > 500 m²/g"是定量，"确认成功"是定性）
4. 检查是否有中间QC检查点

### D4: 批次稳定性和实验可重复性 (权重10%)
**评估标准**：
- 9-10分：参数、关键控制点和中间检查充分定义，具有强批次可重复性
- 7-8分：主要参数清晰，方案通常可重复
- 5-6分：路线可执行，但一些关键参数或工艺窗口未充分说明
- 3-4分：多个步骤依赖隐性经验，造成显著的批次间差异
- 1-2分：关键参数缺失，使重复不切实际

**推理要求**：
1. 检查所有试剂是否有精确用量（g/mL/molarity）
2. 检查关键参数（温度、时间、pH、压力）是否都有明确数值
3. 识别关键控制点（如"缓慢滴加防止局部过热"）
4. 评估参数窗口是否足够窄以保证批次一致性

### D5: 路线简洁性和方法适当性 (权重10%)
**评估标准**：
- 9-10分：路线使用足够简单适当的方法，设备负担低，放大潜力好
- 7-8分：路线复杂度中等，但复杂性主要由目标结构论证
- 5-6分：路线somewhat复杂，某些步骤可简化或替换
- 3-4分：路线过度工程化；高温、高压、惰性气氛或专用步骤缺乏论证
- 1-2分：路线复杂度与目标材料严重不匹配

**推理要求**：
1. 评估步骤数量是否合理（简单材料3-5步，复合材料5-8步）
2. 检查是否有过度复杂化（能否合并步骤？）
3. 评估复杂操作的正当性（如惰性气氛是否因为试剂易氧化？）
4. 评估设备要求是否合理（常规实验室能否实现？）

### D6: 安全性、试剂可获得性和风险缓解 (权重10%)
**评估标准**：
- 9-10分：主要使用易得试剂和可控条件；安全预防措施和废物处理明确指定
- 7-8分：存在常见危害但可控，有充分的保护和废物处理措施
- 5-6分：路线涉及高温、高压、腐蚀性试剂、有机溶剂或中等毒性试剂，需严格管理
- 3-4分：存在高毒性、强氧化性、重金属、含氟废物或管制化学品风险，缓解不足
- 1-2分：安全或合规风险超出标准实验室合理管理能力

**推理要求**：
1. 识别所有主要风险（腐蚀性、毒性、易燃性、氧化性、反应性）
2. 评估缓解措施是否充分且具体（不能只说"在通风橱操作"）
3. 检查废物处理方案是否合理
4. 评估试剂是否容易获取

## 输出格式要求

请严格按以下JSON格式输出评分结果（不要输出其他内容）：

```json
{{
  "scores": {{
    "D1": <整数1-10>,
    "D2": <整数1-10>,
    "D3": <整数1-10>,
    "D4": <整数1-10>,
    "D5": <整数1-10>,
    "D6": <整数1-10>
  }},
  "reasons": {{
    "D1": "<具体理由，必须引用具体步骤编号和参数，说明化学原理，1-3句话>",
    "D2": "<具体理由，必须引用具体步骤编号和参数，说明化学原理，1-3句话>",
    "D3": "<具体理由，必须引用具体步骤编号和参数，说明化学原理，1-3句话>",
    "D4": "<具体理由，必须引用具体步骤编号和参数，说明化学原理，1-3句话>",
    "D5": "<具体理由，必须引用具体步骤编号和参数，说明化学原理，1-3句话>",
    "D6": "<具体理由，必须引用具体步骤编号和参数，说明化学原理，1-3句话>"
  }},
  "weighted_total": <浮点数，计算公式: 25*(D1/10) + 25*(D2/10) + 20*(D3/10) + 10*(D4/10) + 10*(D5/10) + 10*(D6/10)>,
  "grade": "<A/B+/B/C/D，A≥85, B+=75-84, B=65-74, C=55-64, D<55>"
}}
```

**重要要求**：
1. 每个维度的理由必须引用具体步骤编号（如"Step 2"）
2. 每个维度的理由必须说明化学原理（如"碱性条件使氨基去质子化促进SN2反应"）
3. 不能使用"反应化学成熟"、"工艺参数合理"等通用套话
4. 分数必须严格对照量表的5级描述
5. 只输出JSON，不要输出其他内容
"""
    
    return prompt


def call_mimo_api(prompt: str, max_retries: int = 3) -> Dict[str, Any]:
    """
    调用小米mimo API
    
    Args:
        prompt: 评分prompt
        max_retries: 最大重试次数
    
    Returns:
        API返回的JSON数据
    """
    if not API_KEY:
        raise ValueError("MIMO_API_KEY环境变量未设置，请先设置API密钥")
    
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": API_MODEL,
        "messages": [
            {
                "role": "system",
                "content": "你是材料化学专家，擅长材料合成方案的化学推理和评估。请严格按照用户要求进行分析，只输出JSON格式的结果。"
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0.3,  # 较低温度确保输出稳定
        "max_tokens": 2000
    }
    
    for attempt in range(max_retries):
        try:
            response = requests.post(
                f"{API_BASE_URL}/chat/completions",
                headers=headers,
                json=payload,
                timeout=120  # 2分钟超时
            )
            response.raise_for_status()
            
            result = response.json()
            content = result['choices'][0]['message']['content']
            
            # 提取JSON（可能包含markdown代码块）
            if '```json' in content:
                json_str = content.split('```json')[1].split('```')[0].strip()
            elif '```' in content:
                json_str = content.split('```')[1].split('```')[0].strip()
            else:
                json_str = content.strip()
            
            return json.loads(json_str)
            
        except requests.exceptions.RequestException as e:
            print(f"  ⚠️ API调用失败 (尝试 {attempt+1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                time.sleep(5 * (attempt + 1))  # 递增等待
            else:
                raise
        except (json.JSONDecodeError, KeyError) as e:
            print(f"  ⚠️ 解析API响应失败 (尝试 {attempt+1}/{max_retries}): {e}")
            print(f"  原始内容: {content[:200]}...")
            if attempt < max_retries - 1:
                time.sleep(2)
            else:
                raise
    
    # 不应到达这里，但为了类型安全
    raise RuntimeError(f"API调用失败：已重试{max_retries}次")


def score_single_scheme(scheme_data: Dict[str, Any], scheme_id: str, output_dir: str) -> Dict[str, Any]:
    """
    对单个方案进行评分
    
    Args:
        scheme_data: 方案数据
        scheme_id: 方案ID
        output_dir: 输出目录
    
    Returns:
        评分结果
    """
    print(f"\n{'='*60}")
    print(f"评分 {scheme_id}...")
    print('='*60)
    
    # 构建prompt
    prompt = build_scoring_prompt(scheme_data, scheme_id)
    
    # 调用API
    try:
        result = call_mimo_api(prompt)
        
        if result:
            # 验证返回数据结构
            if 'scores' not in result or 'reasons' not in result:
                print(f"❌ {scheme_id} API返回数据格式错误：缺少scores或reasons字段")
                return None
            
            if not all(f'D{i}' in result['scores'] for i in range(1, 7)):
                print(f"❌ {scheme_id} API返回数据格式错误：scores缺少D1-D6")
                return None
            
            # 添加元数据
            result['scheme_id'] = scheme_id
            result['run_id'] = scheme_data['run_id']
            result['group'] = scheme_id.split('-')[0]
            result['index'] = int(scheme_id.split('-')[1])
            result['scored_at'] = time.strftime('%Y-%m-%d %H:%M:%S')
            result['scorer_notes'] = '深度化学推理评分 - mimo-v2.5-pro API'
            
            # 计算验证
            scores = result['scores']
            calculated_total = (
                25 * (scores['D1'] / 10) +
                25 * (scores['D2'] / 10) +
                20 * (scores['D3'] / 10) +
                10 * (scores['D4'] / 10) +
                10 * (scores['D5'] / 10) +
                10 * (scores['D6'] / 10)
            )
            
            # 验证API返回的weighted_total
            if 'weighted_total' not in result:
                result['weighted_total'] = calculated_total
            elif abs(result['weighted_total'] - calculated_total) > 0.01:
                print(f"  ⚠️ {scheme_id} weighted_total计算不匹配，使用计算值: {calculated_total}")
                result['weighted_total'] = calculated_total
            
            result['calculation'] = (
                f"25×{scores['D1']/10} + 25×{scores['D2']/10} + 20×{scores['D3']/10} + "
                f"10×{scores['D4']/10} + 10×{scores['D5']/10} + 10×{scores['D6']/10} = {calculated_total}"
            )
            
            # 保存结果
            group = scheme_id.split('-')[0]
            group_dir = os.path.join(output_dir, f'{group}_group')
            os.makedirs(group_dir, exist_ok=True)
            
            output_file = os.path.join(group_dir, f'{scheme_id}.json')
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            
            print(f"✅ {scheme_id} 评分完成: 总分={result['weighted_total']}, 等级={result['grade']}")
            return result
        else:
            print(f"❌ {scheme_id} 评分失败：API返回为空")
            return None
            
    except Exception as e:
        print(f"❌ {scheme_id} 评分失败：{type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return None


def main():
    """主函数：批量评分"""
    # 路径配置
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    schemes_data_dir = os.path.join(base_dir, '03_schemes_data')
    results_dir = os.path.join(base_dir, '04_scoring_results')
    task_queue_file = os.path.join(base_dir, '01_task_queue.json')
    
    # 加载任务队列
    with open(task_queue_file, 'r', encoding='utf-8') as f:
        task_queue = json.load(f)
    
    # 获取待评分任务
    pending_tasks = [t for t in task_queue['task_queue'] if t['status'] == 'pending']
    print(f"\n📋 待评分任务: {len(pending_tasks)} 个")
    
    if not pending_tasks:
        print("✅ 所有任务已完成！")
        return
    
    # 连续评分
    completed = 0
    failed = 0
    
    for task in pending_tasks:
        scheme_id = task['id']
        group = task['group']
        index = task['index']
        
        # 加载方案数据
        scheme_file = os.path.join(schemes_data_dir, f'{group}_schemes.json')
        with open(scheme_file, 'r', encoding='utf-8') as f:
            schemes = json.load(f)
        
        if index - 1 < len(schemes):
            scheme_data = schemes[index - 1]
            
            # 评分
            result = score_single_scheme(scheme_data, scheme_id, results_dir)
            
            if result:
                # 更新任务状态
                task['status'] = 'completed'
                completed += 1
                
                # 保存任务队列
                with open(task_queue_file, 'w', encoding='utf-8') as f:
                    json.dump(task_queue, f, ensure_ascii=False, indent=2)
            else:
                failed += 1
                print(f"⚠️ {scheme_id} 评分失败，跳过")
        else:
            print(f"⚠️ {scheme_id} 方案数据不存在")
            failed += 1
        
        # 避免API限流，每次调用间隔2秒
        time.sleep(2)
    
    # 总结
    print(f"\n{'='*60}")
    print(f"📊 评分完成总结")
    print('='*60)
    print(f"成功: {completed} 个")
    print(f"失败: {failed} 个")
    print(f"总计: {completed + failed} 个")
    print(f"\n结果保存在: {results_dir}")
    print(f"任务队列已更新: {task_queue_file}")


if __name__ == '__main__':
    main()
