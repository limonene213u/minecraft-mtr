import os
import sys
import json
import shutil
import requests
from dotenv import load_dotenv

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


def download_file(file_url, dest_path):
    """指定されたURLからファイルをダウンロード"""
    with requests.get(file_url, stream=True) as r:
        r.raise_for_status()
        with open(dest_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
    print(f"ダウンロード完了: {dest_path}")


def download_folder(base_url, folder_name, dest_path):
    """フォルダ全体を再帰的にダウンロード"""
    folder_url = f"{base_url}/{folder_name}/list.php?path={folder_name}"
    response = requests.get(folder_url)
    if response.status_code != 200:
        print(f"フォルダ {folder_name} のリストを取得できませんでした ({response.status_code})")
        print(f"レスポンス内容: {response.text}")
        return

    try:
        items = response.json()
    except json.JSONDecodeError as e:
        print(f"JSONデコードエラー: {e}")
        print(f"レスポンス内容: {response.text}")
        return

    os.makedirs(dest_path, exist_ok=True)

    for item in items:
        item_url = f"{base_url}/{folder_name}/{item}"
        item_path = os.path.join(dest_path, item)
        if item.endswith('/'):  # フォルダの場合
            download_folder(base_url, f"{folder_name}/{item}", item_path)
        else:  # ファイルの場合
            download_file(item_url, item_path)

def download_and_clear(base_url, sub_dir, dest_dir):
    # フォルダをクリア
    if os.path.exists(dest_dir):
        shutil.rmtree(dest_dir)
    os.makedirs(dest_dir, exist_ok=True)

    # ファイルリストを取得
    response = requests.get(f"{base_url}/list.php?path={sub_dir}")
    if response.status_code != 200:
        print(f"エラー: {sub_dir} のリストを取得できませんでした ({response.status_code})")
        print(f"レスポンス内容: {response.text}")
        sys.exit(1)

    try:
        items = response.json()
    except json.JSONDecodeError as e:
        print(f"JSONデコードエラー: {e}")
        print(f"レスポンス内容: {response.text}")
        sys.exit(1)

    for item in items:
        item_name = item["name"]
        item_type = item["type"]
        item_url = f"{base_url}/{sub_dir}/{item_name}"
        item_path = os.path.join(dest_dir, item_name)

        if item_type == "folder":  # フォルダの場合
            download_and_clear(base_url, f"{sub_dir}/{item_name}", item_path)
        else:  # ファイルの場合
            with requests.get(item_url, stream=True) as r:
                r.raise_for_status()
                with open(item_path, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
            print(f"ダウンロード完了: {item_path}")

def main():
    minecraft_dir = get_minecraft_dir()
    if not minecraft_dir:
        minecraft_dir = input("マインクラフトのインストールディレクトリをフルパスで入力してください: ")
        save_minecraft_dir(minecraft_dir)

    resourcepacks_dir = os.path.join(minecraft_dir, "resourcepacks")
    mods_dir = os.path.join(minecraft_dir, "mods")

    try:
        download_and_clear(BASE_URL, "resourcepacks", resourcepacks_dir)
        download_and_clear(BASE_URL, "mods", mods_dir)
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
