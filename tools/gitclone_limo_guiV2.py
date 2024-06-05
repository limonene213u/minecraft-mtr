import os
import subprocess
import sys
import json
import shutil
from tkinter import Tk, filedialog, messagebox, Button, Label, StringVar, Text, Scrollbar, VERTICAL, RIGHT, Y, END
from tkinter.ttk import Progressbar
import threading

# GitHubリポジトリのURL
REPO_URL = "https://github.com/limonene213u/minecraft-mtr.git"
# ディレクトリを保存するファイルのパス
CONFIG_FILE = os.path.expanduser("~/.minecraft_resourcepack_config.json")

def get_minecraft_dir():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)
            return config.get('minecraft_dir', None)
    return None

def save_minecraft_dir(minecraft_dir):
    config = {'minecraft_dir': minecraft_dir}
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f)

def handle_remove_readonly(func, path, exc_info):
    import stat
    os.chmod(path, stat.S_IWRITE)
    func(path)

def clear_directory(directory):
    if os.path.exists(directory):
        for item in os.listdir(directory):
            item_path = os.path.join(directory, item)
            if os.path.isdir(item_path):
                shutil.rmtree(item_path, onerror=handle_remove_readonly)
            else:
                os.remove(item_path)

def clone_repo(clone_dir, status_text, progress):
    status_text.insert(END, "リポジトリをクローンしています...\n")
    status_text.see(END)
    progress['value'] = 10
    if os.path.exists(clone_dir):
        shutil.rmtree(clone_dir, onerror=handle_remove_readonly)
    process = subprocess.Popen(["git", "clone", REPO_URL, clone_dir], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    for line in process.stdout:
        status_text.insert(END, line)
        status_text.see(END)
    process.wait()
    progress['value'] = 50

def copy_files(src_dir, dest_dir, status_text, progress):
    status_text.insert(END, f"{src_dir} から {dest_dir} にファイルをコピーしています...\n")
    status_text.see(END)
    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)
    else:
        clear_directory(dest_dir)  # 既存のファイルを削除する
    if os.path.exists(src_dir):
        for item in os.listdir(src_dir):
            s = os.path.join(src_dir, item)
            d = os.path.join(dest_dir, item)
            if os.path.isdir(s):
                shutil.copytree(s, d, dirs_exist_ok=True)
            else:
                shutil.copy2(s, d)
            status_text.insert(END, f"コピーしました: {s} -> {d}\n")
            status_text.see(END)
    else:
        status_text.insert(END, f"{src_dir} ディレクトリが見つかりません\n")
        status_text.see(END)
    progress['value'] += 25

def select_directory():
    directory = filedialog.askdirectory()
    return directory

def update_minecraft(status_text, progress):
    minecraft_dir = get_minecraft_dir()
    if not minecraft_dir:
        minecraft_dir = select_directory()
        if not minecraft_dir:
            messagebox.showerror("エラー", "インストールディレクトリが選択されていません。")
            return
        save_minecraft_dir(minecraft_dir)

    temp_dir = os.getenv('TEMP') or '/tmp'
    clone_dir = os.path.join(temp_dir, "minecraft-mtr")
    resourcepacks_dir = os.path.join(minecraft_dir, "resourcepacks")
    mods_dir = os.path.join(minecraft_dir, "mods")

    try:
        clone_repo(clone_dir, status_text, progress)
        copy_files(os.path.join(clone_dir, "resourcepacks"), resourcepacks_dir, status_text, progress)
        copy_files(os.path.join(clone_dir, "mods"), mods_dir, status_text, progress)
        messagebox.showinfo("完了", "アップデートが完了しました！")
    except subprocess.CalledProcessError as e:
        messagebox.showerror("エラー", f"エラーが発生しました: {e}")

def update_minecraft_thread(status_text, progress):
    thread = threading.Thread(target=update_minecraft, args=(status_text, progress))
    thread.start()

def change_minecraft_dir(status_text):
    new_dir = select_directory()
    if new_dir:
        save_minecraft_dir(new_dir)
        messagebox.showinfo("完了", "マインクラフトのインストールディレクトリが変更されました。")

def create_gui():
    root = Tk()
    root.title("Minecraft MTR Updater")

    label = Label(root, text="Minecraft MTR Updater")
    label.pack(pady=10)

    status_text = Text(root, wrap='word', height=15, width=60)
    status_text.pack(pady=5)
    scrollbar = Scrollbar(root, orient=VERTICAL, command=status_text.yview)
    status_text.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side=RIGHT, fill=Y)

    progress = Progressbar(root, orient='horizontal', length=300, mode='determinate')
    progress.pack(pady=5)

    update_button = Button(root, text="アップデートを開始する", command=lambda: update_minecraft_thread(status_text, progress))
    update_button.pack(pady=5)

    change_dir_button = Button(root, text="マインクラフトのインストールディレクトリを変更する", command=lambda: change_minecraft_dir(status_text))
    change_dir_button.pack(pady=5)

    root.mainloop()

if __name__ == "__main__":
    create_gui()
