import tkinter as tk
from tkinter import ttk
import re

class TextGrid:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("文字排版工具")
        
        # 创建主框架，用于左右分列
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 左侧功能区
        self.control_frame = ttk.Frame(main_frame)
        self.control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        
        # 文本输入和基本设置（第一行）
        ttk.Label(self.control_frame, text="输入文字：").grid(row=0, column=0)
        self.text_input = tk.Text(self.control_frame, width=60, height=20, wrap=tk.WORD)  # 更大的文本框，启用自动换行
        self.text_input.grid(row=0, column=1, columnspan=3, pady=(0, 10))
        
        # 网格设置（第二行）
        ttk.Label(self.control_frame, text="横向格数：").grid(row=1, column=0)
        self.cols_var = tk.StringVar(value="5")
        self.cols_entry = ttk.Entry(self.control_frame, textvariable=self.cols_var, width=10)
        self.cols_entry.grid(row=1, column=1)
        
        ttk.Label(self.control_frame, text="纵向格数：").grid(row=1, column=2)
        self.rows_var = tk.StringVar(value="5")
        self.rows_entry = ttk.Entry(self.control_frame, textvariable=self.rows_var, width=10)
        self.rows_entry.grid(row=1, column=3)
        
        # 字符大小设置（第三行）
        ttk.Label(self.control_frame, text="字符大小比例：").grid(row=2, column=0)
        self.size_ratio_var = tk.StringVar(value="0.8")
        self.size_ratio_entry = ttk.Entry(self.control_frame, textvariable=self.size_ratio_var, width=10)
        self.size_ratio_entry.grid(row=2, column=1)
        
        # 在按钮区域添加翻页按钮（第四行）
        button_frame = ttk.Frame(self.control_frame)
        button_frame.grid(row=3, column=0, columnspan=4, pady=10)
        
        self.prev_page_btn = ttk.Button(button_frame, text="上一页", command=self.prev_page)
        self.prev_page_btn.pack(side=tk.LEFT, padx=5)
        
        self.update_btn = ttk.Button(button_frame, text="更新", command=self.update_text)
        self.update_btn.pack(side=tk.LEFT, padx=5)
        
        self.next_page_btn = ttk.Button(button_frame, text="下一页", command=self.next_page)
        self.next_page_btn.pack(side=tk.LEFT, padx=5)
        
        self.save_btn = ttk.Button(button_frame, text="保存为PNG", command=self.save_canvas)
        self.save_btn.pack(side=tk.LEFT, padx=5)
        
        # 添加页码显示（第五行）
        info_frame = ttk.Frame(self.control_frame)
        info_frame.grid(row=4, column=0, columnspan=4)
        
        self.char_count_var = tk.StringVar(value="字数：0")
        self.char_count_label = ttk.Label(info_frame, textvariable=self.char_count_var)
        self.char_count_label.pack(side=tk.LEFT, padx=10)
        
        self.page_var = tk.StringVar(value="第1页/共1页")
        self.page_label = ttk.Label(info_frame, textvariable=self.page_var)
        self.page_label.pack(side=tk.LEFT, padx=10)
        
        self.overflow_var = tk.StringVar(value="溢出字符：0")
        self.overflow_label = ttk.Label(info_frame, textvariable=self.overflow_var)
        self.overflow_label.pack(side=tk.LEFT, padx=10)
        
        # 创建更大的画布
        # 右侧渲染区（画布）
        canvas_frame = ttk.Frame(main_frame)
        canvas_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.canvas = tk.Canvas(canvas_frame, width=1200, height=1000, bg='white')
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # 删除原来的画布代码
        # self.canvas = tk.Canvas(self.root, width=800, height=800, bg='white')
        # self.canvas.pack(pady=10, padx=10)
        
        self.filtered_text = ""
        self.current_page = 1
        self.total_pages = 1
        self.spaces = set()
        
        # 绑定右键事件
        self.canvas.bind('<Button-3>', self.add_space)

    def prev_page(self):
        if self.current_page > 1:
            self.current_page -= 1
            self.draw_grid()

    def next_page(self):
        if self.current_page < self.total_pages:
            self.current_page += 1
            self.draw_grid()

    def filter_text(self, text):
        # 匹配汉字、日文假名、韩文谚文，排除中点符号
        pattern = r'[\u4e00-\u9fff\u3040-\u309f\u30a0-\u30ff\uac00-\ud7af]+'
        matches = re.findall(pattern, text)
        filtered = ''.join(matches)
        return filtered.replace('·', '')  # 移除中点符号
    
    def add_space(self, event):
        # 计算点击的格子位置
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        cols = int(self.cols_var.get())
        rows = int(self.rows_var.get())
        
        # 为序号预留边距
        margin = 30
        grid_width = width - margin * 2
        grid_height = height - margin * 2
        
        cell_width = grid_width / cols
        cell_height = grid_height / rows
        
        # 调整点击坐标以适应边距
        adjusted_x = event.x - margin
        adjusted_y = event.y - margin
        
        # 检查点击是否在网格范围内
        if adjusted_x < 0 or adjusted_y < 0 or adjusted_x > grid_width or adjusted_y > grid_height:
            return
        
        # 获取点击位置对应的格子索引
        col = int(adjusted_x // cell_width)
        row = int(adjusted_y // cell_height)
        
        # 计算在当前页中的位置
        chars_per_page = rows * cols
        page_offset = (self.current_page - 1) * chars_per_page
        index = page_offset + row + (cols - 1 - col) * rows
        
        # 更新空格位置集合
        if index in self.spaces:
            self.spaces.remove(index)
        else:
            self.spaces.add(index)
        
        self.draw_grid()

    def draw_grid(self):
        self.canvas.delete("all")
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        
        cols = int(self.cols_var.get())
        rows = int(self.rows_var.get())
        
        # 为序号预留边距
        margin = 30
        grid_width = width - margin * 2
        grid_height = height - margin * 2
        
        cell_width = grid_width / cols
        cell_height = grid_height / rows
        
        # 绘制网格和序号
        for i in range(cols + 1):
            x = margin + i * cell_width
            # 绘制竖线
            self.canvas.create_line(x, margin, x, height - margin, fill='gray')
            if i < cols:  # 添加数字序号
                self.canvas.create_text(x + cell_width/2, margin/2,
                                     text=str(cols-i), font=('Arial', 12))
        
        for i in range(rows + 1):
            y = margin + i * cell_height
            # 绘制横线
            self.canvas.create_line(margin, y, width - margin, y, fill='gray')
            if i < rows:  # 添加数字序号
                self.canvas.create_text(width - margin/2, y + cell_height/2,
                                     text=str(i+1), font=('Arial', 12))
        
        chars_per_page = rows * cols
        self.total_pages = max(1, (len(self.filtered_text) + chars_per_page - 1) // chars_per_page)
        start_idx = (self.current_page - 1) * chars_per_page
        end_idx = start_idx + chars_per_page
        
        # 创建带空格的显示文本
        display_chars = []
        current_pos = start_idx  # 修改：从当前页的起始位置开始
        
        for i in range(start_idx, end_idx):
            if i in self.spaces:
                display_chars.append("")
            elif current_pos < len(self.filtered_text):
                display_chars.append(self.filtered_text[current_pos])
                current_pos += 1
            else:
                display_chars.append("")  # 添加空字符串填充剩余空间
        
        # 更新页码显示
        self.page_var.set(f"第{self.current_page}页/共{self.total_pages}页")
        
        # 绘制文字
        font_size = min(cell_width, cell_height) * float(self.size_ratio_var.get())
        font = ('SimSun', int(font_size))
        
        for i, char in enumerate(display_chars):
            if not char:  # 跳过空格
                continue
            row = i % rows
            col = cols - 1 - (i // rows)
            
            x = margin + col * cell_width + cell_width/2
            y = margin + row * cell_height + cell_height/2
            
            self.canvas.create_text(x, y, text=char, 
                                  font=font,
                                  anchor='center')

    def update_text(self):
        # 从Text组件获取文本
        text = self.text_input.get('1.0', 'end-1c')
        self.filtered_text = self.filter_text(text)
        self.char_count_var.set(f"字数：{len(self.filtered_text)}")
        self.current_page = 1
        self.spaces.clear()  # 清除所有空格位置
        self.draw_grid()
    
    def run(self):
        # 绑定画布大小变化事件
        self.canvas.bind('<Configure>', lambda e: self.draw_grid())
        self.root.mainloop()

    def save_canvas(self):
        from PIL import Image, ImageGrab
        import datetime
        import os
        
        # 获取当前时间
        now = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 获取前五个字作为文件名
        cols = int(self.cols_var.get())
        rows = int(self.rows_var.get())
        chars_per_page = rows * cols
        start_idx = (self.current_page - 1) * chars_per_page
        
        # 获取当前页的前五个字
        display_text = ""
        char_count = 0
        current_pos = start_idx  # 修正：从当前页开始
        
        for i in range(start_idx, start_idx + chars_per_page):
            if i in self.spaces:
                continue
            elif current_pos < len(self.filtered_text):
                display_text += self.filtered_text[current_pos]
                current_pos += 1
                char_count += 1
                if char_count >= 5:
                    break
        
        filename = f"{now}_{display_text[:5]}.png"
        
        # 获取画布的位置信息
        x = self.canvas.winfo_rootx()
        y = self.canvas.winfo_rooty()
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        
        # 直接截取画布区域
        image = ImageGrab.grab(bbox=(x, y, x+width, y+height))
        image.save(filename)

if __name__ == "__main__":
    app = TextGrid()
    app.run()