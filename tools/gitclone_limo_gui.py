import os
import subprocess
import sys
import json
import shutil
from tkinter import Tk, filedialog, messagebox, Button, Label

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

def clone_repo(clone_dir):
    if os.path.exists(clone_dir):
        shutil.rmtree(clone_dir, onerror=handle_remove_readonly)
    subprocess.run(["git", "clone", REPO_URL, clone_dir], check=True)

def copy_files(src_dir, dest_dir):
    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)
    if os.path.exists(src_dir):
        for item in os.listdir(src_dir):
            s = os.path.join(src_dir, item)
            d = os.path.join(dest_dir, item)
            if os.path.isdir(s):
                shutil.copytree(s, d, dirs_exist_ok=True)
            else:
                shutil.copy2(s, d)
        print(f"{src_dir} から {dest_dir} にファイルをコピーしました！")
    else:
        print(f"{src_dir} ディレクトリが見つかりません")

def select_directory():
    directory = filedialog.askdirectory()
    return directory

def update_minecraft():
    minecraft_dir = get_minecraft_dir()
    if not minecraft_dir:
        minecraft_dir = select_directory()
        if not minecraft_dir:
            messagebox.showerror("エラー", "インストールディレクトリが選択されていません。")
            return
        save_minecraft_dir(minecraft_dir)

    clone_dir = os.path.join(os.getenv('TEMP'), "minecraft-mtr")
    resourcepacks_dir = os.path.join(minecraft_dir, "resourcepacks")
    mods_dir = os.path.join(minecraft_dir, "mods")

    try:
        clone_repo(clone_dir)
        copy_files(os.path.join(clone_dir, "resourcepacks"), resourcepacks_dir)
        copy_files(os.path.join(clone_dir, "mods"), mods_dir)
        messagebox.showinfo("完了", "アップデートが完了しました！")
    except subprocess.CalledProcessError as e:
        messagebox.showerror("エラー", f"エラーが発生しました: {e}")

def change_minecraft_dir():
    new_dir = select_directory()
    if new_dir:
        save_minecraft_dir(new_dir)
        messagebox.showinfo("完了", "マインクラフトのインストールディレクトリが変更されました。")

def create_gui():
    root = Tk()
    root.title("Minecraft MTR Updater")

    label = Label(root, text="Minecraft MTR Updater")
    label.pack(pady=10)

    update_button = Button(root, text="アップデートを開始する", command=update_minecraft)
    update_button.pack(pady=5)

    change_dir_button = Button(root, text="マインクラフトのインストールディレクトリを変更する", command=change_minecraft_dir)
    change_dir_button.pack(pady=5)

    root.mainloop()

if __name__ == "__main__":
    create_gui()

