import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import re
import sys
import os
import platform


class PortKillerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("端口进程杀手")
        self.root.geometry("700x500")
        self.root.resizable(True, True)
        
        # 设置窗口图标（如果存在）
        try:
            if getattr(sys, 'frozen', False):
                # 打包后的路径
                icon_path = os.path.join(sys._MEIPASS, 'icon.ico')
            else:
                # 开发环境路径
                icon_path = os.path.join(os.path.dirname(__file__), 'icon.ico')
            
            if os.path.exists(icon_path):
                self.root.iconbitmap(icon_path)
        except:
            pass
        
        # 设置样式
        style = ttk.Style()
        style.theme_use('clam')
        
        # 创建主框架
        main_frame = ttk.Frame(root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置网格权重
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(3, weight=1)
        
        # 标题
        title_label = ttk.Label(main_frame, text="端口进程杀手", font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, pady=(0, 10))
        
        # 输入框框架
        input_frame = ttk.Frame(main_frame)
        input_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=5)
        input_frame.columnconfigure(1, weight=1)
        
        # 端口输入
        ttk.Label(input_frame, text="端口号:", font=("Arial", 10)).grid(row=0, column=0, sticky=tk.W, padx=5)
        self.port_entry = ttk.Entry(input_frame, width=20, font=("Arial", 10))
        self.port_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=5)
        self.port_entry.bind('<Return>', lambda event: self.search_process())
        
        # 按钮框架
        btn_frame = ttk.Frame(input_frame)
        btn_frame.grid(row=0, column=2, padx=5)
        
        # 查找按钮
        search_btn = ttk.Button(btn_frame, text="查找进程", command=self.search_process)
        search_btn.grid(row=0, column=0, padx=2)
        
        # 杀死按钮
        kill_btn = ttk.Button(btn_frame, text="杀死选中进程", command=self.kill_process, style="Danger.TButton")
        kill_btn.grid(row=0, column=1, padx=2)
        
        # 刷新按钮
        refresh_btn = ttk.Button(btn_frame, text="刷新", command=self.refresh_list)
        refresh_btn.grid(row=0, column=2, padx=2)
        
        # 结果列表框架
        list_frame = ttk.Frame(main_frame)
        list_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        
        # 创建Treeview
        columns = ('协议', '本地地址', '外部地址', '状态', 'PID')
        self.tree = ttk.Treeview(list_frame, columns=columns, show='headings', selectmode='browse')
        
        # 定义列标题
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100, anchor=tk.CENTER)
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # 状态栏
        self.status_var = tk.StringVar(value="就绪")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(5, 0))
        
        # 绑定双击事件
        self.tree.bind('<Double-1>', lambda event: self.kill_process())
        
    def search_process(self):
        """查找占用指定端口的进程"""
        port = self.port_entry.get().strip()
        
        if not port or not port.isdigit():
            messagebox.showwarning("警告", "请输入有效的端口号!")
            return
        
        try:
            # 清空现有数据
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            os_name = platform.system()
            lines = []
            
            if os_name == "Windows":
                cmd = f'netstat -ano | findstr ":{port}"'
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True, encoding='gbk')
                if result.stdout:
                    lines = result.stdout.strip().split('\n')
            else:
                # Linux/macOS 使用 lsof 查找端口
                # lsof -i :<port> -P -n
                cmd = f'lsof -i :{port} -P -n'
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True, encoding='utf-8')
                if result.stdout:
                    lines = result.stdout.strip().split('\n')[1:] # 跳过标题行
            
            if not lines or all(not line.strip() for line in lines):
                messagebox.showinfo("提示", f"未找到占用端口 {port} 的进程")
                self.status_var.set(f"未找到占用端口 {port} 的进程")
                return
            
            process_count = 0
            
            for line in lines:
                if not line.strip():
                    continue
                    
                if os_name == "Windows":
                    parts = line.split()
                    if len(parts) >= 5:
                        protocol = parts[0]
                        local_addr = parts[1]
                        foreign_addr = parts[2]
                        status = parts[3] if len(parts) == 5 else ''
                        pid = parts[-1]
                        
                        if f":{port}" in local_addr:
                            self.tree.insert('', tk.END, values=(protocol, local_addr, foreign_addr, status, pid))
                            process_count += 0 # 这里原代码逻辑有点小问题，下面统一加
                else:
                    # Linux lsof 输出格式: COMMAND PID USER FD TYPE DEVICE SIZE/OFF NODE NAME
                    parts = line.split()
                    if len(parts) >= 9:
                        command = parts[0]
                        pid = parts[1]
                        user = parts[2]
                        name = parts[-1] # 通常是 IP:Port
                        
                        # 简单提取状态，lsof不直接显示TCP状态如ESTABLISHED，通常显示为IPv4/IPv6
                        protocol = "TCP" if "TCP" in line else "UDP"
                        local_addr = name 
                        foreign_addr = "-"
                        status = "LISTEN/ESTAB" # lsof不直接显示具体状态，这里简化处理
                        
                        self.tree.insert('', tk.END, values=(protocol, local_addr, foreign_addr, status, pid))
                        process_count += 1

            # 修正Windows下的计数逻辑（原代码在循环内没有正确递增count）
            if os_name == "Windows":
                 process_count = len(self.tree.get_children())

            self.status_var.set(f"找到 {process_count} 个占用端口 {port} 的进程")
            
            if process_count == 0:
                messagebox.showinfo("提示", f"未找到占用端口 {port} 的进程")
        
        except Exception as e:
            messagebox.showerror("错误", f"查找进程时出错:\n{str(e)}")
            self.status_var.set("查找失败")
    def kill_process(self):
        """杀死选中的进程"""
        selected_item = self.tree.selection()
        
        if not selected_item:
            messagebox.showwarning("警告", "请先选择一个进程!")
            return
        
        # 获取选中的进程信息
        item_values = self.tree.item(selected_item[0], 'values')
        pid = item_values[4]
        protocol = item_values[0]
        local_addr = item_values[1]
        
        # 确认对话框
        confirm = messagebox.askyesno(
            "确认",
            f"确定要结束以下进程吗?\n\n"
            f"PID: {pid}\n"
            f"协议: {protocol}\n"
            f"本地地址: {local_addr}\n\n"
            f"此操作不可撤销!"
        )
        
        if not confirm:
            return
        
        try:
            # --- 跨平台杀死进程逻辑开始 ---
            os_name = platform.system()
            
            if os_name == "Windows":
                cmd = f'taskkill /F /PID {pid}'
                encoding = 'gbk'
            else:  # Linux, macOS, etc.
                # Linux/Mac 需要 sudo 权限才能杀死其他用户的进程，这里假设当前用户有权限
                cmd = f'kill -9 {pid}'
                encoding = 'utf-8'
            
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, encoding=encoding)
            # --- 跨平台杀死进程逻辑结束 ---
            
            if result.returncode == 0:
                messagebox.showinfo("成功", f"已成功结束进程 PID: {pid}")
                self.status_var.set(f"已结束进程 PID: {pid}")
                # 刷新列表
                self.refresh_list()
            else:
                # 注意：Linux下如果权限不足，stderr会有提示
                error_msg = result.stderr.strip() if result.stderr else "未知错误"
                messagebox.showerror("失败", f"结束进程失败:\n{error_msg}")
                self.status_var.set("结束进程失败")
        
        except Exception as e:
            messagebox.showerror("错误", f"结束进程时出错:\n{str(e)}")
            self.status_var.set("结束进程失败")
        """杀死选中的进程"""
        selected_item = self.tree.selection()
        
        if not selected_item:
            messagebox.showwarning("警告", "请先选择一个进程!")
            return
        
        # 获取选中的进程信息
        item_values = self.tree.item(selected_item[0], 'values')
        pid = item_values[4]
        protocol = item_values[0]
        local_addr = item_values[1]
        
        # 确认对话框
        confirm = messagebox.askyesno(
            "确认",
            f"确定要结束以下进程吗?\n\n"
            f"PID: {pid}\n"
            f"协议: {protocol}\n"
            f"本地地址: {local_addr}\n\n"
            f"此操作不可撤销!"
        )
        
        if not confirm:
            return
        
        try:
            # 使用taskkill命令结束进程
            cmd = f'taskkill /F /PID {pid}'
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, encoding='gbk')
            
            if result.returncode == 0:
                messagebox.showinfo("成功", f"已成功结束进程 PID: {pid}")
                self.status_var.set(f"已结束进程 PID: {pid}")
                # 刷新列表
                self.refresh_list()
            else:
                messagebox.showerror("失败", f"结束进程失败:\n{result.stderr}")
                self.status_var.set("结束进程失败")
        
        except Exception as e:
            messagebox.showerror("错误", f"结束进程时出错:\n{str(e)}")
            self.status_var.set("结束进程失败")
    
    def refresh_list(self):
        """刷新列表"""
        if self.port_entry.get().strip():
            self.search_process()
        else:
            # 清空现有数据
            for item in self.tree.get_children():
                self.tree.delete(item)
            self.status_var.set("请输入端口号后刷新")


def main():
    root = tk.Tk()
    app = PortKillerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
