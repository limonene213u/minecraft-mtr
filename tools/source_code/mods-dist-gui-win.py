import os
import json
import shutil
import requests
from dotenv import load_dotenv
from tkinter import Tk, filedialog, messagebox, ttk, StringVar, Label, Button, Frame

load_dotenv()

BASE_URL = os.getenv("RESOURCE_BASE_URL", "http://localhost:8080")
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


def download_file(file_url, dest_path, progress_callback=None):
    """指定されたURLからファイルをダウンロード"""
    with requests.get(file_url, stream=True) as r:
        r.raise_for_status()
        total_size = int(r.headers.get('Content-Length', 0))
        downloaded = 0
        with open(dest_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
                downloaded += len(chunk)
                if progress_callback:
                    progress_callback(downloaded, total_size)
    print(f"ダウンロード完了: {dest_path}")

def download_and_clear(base_url, sub_dir, dest_dir, progress_callback=None):
    """リソースをダウンロード"""
    if os.path.exists(dest_dir):
        shutil.rmtree(dest_dir)
    os.makedirs(dest_dir, exist_ok=True)

    response = requests.get(f"{base_url}/list.php?path={sub_dir}")
    if response.status_code != 200:
        raise Exception(f"エラー: {response.status_code}")

    items = response.json()
    total_items = len(items)

    for i, item in enumerate(items):
        item_name = item["name"]
        item_type = item["type"]
        item_url = f"{base_url}/{sub_dir}/{item_name}"
        item_path = os.path.join(dest_dir, item_name)

        if item_type == "folder":
            download_and_clear(base_url, f"{sub_dir}/{item_name}", item_path, progress_callback)
        else:
            download_file(item_url, item_path)

        # 進捗更新
        if progress_callback:
            progress_callback(i + 1, total_items)


def start_download(progress_bar, label_var):
    """ダウンロードを開始"""
    minecraft_dir = get_minecraft_dir()
    if not minecraft_dir:
        messagebox.showerror("エラー", "インストールフォルダが設定されていません")
        return

    resourcepacks_dir = os.path.join(minecraft_dir, "resourcepacks")
    mods_dir = os.path.join(minecraft_dir, "mods")

    try:
        progress_bar['value'] = 0  # プログレスバーをリセット
        label_var.set("リソースパックをダウンロード中...")

        def update_progress(current, total):
            progress = (current / total) * 100
            progress_bar['value'] = progress
            root.update_idletasks()  # GUIの更新を強制

        download_and_clear(BASE_URL, "resourcepacks", resourcepacks_dir, update_progress)

        label_var.set("Modをダウンロード中...")
        download_and_clear(BASE_URL, "mods", mods_dir, update_progress)

        label_var.set("ダウンロード完了！")
        messagebox.showinfo("完了", "ダウンロードが完了しました！")
    except Exception as e:
        messagebox.showerror("エラー", f"ダウンロード中にエラーが発生しました: {e}")

def set_minecraft_dir(label_var):
    """インストールフォルダを設定"""
    folder = filedialog.askdirectory()
    if folder:
        save_minecraft_dir(folder)
        label_var.set(f"インストールフォルダ: {folder}")

def main():
    global root  # グローバル変数として定義
    minecraft_dir = get_minecraft_dir()

    # Tkinter GUI
    root = Tk()
    root.title("Minecraft Mod Downloader")

    frame = Frame(root)
    frame.pack(padx=10, pady=10)

    label_var = StringVar(value=f"インストールフォルダ: {minecraft_dir or '未設定'}")
    Label(frame, textvariable=label_var, wraplength=300).pack(pady=5)

    Button(frame, text="フォルダを設定", command=lambda: set_minecraft_dir(label_var)).pack(pady=5)

    progress_bar = ttk.Progressbar(frame, length=300, mode="determinate")
    progress_bar.pack(pady=10)

    Button(frame, text="ダウンロード開始", command=lambda: start_download(progress_bar, label_var)).pack(pady=5)

    root.mainloop()

if __name__ == "__main__":
    main()