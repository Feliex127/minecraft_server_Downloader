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
        
        # 多語言支援
        self.languages = {
            #繁體中文
            "zh_TW": {
                "title": "Minecraft 伺服器下載器",
                "server_type": "伺服器類型:",
                "version": "Minecraft 版本:",
                "download_path": "下載路徑:",
                "browse": "瀏覽",
                "server_name": "伺服器名稱:",
                "memory": "分配記憶體 (如 4G):",
                "eula": "我同意 Minecraft EULA",
                "eula_link": "(查看EULA條款)",
                "download_btn": "下載伺服器",
                "cancel_btn": "取消下載",
                "ready": "準備就緒",
                "fetching": "獲取版本列表中...",
                "versions_found": "找到 {} 個版本",
                "no_versions": "未找到可用版本",
                "downloading": "下載中...",
                "download_complete": "下載完成！伺服器已保存到:\n{}",
                "run_server": "雙擊 start.bat 啟動伺服器",
                "error": "錯誤",
                "canceled": "下載已取消",
                "copyright": "© 2023 Minecraft 伺服器下載器 | 支援: Vanilla/Paper/Fabric",
                "select_version": "請選擇Minecraft版本",
                "select_path": "請選擇下載路徑",
                "accept_eula": "必須同意Minecraft EULA才能下載",
                "download_failed": "下載失敗: {}",
                "connection_error": "網絡錯誤: {}",
                "file_not_saved": "文件未正確保存",
                "empty_file": "下載的文件為空"
            },
            #簡體中文
            "zh_CN": {
                "title": "Minecraft 服务器下载器",
                "server_type": "服务器类型:",
                "version": "Minecraft 版本:",
                "download_path": "下载路径:",
                "browse": "浏览",
                "server_name": "服务器名称:",
                "memory": "分配内存 (如 4G):",
                "eula": "我同意 Minecraft EULA",
                "eula_link": "(查看EULA条款)",
                "download_btn": "下载服务器",
                "cancel_btn": "取消下载",
                "ready": "准备就绪",
                "fetching": "获取版本列表中...",
                "versions_found": "找到 {} 个版本",
                "no_versions": "未找到可用版本",
                "downloading": "下载中...",
                "download_complete": "下载完成！服务器已保存到:\n{}",
                "run_server": "双击 start.bat 启动服务器",
                "error": "错误",
                "canceled": "下载已取消",
                "copyright": "© 2023 Minecraft 服务器下载器 | 支持: Vanilla/Paper/Fabric",
                "select_version": "请选择Minecraft版本",
                "select_path": "请选择下载路径",
                "accept_eula": "必须同意Minecraft EULA才能下载",
                "download_failed": "下载失败: {}",
                "connection_error": "网络错误: {}",
                "file_not_saved": "文件未正确保存",
                "empty_file": "下载的文件为空"
            },
            #英文
            "en": {
                "title": "Minecraft Server Downloader",
                "server_type": "Server Type:",
                "version": "Minecraft Version:",
                "download_path": "Download Path:",
                "browse": "Browse",
                "server_name": "Server Name:",
                "memory": "Memory Allocation (e.g. 4G):",
                "eula": "I agree to Minecraft EULA",
                "eula_link": "(View EULA)",
                "download_btn": "Download Server",
                "cancel_btn": "Cancel Download",
                "ready": "Ready",
                "fetching": "Fetching version list...",
                "versions_found": "Found {} versions",
                "no_versions": "No available versions found",
                "downloading": "Downloading...",
                "download_complete": "Download complete! Saved to:\n{}",
                "run_server": "Double click start.bat to run the server",
                "error": "Error",
                "canceled": "Download canceled",
                "copyright": "© 2023 Minecraft Server Downloader | Supports: Vanilla/Paper/Fabric",
                "select_version": "Please select a Minecraft version",
                "select_path": "Please select download path",
                "accept_eula": "You must agree to Minecraft EULA to download",
                "download_failed": "Download failed: {}",
                "connection_error": "Connection error: {}",
                "file_not_saved": "File not saved correctly",
                "empty_file": "Downloaded file is empty"
            
            }
        }

        # 預設繁體中文
        self.current_lang = "zh_TW"
        self.lang = self.languages[self.current_lang]
        
        self.root.title(self.lang["title"])
        self.root.geometry("720x700")
        self.root.resizable(False, False)
        
        # 取消下載事件
        self.cancel_event = Event()
        
        # 伺服器類型和獲取函數映射
        self.server_types = {
            "Vanilla": self.get_vanilla_url,
            "Paper": self.get_paper_url,
            "Fabric": self.get_fabric_url
        }
        
        # 變數初始化
        self.selected_version = tk.StringVar()
        self.selected_server_type = tk.StringVar()
        self.download_path = tk.StringVar()
        self.memory = tk.StringVar(value="4G")
        self.server_name = tk.StringVar(value="minecraft_server")
        self.eula = tk.BooleanVar(value=False)
        self.downloading = False
        
        # UI元素引用
        self.ui_elements = {}
        
        self.setup_ui()
        self.set_default_path()

    def set_default_path(self):
        """設置預設下載路徑（桌面/Minecraft_Servers）"""
        desktop = os.path.join(os.path.expanduser("~"), "Desktop")
        server_dir = os.path.join(desktop, "Minecraft_Servers")
        self.download_path.set(server_dir)

    def setup_ui(self):
        """初始化用戶界面"""
        style = ttk.Style()
        style.configure('TButton', font=('Microsoft YaHei', 10))
        style.configure('Title.TLabel', font=('Microsoft YaHei', 12, 'bold'))
        style.configure('Link.TLabel', foreground="blue", font=('Microsoft YaHei', 9, 'underline'))

        main_frame = ttk.Frame(self.root, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 語言選擇
        lang_frame = ttk.Frame(main_frame)
        lang_frame.grid(row=0, column=1, sticky=tk.E, pady=(0, 10))
        
        self.lang_var = tk.StringVar(value=self.current_lang)
        lang_menu = ttk.OptionMenu(lang_frame, self.lang_var, self.current_lang, *self.languages.keys(), 
                                 command=self.change_language)
        lang_menu.pack(side=tk.RIGHT)
        self.ui_elements["lang_menu"] = lang_menu

        # 標題
        title_label = ttk.Label(
            main_frame, 
            text=self.lang["title"], 
            style='Title.TLabel'
        )
        title_label.grid(row=0, column=0, sticky=tk.W, pady=(0, 15))
        self.ui_elements["title_label"] = title_label

        # 伺服器類型選擇
        server_type_label = ttk.Label(main_frame, text=self.lang["server_type"])
        server_type_label.grid(row=1, column=0, sticky=tk.W, pady=5)
        self.ui_elements["server_type_label"] = server_type_label
        
        self.server_type_combo = ttk.Combobox(
            main_frame, 
            textvariable=self.selected_server_type, 
            values=list(self.server_types.keys()),
            state="readonly",
            width=25
        )
        self.server_type_combo.grid(row=1, column=1, sticky=tk.EW, padx=5, pady=5)
        self.server_type_combo.bind("<<ComboboxSelected>>", self.update_versions)
        self.selected_server_type.set(list(self.server_types.keys())[0])

        # 版本選擇
        version_label = ttk.Label(main_frame, text=self.lang["version"])
        version_label.grid(row=2, column=0, sticky=tk.W, pady=5)
        self.ui_elements["version_label"] = version_label
        
        self.version_combo = ttk.Combobox(
            main_frame, 
            textvariable=self.selected_version, 
            state="readonly",
            width=25
        )
        self.version_combo.grid(row=2, column=1, sticky=tk.EW, padx=5, pady=5)

        # 下載路徑
        download_path_label = ttk.Label(main_frame, text=self.lang["download_path"])
        download_path_label.grid(row=3, column=0, sticky=tk.W, pady=5)
        self.ui_elements["download_path_label"] = download_path_label
        
        path_frame = ttk.Frame(main_frame)
        path_frame.grid(row=3, column=1, sticky=tk.EW, padx=5, pady=5)
        
        path_entry = ttk.Entry(path_frame, textvariable=self.download_path, width=30)
        path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        browse_btn = ttk.Button(path_frame, text=self.lang["browse"], command=self.browse_path, width=8)
        browse_btn.pack(side=tk.LEFT, padx=5)
        self.ui_elements["browse_btn"] = browse_btn

        # 伺服器設置
        server_name_label = ttk.Label(main_frame, text=self.lang["server_name"])
        server_name_label.grid(row=4, column=0, sticky=tk.W, pady=5)
        self.ui_elements["server_name_label"] = server_name_label
        
        ttk.Entry(main_frame, textvariable=self.server_name, width=35).grid(row=4, column=1, sticky=tk.W, padx=5, pady=5)

        memory_label = ttk.Label(main_frame, text=self.lang["memory"])
        memory_label.grid(row=5, column=0, sticky=tk.W, pady=5)
        self.ui_elements["memory_label"] = memory_label
        
        ttk.Entry(main_frame, textvariable=self.memory, width=35).grid(row=5, column=1, sticky=tk.W, padx=5, pady=5)

        # EULA 同意
        eula_frame = ttk.Frame(main_frame)
        eula_frame.grid(row=6, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        eula_check = ttk.Checkbutton(
            eula_frame, 
            text=self.lang["eula"], 
            variable=self.eula,
            onvalue=True, 
            offvalue=False
        )
        eula_check.pack(side=tk.LEFT)
        self.ui_elements["eula_check"] = eula_check

        # EULA 條款鏈接
        eula_link = ttk.Label(
            eula_frame, 
            text=self.lang["eula_link"], 
            style='Link.TLabel',
            cursor="hand2"
        )
        eula_link.pack(side=tk.LEFT, padx=5)
        eula_link.bind("<Button-1>", lambda e: webbrowser.open("https://www.minecraft.net/zh-hans/eula"))
        self.ui_elements["eula_link"] = eula_link

        # 按鈕框架
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=7, column=0, columnspan=2, pady=15)

        self.download_btn = ttk.Button(
            button_frame, 
            text=self.lang["download_btn"], 
            command=self.start_download_thread,
            style='TButton',
            width=15
        )
        self.download_btn.pack(side=tk.LEFT, padx=5)
        self.ui_elements["download_btn"] = self.download_btn

        self.cancel_btn = ttk.Button(
            button_frame, 
            text=self.lang["cancel_btn"], 
            command=self.cancel_download,
            state=tk.DISABLED,
            width=15
        )
        self.cancel_btn.pack(side=tk.LEFT, padx=5)
        self.ui_elements["cancel_btn"] = self.cancel_btn

        # 進度條
        self.progress = ttk.Progressbar(
            main_frame, 
            orient=tk.HORIZONTAL, 
            mode='determinate',
            length=450
        )
        self.progress.grid(row=8, column=0, columnspan=2, pady=10)

        # 狀態標籤
        self.status_label = ttk.Label(
            main_frame, 
            text=self.lang["ready"], 
            foreground="gray",
            wraplength=550
        )
        self.status_label.grid(row=9, column=0, columnspan=2, sticky=tk.W)
        self.ui_elements["status_label"] = self.status_label

        # 版權信息
        copyright_label = ttk.Label(
            main_frame, 
            text=self.lang["copyright"], 
            foreground="gray"
        )
        copyright_label.grid(row=10, column=0, columnspan=2, pady=(20, 0))
        self.ui_elements["copyright_label"] = copyright_label

        # 初始化版本列表
        self.update_versions()

    def change_language(self, lang_code):
        """切換語言"""
        self.current_lang = lang_code
        self.lang = self.languages[lang_code]
        
        # 更新所有UI文字
        self.root.title(self.lang["title"])
        
        # 更新所有可本地化的UI元素
        self.ui_elements["title_label"].config(text=self.lang["title"])
        self.ui_elements["server_type_label"].config(text=self.lang["server_type"])
        self.ui_elements["version_label"].config(text=self.lang["version"])
        self.ui_elements["download_path_label"].config(text=self.lang["download_path"])
        self.ui_elements["browse_btn"].config(text=self.lang["browse"])
        self.ui_elements["server_name_label"].config(text=self.lang["server_name"])
        self.ui_elements["memory_label"].config(text=self.lang["memory"])
        self.ui_elements["eula_check"].config(text=self.lang["eula"])
        self.ui_elements["eula_link"].config(text=self.lang["eula_link"])
        self.ui_elements["download_btn"].config(text=self.lang["download_btn"])
        self.ui_elements["cancel_btn"].config(text=self.lang["cancel_btn"])
        self.ui_elements["copyright_label"].config(text=self.lang["copyright"])
        
        # 更新狀態標籤
        if not self.downloading:
            self.status_label.config(text=self.lang["ready"])

    def browse_path(self):
        """選擇下載路徑"""
        path = filedialog.askdirectory()
        if path:
            self.download_path.set(path)

    def start_download_thread(self):
        """啟動下載線程"""
        if not self.downloading:
            self.cancel_event.clear()
            Thread(target=self.download_server, daemon=True).start()

    def cancel_download(self):
        """取消下載"""
        if self.downloading:
            self.cancel_event.set()
            self.status_label.config(text=self.lang["canceled"], foreground="orange")

    def update_versions(self, event=None):
        """更新版本列表"""
        server_type = self.selected_server_type.get()
        if not server_type:
            return

        self.version_combo.set('')
        self.version_combo['values'] = []
        self.status_label.config(text=self.lang["fetching"], foreground="blue")

        Thread(target=self.fetch_versions, daemon=True).start()

    def fetch_versions(self):
        """獲取伺服器版本列表"""
        try:
            server_type = self.selected_server_type.get()
            versions = []

            if server_type == "Vanilla":
                response = requests.get("https://launchermeta.mojang.com/mc/game/version_manifest.json", timeout=10)
                data = response.json()
                versions = [v['id'] for v in data['versions'] if v['type'] == 'release']
            
            elif server_type == "Paper":
                response = requests.get("https://api.papermc.io/v2/projects/paper", timeout=10)
                data = response.json()
                versions = data['versions'][::-1]
            
            elif server_type == "Fabric":
                response = requests.get("https://meta.fabricmc.net/v2/versions/game", timeout=10)
                data = response.json()
                versions = [v['version'] for v in data]

            self.root.after(0, self.update_version_combo, versions)
            
        except Exception as e:
            self.root.after(0, self.show_error, self.lang["connection_error"].format(str(e)))

    def update_version_combo(self, versions):
        """更新版本下拉框"""
        self.version_combo['values'] = versions
        if versions:
            self.version_combo.set(versions[0])
            self.status_label.config(text=self.lang["versions_found"].format(len(versions)), foreground="green")
        else:
            self.status_label.config(text=self.lang["no_versions"], foreground="red")

    def download_server(self):
        """下載伺服器核心"""
        try:
            # 驗證輸入
            if not self.validate_inputs():
                return

            # 準備下載
            self.prepare_download()

            # 獲取下載URL
            jar_url, jar_name = self.get_download_url()
            if not jar_url:
                raise Exception(self.lang["connection_error"].format(""))

            # 下載文件
            success = self.download_file(jar_url, jar_name)
            if not success:
                return

            # 生成必要文件
            self.generate_config_files(jar_name)

            # 完成提示
            self.show_success_message()

        except Exception as e:
            self.show_error(self.lang["download_failed"].format(str(e)))
            
        finally:
            self.reset_ui_state()

    def validate_inputs(self):
        """驗證用戶輸入"""
        if not self.selected_version.get():
            self.show_error(self.lang["select_version"])
            return False
            
        if not self.download_path.get():
            self.show_error(self.lang["select_path"])
            return False
            
        if not self.eula.get():
            self.show_error(self.lang["accept_eula"])
            return False
            
        return True

    def prepare_download(self):
        """準備下載環境"""
        self.downloading = True
        self.download_btn.config(state=tk.DISABLED)
        self.cancel_btn.config(state=tk.NORMAL)
        self.progress['value'] = 0
        self.status_label.config(text=self.lang["downloading"], foreground="blue")
        self.root.update()

    def get_download_url(self):
        """獲取下載URL"""
        server_type = self.selected_server_type.get()
        version = self.selected_version.get()
        
        try:
            if server_type == "Vanilla":
                return self.get_vanilla_url(version)
            elif server_type == "Paper":
                return self.get_paper_url(version)
            elif server_type == "Fabric":
                return self.get_fabric_url(version)
        except Exception as e:
            self.show_error(self.lang["connection_error"].format(str(e)))
            return None, None

    def get_vanilla_url(self, version):
        """獲取官方原版下載URL"""
        manifest_url = "https://launchermeta.mojang.com/mc/game/version_manifest.json"
        response = requests.get(manifest_url, timeout=15)
        response.raise_for_status()
        
        version_data = next((v for v in response.json()['versions'] if v['id'] == version), None)
        if not version_data:
            raise Exception(self.lang["no_versions"])
        
        version_info = requests.get(version_data['url'], timeout=15).json()
        jar_url = version_info['downloads']['server']['url']
        jar_name = f"server_{version}.jar"
        return jar_url, jar_name

    def get_paper_url(self, version):
        """獲取PaperMC下載URL"""
        builds_url = f"https://api.papermc.io/v2/projects/paper/versions/{version}"
        response = requests.get(builds_url, timeout=15)
        response.raise_for_status()
        
        builds = response.json()['builds']
        if not builds:
            raise Exception(self.lang["no_versions"])
        
        latest_build = max(builds)
        jar_url = f"https://api.papermc.io/v2/projects/paper/versions/{version}/builds/{latest_build}/downloads/paper-{version}-{latest_build}.jar"
        jar_name = f"paper-{version}.jar"
        return jar_url, jar_name

    def get_fabric_url(self, version):
        """獲取Fabric下載URL"""
        installer_url = "https://meta.fabricmc.net/v2/versions/installer"
        loader_url = "https://meta.fabricmc.net/v2/versions/loader"
        
        # 獲取最新安裝器
        installers = requests.get(installer_url, timeout=15).json()
        if not installers:
            raise Exception(self.lang["connection_error"].format(""))
        installer_version = installers[0]['version']
        
        # 獲取加載器版本
        loaders = requests.get(loader_url, timeout=15).json()
        if not loaders:
            raise Exception(self.lang["connection_error"].format(""))
        loader_version = loaders[0]['version']
        
        jar_url = f"https://meta.fabricmc.net/v2/versions/loader/{version}/{loader_version}/{installer_version}/server/jar"
        jar_name = f"fabric-server-{version}.jar"
        return jar_url, jar_name

    def download_file(self, jar_url, jar_name):
        """下載伺服器文件"""
        try:
            # 創建伺服器目錄
            server_dir = os.path.join(
                self.download_path.get(), 
                f"{self.server_name.get()}_{self.selected_server_type.get()}_{self.selected_version.get()}"
            )
            os.makedirs(server_dir, exist_ok=True)
            jar_path = os.path.join(server_dir, jar_name)

            # 開始下載
            self.status_label.config(text=self.lang["downloading"], foreground="blue")
            self.root.update()

            with requests.get(jar_url, stream=True, timeout=30) as response:
                response.raise_for_status()
                
                # 獲取文件大小（防止除零錯誤）
                total_size = int(response.headers.get('content-length', 0)) or 50 * 1024 * 1024  # 默認50MB
                downloaded = 0
                
                self.status_label.config(text=f"{self.lang['downloading']} {jar_name}...", foreground="blue")
                self.root.update()

                with open(jar_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if self.cancel_event.is_set():
                            if os.path.exists(jar_path):
                                os.remove(jar_path)
                            raise Exception(self.lang["canceled"])
                            
                        if chunk:  # 過濾保持活動的空塊
                            f.write(chunk)
                            downloaded += len(chunk)
                            progress = min(100, (downloaded / total_size) * 100)
                            self.progress['value'] = progress
                            self.status_label.config(
                                text=f"{self.lang['downloading']}: {downloaded//1024//1024}MB/{total_size//1024//1024}MB ({progress:.1f}%)",
                                foreground="blue"
                            )
                            self.root.update()

            # 驗證下載
            if not os.path.exists(jar_path):
                raise Exception(self.lang["file_not_saved"])
            if os.path.getsize(jar_path) == 0:
                os.remove(jar_path)
                raise Exception(self.lang["empty_file"])

            return True

        except requests.exceptions.RequestException as e:
            if os.path.exists(jar_path):
                os.remove(jar_path)
            raise Exception(self.lang["connection_error"].format(str(e)))
        except Exception as e:
            if 'jar_path' in locals() and os.path.exists(jar_path):
                os.remove(jar_path)
            raise

    def generate_config_files(self, jar_name):
        """生成配置文件和啟動腳本"""
        server_dir = os.path.join(
            self.download_path.get(), 
            f"{self.server_name.get()}_{self.selected_server_type.get()}_{self.selected_version.get()}"
        )
        
        # 生成啟動腳本
        bat_content = f"""@echo off
title Minecraft {self.selected_server_type.get()} Server {self.selected_version.get()}
java -Xms{self.memory.get()} -Xmx{self.memory.get()} -jar {jar_name} nogui
pause
"""
        bat_path = os.path.join(server_dir, "start.bat")
        with open(bat_path, 'w', encoding='gbk') as f:
            f.write(bat_content)

        # 生成eula.txt
        if self.eula.get():
            with open(os.path.join(server_dir, "eula.txt"), 'w') as f:
                f.write("eula=true\n")

    def show_success_message(self):
        """顯示成功消息"""
        server_dir = os.path.join(
            self.download_path.get(), 
            f"{self.server_name.get()}_{self.selected_server_type.get()}_{self.selected_version.get()}"
        )
        
        self.status_label.config(
            text=self.lang["download_complete"].format(server_dir), 
            foreground="green"
        )
        messagebox.showinfo(
            self.lang["title"],
            f"{self.lang['download_complete'].format(server_dir)}\n\n{self.lang['run_server']}"
        )

    def show_error(self, message):
        """顯示錯誤信息"""
        self.status_label.config(text=message, foreground="red")
        if "canceled" not in message.lower():
            messagebox.showerror(self.lang["error"], message)

    def reset_ui_state(self):
        """重置UI狀態"""
        self.downloading = False
        self.download_btn.config(state=tk.NORMAL)
        self.cancel_btn.config(state=tk.DISABLED)
        self.status_label.config(text=self.lang["ready"], foreground="gray")
        self.root.update()

if __name__ == "__main__":
    # 設置Windows高DPI適配
    if sys.platform == 'win32':
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)
    
    root = tk.Tk()
    try:
        # 嘗試加載Windows系統主題
        root.tk.call('source', 'azure/azure.tcl')
        root.tk.call('set_theme', 'light')
    except:
        pass  # 如果主題加載失敗則使用默認
    
    app = MinecraftServerDownloader(root)
    root.mainloop()
