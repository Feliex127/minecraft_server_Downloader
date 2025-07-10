import os
import requests
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from threading import Thread, Event
import webbrowser
import sys

class MinecraftServerDownloader:
    def __init__(self, root):
        self.root = root
        self.root.title("Minecraft 服务器下载器 v2.4")
        self.root.geometry("760x650")
        self.root.resizable(False, False)
        
        # 取消下载事件
        self.cancel_event = Event()
        
        # 服务器类型和获取函数映射
        self.server_types = {
            "Vanilla (原版)": self.get_vanilla_url,
            "Paper (插件)": self.get_paper_url,
            "Fabric (模组)": self.get_fabric_url
        }
        
        # 变量初始化
        self.selected_version = tk.StringVar()
        self.selected_server_type = tk.StringVar()
        self.download_path = tk.StringVar()
        self.memory = tk.StringVar(value="4G")
        self.server_name = tk.StringVar(value="minecraft_server")
        self.eula = tk.BooleanVar(value=False)
        self.downloading = False
        
        self.setup_ui()
        self.set_default_path()

    def set_default_path(self):
        """设置默认下载路径（桌面/Minecraft_Servers）"""
        desktop = os.path.join(os.path.expanduser("~"), "Desktop")
        server_dir = os.path.join(desktop, "Minecraft_Servers")
        self.download_path.set(server_dir)

    def setup_ui(self):
        """初始化用户界面"""
        style = ttk.Style()
        style.configure('TButton', font=('Microsoft YaHei', 10))
        style.configure('Title.TLabel', font=('Microsoft YaHei', 12, 'bold'))
        style.configure('Link.TLabel', foreground="blue", font=('Microsoft YaHei', 9, 'underline'))

        main_frame = ttk.Frame(self.root, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 标题
        ttk.Label(
            main_frame, 
            text="Minecraft 服务器下载器", 
            style='Title.TLabel'
        ).grid(row=0, column=0, columnspan=2, pady=(0, 15))

        # 服务器类型选择
        ttk.Label(main_frame, text="服务器类型:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.server_type_combo = ttk.Combobox(
            main_frame, 
            textvariable=self.selected_server_type, 
            values=list(self.server_types.keys()),
            state="readonly",
            width=28
        )
        self.server_type_combo.grid(row=1, column=1, sticky=tk.EW, padx=5, pady=5)
        self.server_type_combo.bind("<<ComboboxSelected>>", self.update_versions)
        self.selected_server_type.set(list(self.server_types.keys())[0])

        # 版本选择
        ttk.Label(main_frame, text="Minecraft 版本:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.version_combo = ttk.Combobox(
            main_frame, 
            textvariable=self.selected_version, 
            state="readonly",
            width=28
        )
        self.version_combo.grid(row=2, column=1, sticky=tk.EW, padx=5, pady=5)

        # 下载路径
        ttk.Label(main_frame, text="下载路径:").grid(row=3, column=0, sticky=tk.W, pady=5)
        path_frame = ttk.Frame(main_frame)
        path_frame.grid(row=3, column=1, sticky=tk.EW, padx=5, pady=5)
        ttk.Entry(path_frame, textvariable=self.download_path, width=33).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(path_frame, text="浏览", command=self.browse_path, width=8).pack(side=tk.LEFT, padx=5)

        # 服务器设置
        ttk.Label(main_frame, text="服务器名称:").grid(row=4, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.server_name, width=38).grid(row=4, column=1, sticky=tk.W, padx=5, pady=5)

        ttk.Label(main_frame, text="分配内存 (單位請用G 不要小數點 注意:G要大寫):").grid(row=5, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.memory, width=38).grid(row=5, column=1, sticky=tk.W, padx=5, pady=5)

        # EULA 同意
        eula_frame = ttk.Frame(main_frame)
        eula_frame.grid(row=6, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        ttk.Checkbutton(
            eula_frame, 
            text="我同意 Minecraft EULA", 
            variable=self.eula,
            onvalue=True, 
            offvalue=False
        ).pack(side=tk.LEFT)

        # EULA 条款链接
        eula_link = ttk.Label(
            eula_frame, 
            text="(查看EULA条款)", 
            style='Link.TLabel',
            cursor="hand2"
        )
        eula_link.pack(side=tk.LEFT, padx=5)
        eula_link.bind("<Button-1>", lambda e: webbrowser.open("https://www.minecraft.net/zh-hans/eula"))

        # 按钮框架
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=7, column=0, columnspan=2, pady=15)

        self.download_btn = ttk.Button(
            button_frame, 
            text="下载服务器", 
            command=self.start_download_thread,
            style='TButton',
            width=15
        )
        self.download_btn.pack(side=tk.LEFT, padx=5)

        self.cancel_btn = ttk.Button(
            button_frame, 
            text="取消下载", 
            command=self.cancel_download,
            state=tk.DISABLED,
            width=15
        )
        self.cancel_btn.pack(side=tk.LEFT, padx=5)

        # 进度条
        self.progress = ttk.Progressbar(
            main_frame, 
            orient=tk.HORIZONTAL, 
            mode='determinate',
            length=450
        )
        self.progress.grid(row=8, column=0, columnspan=2, pady=10)

        # 状态标签
        self.status_label = ttk.Label(
            main_frame, 
            text="准备就绪", 
            foreground="gray",
            wraplength=550
        )
        self.status_label.grid(row=9, column=0, columnspan=2, sticky=tk.W)

        # 版权信息
        ttk.Label(
            main_frame, 
            text="© 2025 feliex127 | 支持: 原版(Vanilla)/紙(paper)/織布(Fabric)", 
            foreground="gray"
        ).grid(row=10, column=0, columnspan=2, pady=(20, 0))

        # 初始化版本列表
        self.update_versions()

    def browse_path(self):
        """选择下载路径"""
        path = filedialog.askdirectory()
        if path:
            self.download_path.set(path)

    def start_download_thread(self):
        """启动下载线程"""
        if not self.downloading:
            self.cancel_event.clear()
            Thread(target=self.download_server, daemon=True).start()

    def cancel_download(self):
        """取消下载"""
        if self.downloading:
            self.cancel_event.set()
            self.status_label.config(text="正在取消下载...", foreground="orange")

    def update_versions(self, event=None):
        """更新版本列表"""
        server_type = self.selected_server_type.get()
        if not server_type:
            return

        self.version_combo.set('')
        self.version_combo['values'] = []
        self.status_label.config(text="获取版本列表中...", foreground="blue")

        Thread(target=self.fetch_versions, daemon=True).start()

    def fetch_versions(self):
        """获取服务器版本列表"""
        try:
            server_type = self.selected_server_type.get()
            versions = []

            if "Vanilla" in server_type:
                response = requests.get("https://launchermeta.mojang.com/mc/game/version_manifest.json", timeout=10)
                data = response.json()
                versions = [v['id'] for v in data['versions'] if v['type'] == 'release']
            
            elif "Paper" in server_type:
                response = requests.get("https://api.papermc.io/v2/projects/paper", timeout=10)
                data = response.json()
                versions = data['versions'][::-1]
            
            elif "Fabric" in server_type:
                response = requests.get("https://meta.fabricmc.net/v2/versions/game", timeout=10)
                data = response.json()
                versions = [v['version'] for v in data]

            self.root.after(0, self.update_version_combo, versions)
            
        except Exception as e:
            self.root.after(0, self.show_error, f"获取版本失败: {str(e)}")

    def update_version_combo(self, versions):
        """更新版本下拉框"""
        self.version_combo['values'] = versions
        if versions:
            self.version_combo.set(versions[0])
            self.status_label.config(text=f"找到 {len(versions)} 个版本", foreground="green")
        else:
            self.status_label.config(text="未找到可用版本", foreground="red")

    def download_server(self):
        """下载服务器核心"""
        try:
            # 验证输入
            if not self.validate_inputs():
                return

            # 准备下载
            self.prepare_download()

            # 获取下载URL
            jar_url, jar_name = self.get_download_url()
            if not jar_url:
                raise Exception("无法获取下载链接")

            # 下载文件
            success = self.download_file(jar_url, jar_name)
            if not success:
                return

            # 生成必要文件
            self.generate_config_files(jar_name)

            # 完成提示
            self.show_success_message()

        except Exception as e:
            self.show_error(f"下载失败: {str(e)}")
            
        finally:
            self.reset_ui_state()

    def validate_inputs(self):
        """验证用户输入"""
        if not self.selected_version.get():
            self.show_error("请选择Minecraft版本")
            return False
            
        if not self.download_path.get():
            self.show_error("请选择下载路径")
            return False
            
        if not self.eula.get():
            self.show_error("必须同意Minecraft EULA才能下载")
            return False
            
        return True

    def prepare_download(self):
        """准备下载环境"""
        self.downloading = True
        self.download_btn.config(state=tk.DISABLED)
        self.cancel_btn.config(state=tk.NORMAL)
        self.progress['value'] = 0
        self.status_label.config(text="准备下载...", foreground="blue")
        self.root.update()

    def get_download_url(self):
        """获取下载URL"""
        server_type = self.selected_server_type.get()
        version = self.selected_version.get()
        
        try:
            if "Vanilla" in server_type:
                return self.get_vanilla_url(version)
            elif "Paper" in server_type:
                return self.get_paper_url(version)
            elif "Fabric" in server_type:
                return self.get_fabric_url(version)
        except Exception as e:
            self.show_error(f"获取下载链接失败: {str(e)}")
            return None, None

    def get_vanilla_url(self, version):
        """获取官方原版下载URL"""
        manifest_url = "https://launchermeta.mojang.com/mc/game/version_manifest.json"
        response = requests.get(manifest_url, timeout=15)
        response.raise_for_status()
        
        version_data = next((v for v in response.json()['versions'] if v['id'] == version), None)
        if not version_data:
            raise Exception(f"找不到版本 {version}")
        
        version_info = requests.get(version_data['url'], timeout=15).json()
        jar_url = version_info['downloads']['server']['url']
        jar_name = f"server_{version}.jar"
        return jar_url, jar_name

    def get_paper_url(self, version):
        """获取PaperMC下载URL"""
        builds_url = f"https://api.papermc.io/v2/projects/paper/versions/{version}"
        response = requests.get(builds_url, timeout=15)
        response.raise_for_status()
        
        builds = response.json()['builds']
        if not builds:
            raise Exception(f"版本 {version} 没有可用的构建")
        
        latest_build = max(builds)
        jar_url = f"https://api.papermc.io/v2/projects/paper/versions/{version}/builds/{latest_build}/downloads/paper-{version}-{latest_build}.jar"
        jar_name = f"paper-{version}.jar"
        return jar_url, jar_name

    def get_fabric_url(self, version):
        """获取Fabric下载URL"""
        installer_url = "https://meta.fabricmc.net/v2/versions/installer"
        loader_url = "https://meta.fabricmc.net/v2/versions/loader"
        
        # 获取最新安装器
        installers = requests.get(installer_url, timeout=15).json()
        if not installers:
            raise Exception("无法获取Fabric安装器")
        installer_version = installers[0]['version']
        
        # 获取加载器版本
        loaders = requests.get(loader_url, timeout=15).json()
        if not loaders:
            raise Exception("无法获取Fabric加载器")
        loader_version = loaders[0]['version']
        
        jar_url = f"https://meta.fabricmc.net/v2/versions/loader/{version}/{loader_version}/{installer_version}/server/jar"
        jar_name = f"fabric-server-{version}.jar"
        return jar_url, jar_name

    def download_file(self, jar_url, jar_name):
        """下载服务器文件"""
        try:
            # 创建服务器目录
            server_dir = os.path.join(
                self.download_path.get(), 
                f"{self.server_name.get()}_{self.selected_server_type.get().split()[0]}_{self.selected_version.get()}"
            )
            os.makedirs(server_dir, exist_ok=True)
            jar_path = os.path.join(server_dir, jar_name)

            # 开始下载
            self.status_label.config(text=f"正在连接服务器...", foreground="blue")
            self.root.update()

            with requests.get(jar_url, stream=True, timeout=30) as response:
                response.raise_for_status()
                
                # 获取文件大小（防止除零错误）
                total_size = int(response.headers.get('content-length', 0)) or 50 * 1024 * 1024  # 默认50MB
                downloaded = 0
                
                self.status_label.config(text=f"开始下载 {jar_name}...", foreground="blue")
                self.root.update()

                with open(jar_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if self.cancel_event.is_set():
                            if os.path.exists(jar_path):
                                os.remove(jar_path)
                            raise Exception("下载已取消")
                            
                        if chunk:  # 过滤保持活动的空块
                            f.write(chunk)
                            downloaded += len(chunk)
                            progress = min(100, (downloaded / total_size) * 100)
                            self.progress['value'] = progress
                            self.status_label.config(
                                text=f"下载中: {downloaded//1024//1024}MB/{total_size//1024//1024}MB ({progress:.1f}%)",
                                foreground="blue"
                            )
                            self.root.update()

            # 验证下载
            if not os.path.exists(jar_path):
                raise Exception("文件未正确保存")
            if os.path.getsize(jar_path) == 0:
                os.remove(jar_path)
                raise Exception("下载的文件为空")

            return True

        except requests.exceptions.RequestException as e:
            if os.path.exists(jar_path):
                os.remove(jar_path)
            raise Exception(f"网络错误: {str(e)}")
        except Exception as e:
            if 'jar_path' in locals() and os.path.exists(jar_path):
                os.remove(jar_path)
            raise

    def generate_config_files(self, jar_name):
        """生成配置文件和启动脚本"""
        server_dir = os.path.join(
            self.download_path.get(), 
            f"{self.server_name.get()}_{self.selected_server_type.get().split()[0]}_{self.selected_version.get()}"
        )
        
        # 生成启动脚本
        server_type = self.selected_server_type.get().split()[0]
        bat_content = f"""@echo off
title Minecraft {server_type} Server {self.selected_version.get()}
java -Xms{self.memory.get()} -Xmx{self.memory.get()} -jar {jar_name} nogui
pause
"""
        bat_path = os.path.join(server_dir, "啟動伺服器.bat")
        with open(bat_path, 'w', encoding='gbk') as f:
            f.write(bat_content)

        # 生成eula.txt
        if self.eula.get():
            with open(os.path.join(server_dir, "eula.txt"), 'w') as f:
                f.write("eula=true\n")

    def show_success_message(self):
        """显示成功消息"""
        server_dir = os.path.join(
            self.download_path.get(), 
            f"{self.server_name.get()}_{self.selected_server_type.get().split()[0]}_{self.selected_version.get()}"
        )
        
        self.status_label.config(
            text=f"下载完成！服务器已保存到:\n{server_dir}", 
            foreground="green"
        )
        messagebox.showinfo(
            "下载完成", 
            f"服务器文件已成功下载到:\n{server_dir}\n\n双击 啟動伺服器.bat 來启动服务器"
        )

    def show_error(self, message):
        """显示错误信息"""
        self.status_label.config(text=message, foreground="red")
        if "取消" not in message:
            messagebox.showerror("错误", message)

    def reset_ui_state(self):
        """重置UI状态"""
        self.downloading = False
        self.download_btn.config(state=tk.NORMAL)
        self.cancel_btn.config(state=tk.DISABLED)
        self.root.update()

if __name__ == "__main__":
    # 设置Windows高DPI适配
    if sys.platform == 'win32':
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)
    
    root = tk.Tk()
    try:
        # 尝试加载Windows系统主题
        root.tk.call('source', 'azure/azure.tcl')
        root.tk.call('set_theme', 'light')
    except:
        pass  # 如果主题加载失败则使用默认
    
    app = MinecraftServerDownloader(root)
    root.mainloop()