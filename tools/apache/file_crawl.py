#file_crawl.py

import os
import json

# ファイルリストを取得する関数
def get_file_list(directory):
    try:
        # 指定されたディレクトリの中身を取得
        files = os.listdir(directory)
        # ファイルとディレクトリを分ける
        file_list = [f for f in files if os.path.isfile(os.path.join(directory, f))]
        dir_list = [d for d in files if os.path.isdir(os.path.join(directory, d))]
        
        return {"files": file_list, "directories": dir_list}
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        return None

# JSONファイルを作成または更新する関数
def create_or_update_json_file(json_path, data):
    try:
        # JSONファイルが存在する場合は削除
        if os.path.exists(json_path):
            os.remove(json_path)
        
        # JSONファイルを作成してデータを書き込む
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"{json_path} を作成または更新しました。")
    except Exception as e:
        print(f"JSONファイルの作成または更新に失敗しました: {e}")

# メインロジック
def main():
    # 対象ディレクトリのパス
    mod_directory = "/mods"
    resourcepack_directory = "/resourcepack"
    
    # ファイルリストを取得
    mod_files = get_file_list(mod_directory)
    resourcepack_files = get_file_list(resourcepack_directory)
    
    # JSONファイルのパス
    mod_json_path = "mod_files.json"
    resourcepack_json_path = "resourcepack_files.json"
    
    # JSONファイルを作成または更新
    if mod_files is not None:
        create_or_update_json_file(mod_json_path, mod_files)
    if resourcepack_files is not None:
        create_or_update_json_file(resourcepack_json_path, resourcepack_files)

if __name__ == "__main__":
    main()
