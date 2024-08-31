import os
import subprocess
import sys
import json
import shutil
import requests  # Apacheサーバーからファイルをダウンロードするために使用
from tkinter import Tk, filedialog, messagebox, Button, Label, StringVar, Text, Scrollbar, VERTICAL, RIGHT, Y, END
from tkinter.ttk import Progressbar
import threading

# ApacheサーバーのURL
MODS_URL = "https://mtr-sign.limonene-aktk.link/mods/"
RESOURCEPACK_URL = "https://mtr-sign.limonene-aktk.link/resourcepack/"
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

def download_files(url, dest_dir, status_text, progress):
    status_text.insert(END, f"{url} から {dest_dir} にファイルをダウンロードしています...\n")
    status_text.see(END)
    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)
    else:
        clear_directory(dest_dir)  # 既存のファイルを削除する

    # サーバーからファイルリストを取得
    try:
        response = requests.get(url)
        response.raise_for_status()
        file_list = response.json()  # ここでは、ファイルリストがJSONで提供されていると仮定しています
    except requests.RequestException as e:
        status_text.insert(END, f"エラー: ファイルリストの取得に失敗しました: {e}\n")
        status_text.see(END)
        return

    # 各ファイルをダウンロード
    for file_info in file_list:
        file_name = file_info["name"]
        file_url = f"{url}{file_name}"
        dest_file_path = os.path.join(dest_dir, file_name)

        try:
            file_response = requests.get(file_url, stream=True)
            file_response.raise_for_status()

            with open(dest_file_path, 'wb') as f:
                for chunk in file_response.iter_content(chunk_size=8192):
                    f.write(chunk)

            status_text.insert(END, f"ダウンロード完了: {file_name}\n")
            status_text.see(END)
        except requests.RequestException as e:
            status_text.insert(END, f"エラー: {file_name} のダウンロードに失敗しました: {e}\n")
            status_text.see(END)
    progress['value'] += 50

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

    mods_dir = os.path.join(minecraft_dir, "mods")
    resourcepacks_dir = os.path.join(minecraft_dir, "resourcepacks")

    try:
        download_files(MODS_URL, mods_dir, status_text, progress)
        download_files(RESOURCEPACK_URL, resourcepacks_dir, status_text, progress)
        messagebox.showinfo("完了", "アップデートが完了しました！")
    except Exception as e:
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
