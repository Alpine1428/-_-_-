import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import subprocess
import os
import winreg
import ctypes
import sys


def is_admin():
    """Проверка прав администратора"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


def run_as_admin():
    """Перезапуск с правами админа"""
    if not is_admin():
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, " ".join(sys.argv), None, 1
        )
        sys.exit()


class CheckSimulator:
    def __init__(self, root):
        self.root = root
        self.root.title("🛡️ Тренажёр для атестации проверяющих")
        self.root.geometry("780x900")
        self.root.resizable(False, False)
        self.root.configure(bg="#1e1e2e")

        # Список установленных дебаггеров для отката
        self.installed_debuggers = []

        # Стили
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Title.TLabel", font=("Segoe UI", 16, "bold"),
                         foreground="#cdd6f4", background="#1e1e2e")
        style.configure("Section.TLabelframe", foreground="#89b4fa",
                         background="#1e1e2e", font=("Segoe UI", 11, "bold"))
        style.configure("Section.TLabelframe.Label", foreground="#89b4fa",
                         background="#1e1e2e")
        style.configure("Action.TCheckbutton", foreground="#cdd6f4",
                         background="#1e1e2e", font=("Segoe UI", 10))
        style.configure("Status.TLabel", foreground="#a6e3a1",
                         background="#1e1e2e", font=("Segoe UI", 9))
        style.configure("Warning.TLabel", foreground="#f38ba8",
                         background="#1e1e2e", font=("Segoe UI", 9, "italic"))
        style.configure("Path.TLabel", foreground="#94e2d5",
                         background="#1e1e2e", font=("Consolas", 9))

        # Заголовок
        header_frame = tk.Frame(root, bg="#1e1e2e")
        header_frame.pack(fill="x", padx=20, pady=(15, 5))

        ttk.Label(header_frame, text="🛡️ Тренажёр для атестации",
                  style="Title.TLabel").pack()
        ttk.Label(header_frame,
                  text="Выберите действия для имитации и нажмите «Выполнить»",
                  style="Warning.TLabel").pack(pady=(2, 0))

        # Скроллируемая область
        canvas = tk.Canvas(root, bg="#1e1e2e", highlightthickness=0)
        scrollbar = ttk.Scrollbar(root, orient="vertical", command=canvas.yview)
        scroll_frame = tk.Frame(canvas, bg="#1e1e2e")

        scroll_frame.bind("<Configure>",
                          lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True, padx=(20, 0), pady=10)
        scrollbar.pack(side="right", fill="y", padx=(0, 10), pady=10)

        # Привязка колёсика мыши
        def on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        canvas.bind_all("<MouseWheel>", on_mousewheel)

        # =====================================================
        # СЕКЦИЯ 1: Чистка реестра (RegistryExplorer)
        # =====================================================
        self.registry_vars = {}
        reg_frame = ttk.LabelFrame(scroll_frame,
                                    text="📋 Чистка реестра (RegistryExplorer)",
                                    style="Section.TLabelframe", padding=10)
        reg_frame.pack(fill="x", padx=10, pady=8)

        registry_items = [
            ("userassist", "Удалить UserAssist",
             r"Software\Microsoft\Windows\CurrentVersion\Explorer\UserAssist"),
            ("featureusage", "Удалить FeatureUsage",
             r"Software\Microsoft\Windows\CurrentVersion\Explorer\FeatureUsage"),
            ("comdlg32", "Удалить ComDlg32",
             r"Software\Microsoft\Windows\CurrentVersion\Explorer\ComDlg32"),
            ("recentdocs", "Удалить RecentDocs",
             r"Software\Microsoft\Windows\CurrentVersion\Explorer\RecentDocs"),
            ("runmru", "Удалить RunMRU",
             r"Software\Microsoft\Windows\CurrentVersion\Explorer\RunMRU"),
            ("appcompat", "Удалить AppCompatFlags",
             r"Software\Microsoft\Windows NT\CurrentVersion\AppCompatFlags"),
            ("mrulistex", "Удалить MRUListEx значения",
             "MRUListEx"),
        ]

        for key, text, path in registry_items:
            var = tk.BooleanVar()
            self.registry_vars[key] = (var, path)
            cb = ttk.Checkbutton(reg_frame, text=f"  {text}\n     Путь: {path}",
                                  variable=var, style="Action.TCheckbutton")
            cb.pack(anchor="w", pady=3)

        # =====================================================
        # СЕКЦИЯ 2: Чистка ShellBag (UsrClass.dat)
        # =====================================================
        self.shellbag_vars = {}
        shell_frame = ttk.LabelFrame(scroll_frame,
                                      text="🐚 Чистка ShellBag (UsrClass.dat)",
                                      style="Section.TLabelframe", padding=10)
        shell_frame.pack(fill="x", padx=10, pady=8)

        shellbag_items = [
            ("bags", "Удалить Bags",
             r"Local Settings\Software\Microsoft\Windows\Shell\Bags"),
            ("bagmru", "Удалить BagMRU",
             r"Local Settings\Software\Microsoft\Windows\Shell\BagMRU"),
        ]

        for key, text, path in shellbag_items:
            var = tk.BooleanVar()
            self.shellbag_vars[key] = (var, path)
            cb = ttk.Checkbutton(shell_frame, text=f"  {text}\n     Путь: {path}",
                                  variable=var, style="Action.TCheckbutton")
            cb.pack(anchor="w", pady=3)

        # =====================================================
        # СЕКЦИЯ 3: Чистка Prefetch
        # =====================================================
        self.prefetch_var = tk.BooleanVar()
        pf_frame = ttk.LabelFrame(scroll_frame, text="📂 Чистка Prefetch",
                                    style="Section.TLabelframe", padding=10)
        pf_frame.pack(fill="x", padx=10, pady=8)

        ttk.Checkbutton(pf_frame,
                         text="  Очистить папку Prefetch\n     C:\\Windows\\Prefetch",
                         variable=self.prefetch_var,
                         style="Action.TCheckbutton").pack(anchor="w", pady=3)

        # =====================================================
        # СЕКЦИЯ 4: Чистка JumpList
        # =====================================================
        self.jumplist_vars = {}
        jl_frame = ttk.LabelFrame(scroll_frame, text="📑 Чистка JumpList",
                                    style="Section.TLabelframe", padding=10)
        jl_frame.pack(fill="x", padx=10, pady=8)

        jumplist_items = [
            ("auto_dest", "Очистить AutomaticDestinations",
             os.path.join(os.environ.get("APPDATA", ""),
                          r"Microsoft\Windows\Recent\AutomaticDestinations")),
            ("custom_dest", "Очистить CustomDestinations",
             os.path.join(os.environ.get("APPDATA", ""),
                          r"Microsoft\Windows\Recent\CustomDestinations")),
        ]

        for key, text, path in jumplist_items:
            var = tk.BooleanVar()
            self.jumplist_vars[key] = (var, path)
            cb = ttk.Checkbutton(jl_frame, text=f"  {text}\n     {path}",
                                  variable=var, style="Action.TCheckbutton")
            cb.pack(anchor="w", pady=3)

        # =====================================================
        # СЕКЦИЯ 5: Чистка Recent
        # =====================================================
        self.recent_var = tk.BooleanVar()
        recent_frame = ttk.LabelFrame(scroll_frame, text="🕐 Чистка Recent",
                                        style="Section.TLabelframe", padding=10)
        recent_frame.pack(fill="x", padx=10, pady=8)

        recent_path = os.path.join(os.environ.get("APPDATA", ""),
                                    r"Microsoft\Windows\Recent")
        ttk.Checkbutton(recent_frame,
                         text=f"  Очистить Recent (ярлыки)\n     {recent_path}",
                         variable=self.recent_var,
                         style="Action.TCheckbutton").pack(anchor="w", pady=3)

        # =====================================================
        # СЕКЦИЯ 6: Чистка BAM
        # =====================================================
        self.bam_var = tk.BooleanVar()
        bam_frame = ttk.LabelFrame(scroll_frame, text="📊 Чистка BAM данных",
                                     style="Section.TLabelframe", padding=10)
        bam_frame.pack(fill="x", padx=10, pady=8)

        ttk.Checkbutton(bam_frame,
                         text="  Очистить данные службы BAM\n"
                              "     SYSTEM\\CurrentControlSet\\Services\\bam\\State\\UserSettings",
                         variable=self.bam_var,
                         style="Action.TCheckbutton").pack(anchor="w", pady=3)

        # =====================================================
        # СЕКЦИЯ 7: Дебаггеры (SimpleUnlocker) — ОБНОВЛЁННАЯ
        # =====================================================
        self.debugger_entries = []
        dbg_frame = ttk.LabelFrame(scroll_frame,
                                     text="🐛 Установка дебаггеров (SimpleUnlocker)",
                                     style="Section.TLabelframe", padding=10)
        dbg_frame.pack(fill="x", padx=10, pady=8)

        ttk.Label(dbg_frame,
                  text="Дебаггер перенаправляет запуск .exe → на выбранный вами файл.\n"
                       "Если файл-подмена не выбран, по умолчанию откроется калькулятор.",
                  style="Warning.TLabel").pack(anchor="w", pady=(0, 8))

        # --- Дебаггер 1: JournalTrace.exe ---
        self.dbg1_var = tk.BooleanVar()
        self.dbg1_redirect_path = tk.StringVar(value="C:\\Windows\\System32\\calc.exe")

        dbg1_frame = tk.Frame(dbg_frame, bg="#1e1e2e")
        dbg1_frame.pack(fill="x", pady=5)

        ttk.Checkbutton(dbg1_frame,
                         text="  Дебаггер на JournalTrace.exe",
                         variable=self.dbg1_var,
                         style="Action.TCheckbutton").pack(anchor="w")

        dbg1_path_frame = tk.Frame(dbg1_frame, bg="#1e1e2e")
        dbg1_path_frame.pack(fill="x", padx=25, pady=2)

        tk.Label(dbg1_path_frame, text="Подмена на →", bg="#1e1e2e",
                 fg="#94e2d5", font=("Segoe UI", 9)).pack(side="left")
        dbg1_entry = tk.Entry(dbg1_path_frame, textvariable=self.dbg1_redirect_path,
                               width=45, bg="#313244", fg="#cdd6f4",
                               insertbackground="#cdd6f4", font=("Consolas", 9))
        dbg1_entry.pack(side="left", padx=5)
        tk.Button(dbg1_path_frame, text="📁 Обзор",
                  command=lambda: self.browse_file(self.dbg1_redirect_path),
                  bg="#89b4fa", fg="#1e1e2e", font=("Segoe UI", 8, "bold"),
                  relief="flat", padx=8, cursor="hand2").pack(side="left")

        # --- Дебаггер 2: Кастомный ---
        self.dbg2_var = tk.BooleanVar()
        self.dbg2_target_name = tk.StringVar(value="")
        self.dbg2_redirect_path = tk.StringVar(value="C:\\Windows\\System32\\calc.exe")

        sep = ttk.Separator(dbg_frame, orient="horizontal")
        sep.pack(fill="x", pady=8)

        dbg2_frame = tk.Frame(dbg_frame, bg="#1e1e2e")
        dbg2_frame.pack(fill="x", pady=5)

        ttk.Checkbutton(dbg2_frame,
                         text="  Дебаггер на кастомный .exe",
                         variable=self.dbg2_var,
                         style="Action.TCheckbutton").pack(anchor="w")

        # Целевой exe
        dbg2_target_frame = tk.Frame(dbg2_frame, bg="#1e1e2e")
        dbg2_target_frame.pack(fill="x", padx=25, pady=2)

        tk.Label(dbg2_target_frame, text="Целевой .exe  →", bg="#1e1e2e",
                 fg="#f9e2af", font=("Segoe UI", 9)).pack(side="left")
        dbg2_target_entry = tk.Entry(dbg2_target_frame,
                                      textvariable=self.dbg2_target_name,
                                      width=30, bg="#313244", fg="#cdd6f4",
                                      insertbackground="#cdd6f4",
                                      font=("Consolas", 9))
        dbg2_target_entry.pack(side="left", padx=5)
        tk.Button(dbg2_target_frame, text="📁 Обзор",
                  command=lambda: self.browse_exe_name(self.dbg2_target_name),
                  bg="#f9e2af", fg="#1e1e2e", font=("Segoe UI", 8, "bold"),
                  relief="flat", padx=8, cursor="hand2").pack(side="left")

        # Подмена
        dbg2_redir_frame = tk.Frame(dbg2_frame, bg="#1e1e2e")
        dbg2_redir_frame.pack(fill="x", padx=25, pady=2)

        tk.Label(dbg2_redir_frame, text="Подмена на   →", bg="#1e1e2e",
                 fg="#94e2d5", font=("Segoe UI", 9)).pack(side="left")
        dbg2_redir_entry = tk.Entry(dbg2_redir_frame,
                                     textvariable=self.dbg2_redirect_path,
                                     width=45, bg="#313244", fg="#cdd6f4",
                                     insertbackground="#cdd6f4",
                                     font=("Consolas", 9))
        dbg2_redir_entry.pack(side="left", padx=5)
        tk.Button(dbg2_redir_frame, text="📁 Обзор",
                  command=lambda: self.browse_file(self.dbg2_redirect_path),
                  bg="#89b4fa", fg="#1e1e2e", font=("Segoe UI", 8, "bold"),
                  relief="flat", padx=8, cursor="hand2").pack(side="left")

        # --- Дебаггер 3: Ещё один кастомный ---
        self.dbg3_var = tk.BooleanVar()
        self.dbg3_target_name = tk.StringVar(value="")
        self.dbg3_redirect_path = tk.StringVar(value="C:\\Windows\\System32\\calc.exe")

        sep2 = ttk.Separator(dbg_frame, orient="horizontal")
        sep2.pack(fill="x", pady=8)

        dbg3_frame = tk.Frame(dbg_frame, bg="#1e1e2e")
        dbg3_frame.pack(fill="x", pady=5)

        ttk.Checkbutton(dbg3_frame,
                         text="  Дебаггер на ещё один .exe",
                         variable=self.dbg3_var,
                         style="Action.TCheckbutton").pack(anchor="w")

        dbg3_target_frame = tk.Frame(dbg3_frame, bg="#1e1e2e")
        dbg3_target_frame.pack(fill="x", padx=25, pady=2)

        tk.Label(dbg3_target_frame, text="Целевой .exe  →", bg="#1e1e2e",
                 fg="#f9e2af", font=("Segoe UI", 9)).pack(side="left")
        tk.Entry(dbg3_target_frame, textvariable=self.dbg3_target_name,
                 width=30, bg="#313244", fg="#cdd6f4",
                 insertbackground="#cdd6f4",
                 font=("Consolas", 9)).pack(side="left", padx=5)
        tk.Button(dbg3_target_frame, text="📁 Обзор",
                  command=lambda: self.browse_exe_name(self.dbg3_target_name),
                  bg="#f9e2af", fg="#1e1e2e", font=("Segoe UI", 8, "bold"),
                  relief="flat", padx=8, cursor="hand2").pack(side="left")

        dbg3_redir_frame = tk.Frame(dbg3_frame, bg="#1e1e2e")
        dbg3_redir_frame.pack(fill="x", padx=25, pady=2)

        tk.Label(dbg3_redir_frame, text="Подмена на   →", bg="#1e1e2e",
                 fg="#94e2d5", font=("Segoe UI", 9)).pack(side="left")
        tk.Entry(dbg3_redir_frame, textvariable=self.dbg3_redirect_path,
                 width=45, bg="#313244", fg="#cdd6f4",
                 insertbackground="#cdd6f4",
                 font=("Consolas", 9)).pack(side="left", padx=5)
        tk.Button(dbg3_redir_frame, text="📁 Обзор",
                  command=lambda: self.browse_file(self.dbg3_redirect_path),
                  bg="#89b4fa", fg="#1e1e2e", font=("Segoe UI", 8, "bold"),
                  relief="flat", padx=8, cursor="hand2").pack(side="left")

        # =====================================================
        # СЕКЦИЯ 8: Быстрые пресеты
        # =====================================================
        preset_frame = ttk.LabelFrame(scroll_frame, text="⚡ Быстрые пресеты",
                                        style="Section.TLabelframe", padding=10)
        preset_frame.pack(fill="x", padx=10, pady=8)

        presets_row = tk.Frame(preset_frame, bg="#1e1e2e")
        presets_row.pack(fill="x", pady=3)

        tk.Button(presets_row, text="Выбрать ВСЁ", command=self.select_all,
                  bg="#89b4fa", fg="#1e1e2e", font=("Segoe UI", 9, "bold"),
                  relief="flat", padx=10, pady=3, cursor="hand2").pack(side="left", padx=3)
        tk.Button(presets_row, text="Снять ВСЁ", command=self.deselect_all,
                  bg="#6c7086", fg="#cdd6f4", font=("Segoe UI", 9, "bold"),
                  relief="flat", padx=10, pady=3, cursor="hand2").pack(side="left", padx=3)
        tk.Button(presets_row, text="Только реестр", command=self.preset_registry,
                  bg="#f9e2af", fg="#1e1e2e", font=("Segoe UI", 9, "bold"),
                  relief="flat", padx=10, pady=3, cursor="hand2").pack(side="left", padx=3)
        tk.Button(presets_row, text="Только дебаггеры",
                  command=self.preset_debuggers,
                  bg="#f38ba8", fg="#1e1e2e", font=("Segoe UI", 9, "bold"),
                  relief="flat", padx=10, pady=3, cursor="hand2").pack(side="left", padx=3)
        tk.Button(presets_row, text="Полная чистка",
                  command=self.preset_full_clean,
                  bg="#fab387", fg="#1e1e2e", font=("Segoe UI", 9, "bold"),
                  relief="flat", padx=10, pady=3, cursor="hand2").pack(side="left", padx=3)

        # =====================================================
        # Кнопки действий
        # =====================================================
        btn_frame = tk.Frame(scroll_frame, bg="#1e1e2e")
        btn_frame.pack(fill="x", padx=10, pady=15)

        tk.Button(btn_frame, text="✅ ВЫПОЛНИТЬ ВЫБРАННОЕ",
                  command=self.execute_selected,
                  bg="#a6e3a1", fg="#1e1e2e", font=("Segoe UI", 13, "bold"),
                  relief="flat", padx=20, pady=10, cursor="hand2"
                  ).pack(fill="x", pady=3)

        tk.Button(btn_frame, text="🔄 ОТКАТИТЬ ВСЕ ДЕБАГГЕРЫ",
                  command=self.undo_debuggers,
                  bg="#f9e2af", fg="#1e1e2e", font=("Segoe UI", 11, "bold"),
                  relief="flat", padx=20, pady=8, cursor="hand2"
                  ).pack(fill="x", pady=3)

        # Лог
        log_frame = ttk.LabelFrame(scroll_frame, text="📝 Лог действий",
                                     style="Section.TLabelframe", padding=10)
        log_frame.pack(fill="x", padx=10, pady=(0, 15))

        log_btn_frame = tk.Frame(log_frame, bg="#1e1e2e")
        log_btn_frame.pack(fill="x", pady=(0, 5))
        tk.Button(log_btn_frame, text="🗑️ Очистить лог",
                  command=lambda: self.log_text.delete("1.0", "end"),
                  bg="#45475a", fg="#cdd6f4", font=("Segoe UI", 8),
                  relief="flat", padx=8, cursor="hand2").pack(side="right")

        self.log_text = tk.Text(log_frame, height=12, bg="#181825", fg="#a6e3a1",
                                 font=("Consolas", 9), relief="flat",
                                 insertbackground="#a6e3a1")
        self.log_text.pack(fill="x")

    # =====================================================
    # Диалоги выбора файлов
    # =====================================================
    def browse_file(self, string_var):
        """Выбор файла-подмены (на что перенаправить)"""
        filepath = filedialog.askopenfilename(
            title="Выберите файл-подмену (что откроется вместо оригинала)",
            filetypes=[
                ("Исполняемые файлы", "*.exe"),
                ("Все файлы", "*.*")
            ],
            initialdir="C:\\Windows\\System32"
        )
        if filepath:
            string_var.set(filepath)

    def browse_exe_name(self, string_var):
        """Выбор целевого .exe (на какой файл ставить дебаггер)"""
        filepath = filedialog.askopenfilename(
            title="Выберите целевой .exe (на какой файл поставить дебаггер)",
            filetypes=[
                ("Исполняемые файлы", "*.exe"),
                ("Все файлы", "*.*")
            ]
        )
        if filepath:
            # Берём только имя файла, т.к. IFEO работает по имени
            exe_name = os.path.basename(filepath)
            string_var.set(exe_name)

    # =====================================================
    # Логирование
    # =====================================================
    def log(self, message):
        self.log_text.insert("end", f"{message}\n")
        self.log_text.see("end")
        self.root.update_idletasks()

    # =====================================================
    # Пресеты
    # =====================================================
    def select_all(self):
        for var, _ in self.registry_vars.values():
            var.set(True)
        for var, _ in self.shellbag_vars.values():
            var.set(True)
        self.prefetch_var.set(True)
        for var, _ in self.jumplist_vars.values():
            var.set(True)
        self.recent_var.set(True)
        self.bam_var.set(True)
        self.dbg1_var.set(True)
        self.dbg2_var.set(True)
        self.dbg3_var.set(True)

    def deselect_all(self):
        for var, _ in self.registry_vars.values():
            var.set(False)
        for var, _ in self.shellbag_vars.values():
            var.set(False)
        self.prefetch_var.set(False)
        for var, _ in self.jumplist_vars.values():
            var.set(False)
        self.recent_var.set(False)
        self.bam_var.set(False)
        self.dbg1_var.set(False)
        self.dbg2_var.set(False)
        self.dbg3_var.set(False)

    def preset_registry(self):
        self.deselect_all()
        for var, _ in self.registry_vars.values():
            var.set(True)
        for var, _ in self.shellbag_vars.values():
            var.set(True)

    def preset_debuggers(self):
        self.deselect_all()
        self.dbg1_var.set(True)
        self.dbg2_var.set(True)
        self.dbg3_var.set(True)

    def preset_full_clean(self):
        self.select_all()
        self.dbg1_var.set(False)
        self.dbg2_var.set(False)
        self.dbg3_var.set(False)

    # =====================================================
    # Главное выполнение
    # =====================================================
    def execute_selected(self):
        if not is_admin():
            messagebox.showerror("Ошибка",
                                  "Запустите программу от имени администратора!")
            return

        confirm = messagebox.askyesno(
            "Подтверждение",
            "⚠️ Вы уверены?\n\n"
            "Выбранные действия изменят систему.\n"
            "Используйте только для тестирования атестуемых!\n\n"
            "Продолжить?"
        )
        if not confirm:
            return

        self.log("=" * 55)
        self.log("🚀 Начинаю выполнение...")
        self.log("=" * 55)

        count = 0

        # --- Реестр ---
        for key, (var, path) in self.registry_vars.items():
            if var.get():
                count += 1
                self.clean_registry(key, path)

        # --- ShellBag ---
        for key, (var, path) in self.shellbag_vars.items():
            if var.get():
                count += 1
                self.clean_shellbag(key, path)

        # --- Prefetch ---
        if self.prefetch_var.get():
            count += 1
            self.clean_prefetch()

        # --- JumpList ---
        for key, (var, path) in self.jumplist_vars.items():
            if var.get():
                count += 1
                self.clean_jumplist(key, path)

        # --- Recent ---
        if self.recent_var.get():
            count += 1
            self.clean_recent()

        # --- BAM ---
        if self.bam_var.get():
            count += 1
            self.clean_bam()

        # --- Дебаггер 1: JournalTrace.exe ---
        if self.dbg1_var.get():
            count += 1
            redirect = self.dbg1_redirect_path.get().strip()
            if not redirect:
                redirect = "C:\\Windows\\System32\\calc.exe"
            self.set_debugger("JournalTrace.exe", redirect)

        # --- Дебаггер 2: Кастомный ---
        if self.dbg2_var.get():
            target = self.dbg2_target_name.get().strip()
            redirect = self.dbg2_redirect_path.get().strip()
            if not target:
                self.log("⚠️ Дебаггер 2: не указан целевой .exe, пропускаю")
            else:
                if not redirect:
                    redirect = "C:\\Windows\\System32\\calc.exe"
                count += 1
                self.set_debugger(target, redirect)

        # --- Дебаггер 3: Ещё один кастомный ---
        if self.dbg3_var.get():
            target = self.dbg3_target_name.get().strip()
            redirect = self.dbg3_redirect_path.get().strip()
            if not target:
                self.log("⚠️ Дебаггер 3: не указан целевой .exe, пропускаю")
            else:
                if not redirect:
                    redirect = "C:\\Windows\\System32\\calc.exe"
                count += 1
                self.set_debugger(target, redirect)

        self.log(f"\n✅ Выполнено действий: {count}")
        self.log("=" * 55)

        if count > 0:
            messagebox.showinfo("Готово", f"Выполнено {count} действий.\nСм. лог.")
        else:
            messagebox.showwarning("Ничего не выбрано",
                                    "Отметьте хотя бы одно действие!")

    # =====================================================
    # Реализация чисток
    # =====================================================
    def clean_registry(self, key, path):
        if key == "mrulistex":
            mru_paths = [
                r"Software\Microsoft\Windows\CurrentVersion\Explorer\RunMRU",
                r"Software\Microsoft\Windows\CurrentVersion\Explorer\ComDlg32\OpenSavePidlMRU",
                r"Software\Microsoft\Windows\CurrentVersion\Explorer\ComDlg32\LastVisitedPidlMRU",
            ]
            for mru_path in mru_paths:
                try:
                    reg_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                                             mru_path, 0,
                                             winreg.KEY_ALL_ACCESS)
                    try:
                        winreg.DeleteValue(reg_key, "MRUListEx")
                        self.log(f"  ✅ Удалён MRUListEx из {mru_path}")
                    except FileNotFoundError:
                        self.log(f"  ℹ️ MRUListEx не найден в {mru_path}")
                    winreg.CloseKey(reg_key)
                except Exception as e:
                    self.log(f"  ⚠️ Ошибка MRUListEx {mru_path}: {e}")
        else:
            try:
                self.delete_registry_tree(winreg.HKEY_CURRENT_USER, path)
                self.log(f"  ✅ Удалён раздел: HKCU\\{path}")
            except FileNotFoundError:
                self.log(f"  ℹ️ Раздел не найден: HKCU\\{path}")
            except Exception as e:
                self.log(f"  ⚠️ Ошибка удаления {path}: {e}")

    def delete_registry_tree(self, hive, path):
        try:
            key = winreg.OpenKey(hive, path, 0,
                                 winreg.KEY_ALL_ACCESS | winreg.KEY_WOW64_64KEY)
        except FileNotFoundError:
            raise
        try:
            while True:
                try:
                    subkey_name = winreg.EnumKey(key, 0)
                    self.delete_registry_tree(hive, f"{path}\\{subkey_name}")
                except OSError:
                    break
            winreg.CloseKey(key)
            winreg.DeleteKey(hive, path)
        except Exception as e:
            winreg.CloseKey(key)
            raise e

    def clean_shellbag(self, key, path):
        actual_path = f"Software\\Classes\\{path}"
        try:
            self.delete_registry_tree(winreg.HKEY_CURRENT_USER, actual_path)
            self.log(f"  ✅ Удалён ShellBag: {actual_path}")
        except FileNotFoundError:
            self.log(f"  ℹ️ ShellBag не найден: {actual_path}")
        except Exception as e:
            self.log(f"  ⚠️ Ошибка ShellBag: {e}")

    def clean_prefetch(self):
        prefetch_path = r"C:\Windows\Prefetch"
        try:
            count = 0
            for f in os.listdir(prefetch_path):
                if f.endswith(".pf"):
                    try:
                        os.remove(os.path.join(prefetch_path, f))
                        count += 1
                    except PermissionError:
                        pass
            self.log(f"  ✅ Очищен Prefetch: удалено {count} .pf файлов")
        except Exception as e:
            self.log(f"  ⚠️ Ошибка Prefetch: {e}")

    def clean_jumplist(self, key, path):
        try:
            if os.path.exists(path):
                count = 0
                for f in os.listdir(path):
                    try:
                        os.remove(os.path.join(path, f))
                        count += 1
                    except:
                        pass
                self.log(f"  ✅ Очищен JumpList ({key}): удалено {count} файлов")
            else:
                self.log(f"  ℹ️ Папка не найдена: {path}")
        except Exception as e:
            self.log(f"  ⚠️ Ошибка JumpList: {e}")

    def clean_recent(self):
        recent_path = os.path.join(os.environ.get("APPDATA", ""),
                                    r"Microsoft\Windows\Recent")
        try:
            count = 0
            for f in os.listdir(recent_path):
                fp = os.path.join(recent_path, f)
                if os.path.isfile(fp) and f.endswith(".lnk"):
                    try:
                        os.remove(fp)
                        count += 1
                    except:
                        pass
            self.log(f"  ✅ Очищен Recent: удалено {count} ярлыков")
        except Exception as e:
            self.log(f"  ⚠️ Ошибка Recent: {e}")

    def clean_bam(self):
        try:
            bam_base = r"SYSTEM\CurrentControlSet\Services\bam\State\UserSettings"
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, bam_base, 0,
                                 winreg.KEY_ALL_ACCESS | winreg.KEY_WOW64_64KEY)
            i = 0
            subkeys = []
            while True:
                try:
                    subkeys.append(winreg.EnumKey(key, i))
                    i += 1
                except OSError:
                    break
            winreg.CloseKey(key)

            for sid in subkeys:
                sid_path = f"{bam_base}\\{sid}"
                try:
                    sid_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                                             sid_path, 0,
                                             winreg.KEY_ALL_ACCESS | winreg.KEY_WOW64_64KEY)
                    values = []
                    j = 0
                    while True:
                        try:
                            values.append(winreg.EnumValue(sid_key, j))
                            j += 1
                        except OSError:
                            break

                    deleted = 0
                    for val_name, val_data, val_type in values:
                        if val_name.lower() not in ("version", "sequencenumber"):
                            try:
                                winreg.DeleteValue(sid_key, val_name)
                                deleted += 1
                            except:
                                pass
                    winreg.CloseKey(sid_key)
                    if deleted > 0:
                        self.log(f"  ✅ BAM: удалено {deleted} записей из {sid[:25]}...")
                except Exception as e:
                    self.log(f"  ⚠️ BAM ошибка для {sid[:25]}: {e}")
        except Exception as e:
            self.log(f"  ⚠️ Ошибка BAM: {e}")

    # =====================================================
    # Дебаггеры
    # =====================================================
    def set_debugger(self, exe_name, redirect_path):
        """Установка дебаггера через IFEO"""
        ifeo_path = (f"SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\"
                     f"Image File Execution Options\\{exe_name}")
        try:
            key = winreg.CreateKeyEx(winreg.HKEY_LOCAL_MACHINE, ifeo_path,
                                      0, winreg.KEY_ALL_ACCESS)
            winreg.SetValueEx(key, "Debugger", 0, winreg.REG_SZ, redirect_path)
            winreg.CloseKey(key)

            # Запоминаем для отката
            if exe_name not in self.installed_debuggers:
                self.installed_debuggers.append(exe_name)

            self.log(f"  🐛 Дебаггер: {exe_name} → {redirect_path}")
        except Exception as e:
            self.log(f"  ⚠️ Ошибка дебаггера {exe_name}: {e}")

    def undo_debuggers(self):
        """Откат всех дебаггеров"""
        if not is_admin():
            messagebox.showerror("Ошибка",
                                  "Запустите программу от имени администратора!")
            return

        # Собираем все возможные цели
        targets = set(self.installed_debuggers)
        targets.add("JournalTrace.exe")
        t2 = self.dbg2_target_name.get().strip()
        t3 = self.dbg3_target_name.get().strip()
        if t2:
            targets.add(t2)
        if t3:
            targets.add(t3)

        self.log("\n🔄 Откат всех дебаггеров...")
        removed = 0
        for exe_name in targets:
            ifeo_path = (f"SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\"
                         f"Image File Execution Options\\{exe_name}")
            try:
                # Сначала удаляем значение Debugger
                try:
                    key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                                         ifeo_path, 0, winreg.KEY_ALL_ACCESS)
                    winreg.DeleteValue(key, "Debugger")
                    winreg.CloseKey(key)
                except:
                    pass
                # Потом пытаемся удалить ключ
                winreg.DeleteKey(winreg.HKEY_LOCAL_MACHINE, ifeo_path)
                self.log(f"  ✅ Дебаггер снят: {exe_name}")
                removed += 1
            except FileNotFoundError:
                self.log(f"  ℹ️ Не был установлен: {exe_name}")
            except Exception as e:
                self.log(f"  ⚠️ Ошибка отката {exe_name}: {e}")

        self.installed_debuggers.clear()
        self.log(f"  Снято дебаггеров: {removed}")
        messagebox.showinfo("Готово", f"Дебаггеры откачены ({removed} шт.)")


def main():
    if not is_admin():
        root = tk.Tk()
        root.withdraw()
        result = messagebox.askyesno(
            "Требуются права администратора",
            "Для работы программы нужны права администратора.\n"
            "Перезапустить с правами админа?"
        )
        root.destroy()
        if result:
            run_as_admin()
        else:
            sys.exit()

    root = tk.Tk()
    app = CheckSimulator(root)
    root.mainloop()


if __name__ == "__main__":
    main()