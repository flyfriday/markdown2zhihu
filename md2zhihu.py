import re
import os
from functools import wraps

def task(priority=0):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        wrapper._is_task = True
        wrapper._priority = priority
        return wrapper
    return decorator

class MD2Zhihu:
    def __init__(self, encoding=None):
        self.tasks = self._collect_and_sort_tasks()
        self.encoding = encoding
    
    def _collect_and_sort_tasks(self):
        tasks = []
        for attr_name in dir(self):
            if attr_name.startswith('__'):
                continue
            attr = getattr(self, attr_name)
            if callable(attr) and hasattr(attr, '_is_task'):
                tasks.append(attr)
        
        tasks.sort(key=lambda x: getattr(x, '_priority', 0))
        return tasks
    
    @task(priority=0)
    def process_latex_formula(self, content):
        def replacer(match):
            content = match.group(1).strip()  # 去除首尾空白字符
            return f"$$ {content} $$"
        # `re.DOTALL` 让 `.*?` 可以匹配换行符
        content = re.sub(r'\$\s*(.*?)\s*\$', replacer, content, flags=re.DOTALL)
        return content

    # @task(priority=1)
    # def process_test(self, content):
    #     content = content.replace("    ", "&ensp;&ensp;&ensp;&ensp;")
    #     content = content.replace("\n", "<br>")
    #     return content


    # @task(priority=0)
    # def process_(self, content):
    #     """
    #     对Markdown内容进行格式化：
    #     1. 去除每行开头的空格。
    #     2. 将有序列表标记 'N. ' 替换为 'N) '。
    #     3. 确保代码块前后有空行。
    #     4. 确保每个被修改的有序列表项后都有一个空行。
    #     """
    #     # 使用 splitlines() 而不是 keepends=True，让我们能完全控制换行符
    #     input_lines = content.splitlines()
    #     output_lines = []
        
    #     in_code_block = False
        
    #     for i, line in enumerate(input_lines):
    #         # 步骤 1: 去除行首空格
    #         # stripped_line = line.lstrip()
    #         stripped_line = line
            
    #         is_fence_line = re.match(r"^(```|~~~)", stripped_line)

    #         # 步骤 3: 确保代码块前后有空行
    #         if is_fence_line:
    #             if not in_code_block: 
    #                 # 进入代码块前，如果上一行不是空行，则添加
    #                 if output_lines and output_lines[-1].strip() != '':
    #                     output_lines.append("")
    #                 output_lines.append(stripped_line)
    #                 in_code_block = True
    #             else: 
    #                 output_lines.append(stripped_line)
    #                 in_code_block = False
    #                 # 退出代码块后，如果下一行不是空行，则添加
    #                 if (i + 1 < len(input_lines) and input_lines[i+1].strip() != ''):
    #                     output_lines.append("")
    #         else:
    #             # 步骤 2 & 4: 处理有序列表并确保其后有空行
    #             ol_match = re.match(r"^(\s*)(\d+)\.\s*(.*)", stripped_line)
    #             if ol_match and not in_code_block:
    #                 leading_spaces = ol_match.group(1)
    #                 number = ol_match.group(2)
    #                 content = ol_match.group(3)
    #                 # 重新构建行
    #                 if leading_spaces:
    #                     processed_line = f"&ensp;&ensp;{ol_match.group(2)}) {ol_match.group(3)}"
    #                 else:
    #                     processed_line = f"{ol_match.group(2)}) {ol_match.group(3)}"
    #                 output_lines.append(processed_line)
    #                 # ***核心修正***: 无条件地在被修改的列表项后添加一个空行
    #                 output_lines.append("")
    #             else:
    #                 # 对于所有其他行，直接添加
    #                 output_lines.append(stripped_line)

    #     # 将所有行用 \n 连接起来
    #     finalized_content = "\n ".join(output_lines)
        
    #     # 最终全局清理：将三个或更多连续的换行符压缩为两个（即一个标准空行）
    #     # 这会修复由于强制添加空行而可能产生的 \n\n\n 情况
    #     final_processed_content = re.sub(r'\n{3,}', '\n\n', finalized_content)
        
    #     # 确保文件以单个换行符结尾，并移除末尾所有空白
    #     return final_processed_content.strip() + '\n'


    def __call__(self):
        save_dir = "processed_data"
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
        raw_md_path = os.listdir("data/")
        for raw_name in raw_md_path:
            save_name = os.path.join(save_dir, "processed_"+raw_name)

            if not (raw_name.endswith(".txt") or raw_name.endswith(".md")):
                return False, "only support .txt or .md"


            if self.encoding is None:
                import chardet
                with open(os.path.join("data", raw_name), "rb") as f:
                    s = f.read()
                    chatest = chardet.detect(s)
                    self.encoding = chatest['encoding']

            with open(os.path.join("data", raw_name), "r", encoding=self.encoding) as f:
                content = f.read()

            for i, task_func in enumerate(self.tasks, 1):
                print(f"task {i}: {task_func.__name__} (priority: {task_func._priority})")
                content = task_func(content)

            with open(save_name, "w", encoding=self.encoding) as f:
                f.write(content)            


def replace_markdown_equation(source_file:str, target_file:str, enable_tag=True):
    if not (source_file.endswith(".txt") or source_file.endswith(".md")):
        return False, "文件格式问题，仅仅支持txt或md"

    with open(source_file, "r", encoding="utf-8") as f:
        content = f.read()

    # line_equations_format = re.compile(r'\$\$(.*?)\$\$', re.S)  #最小匹配
    # line_equations = re.findall(line_equations_format, content)
    # for index, line_equation in enumerate(line_equations):
    #     tag = "\\tag{" + str(index+1) + "}" if enable_tag and "\\tag" not in line_equation else ""
    #     prev_eq = "$${}$$".format(line_equation)
    #     new_eq = "\n{}\n".format(PATH.format(line_equation+tag, line_equation+tag))
    #     content = content.replace(prev_eq, new_eq)
    # inline_equations_format = re.compile(r'\$(.*?)\$', re.S)  # 最小匹配
    # inline_equations = re.findall(inline_equations_format, content)
    # breakpoint()
    # for index, inline_equation in enumerate(inline_equations):
    #     prev_eq = "${}$".format(inline_equation)
    #     new_eq = "$${}$$".format(inline_equation)
    #     content = content.replace(prev_eq, new_eq)
    def replacer(match):
        content = match.group(1).strip()  # 去除首尾空白字符
        return f"$$ {content} $$"

    # `re.DOTALL` 让 `.*?` 可以匹配换行符
    content = re.sub(r'\$\s*(.*?)\s*\$', replacer, content, flags=re.DOTALL)
    # content = remove_extra_newlines(content)
    with open(target_file, "w", encoding="utf-8") as f:
        f.write(content)


if __name__ == "__main__":
    s = "DDPM.md" # 修改前的文件路径
    t = "after_DDPM.md"  # 修改后的文件路径

    # 使用示例
    priority_manager = MD2Zhihu()
    priority_manager()
    # replace_markdown_equation(s, t, True)