import zipfile_cp932 as zipfile
import os
import tkinter as tk
from tkinter import filedialog, simpledialog
import pyperclip
import webbrowser

def extract_zip(file_path, password=None):
    zip_dir = os.path.dirname(file_path)  # ZIPファイルのあるディレクトリ
    base_name = os.path.splitext(os.path.basename(file_path))[0]  # 拡張子を除いたファイル名
    extract_dir = os.path.join(zip_dir, base_name)  # 解凍先のディレクトリ
    os.makedirs(extract_dir, exist_ok=True)  # 解凍先ディレクトリを作成
    extracted_files = []  # 解凍されたファイルのリスト
    print(file_path)
    with zipfile.ZipFile(file_path, 'r') as zf:
        for f in zf.namelist():
            extracted_file_path = os.path.join(extract_dir, f)
            if f.endswith('/'):
                # ディレクトリの場合
                os.makedirs(extracted_file_path, exist_ok=True)
                print(f'mkdir: {extracted_file_path}')
            else:
                # ファイルの場合
                dir_name = os.path.dirname(extracted_file_path)
                if dir_name:
                    os.makedirs(dir_name, exist_ok=True)
                print(f'file: {extracted_file_path}')
                try:
                    with open(extracted_file_path, 'wb') as uzf:
                        uzf.write(zf.read(f, pwd=password))
                    extracted_files.append(extracted_file_path)
                except RuntimeError as e:
                    print(f'Error extracting {f}: {e}')
                    if "encrypted" in str(e) or "Bad password" in str(e):
                        return False, extracted_files  # パスワードが必要または間違っている場合
    return True, extracted_files  # 成功

def open_folder(folder_path):
    webbrowser.open(f'file:///{folder_path}')

def show_completion_dialog(original_file_path, extracted_files):
    folder_path = os.path.dirname(extracted_files[0]) if extracted_files else os.path.dirname(original_file_path)
    original_file_name = os.path.basename(original_file_path)

    completion_dialog = tk.Toplevel()
    completion_dialog.title("解凍完了")

    tk.Label(completion_dialog, text=f"元ファイル名：{original_file_name}", anchor='w').pack(fill='x', padx=10)

    if extracted_files:
        for file in extracted_files:
            file_name = os.path.basename(file)
            tk.Label(completion_dialog, text=f"解凍後ファイル名：{file_name}", anchor='w').pack(fill='x', padx=10)

    folder_label = tk.Label(completion_dialog, text=f"解凍先フォルダ：{folder_path}", fg="blue", cursor="hand2", anchor='w')
    folder_label.pack(fill='x', padx=10)

    def open_and_close():
        open_folder(folder_path)
        root.destroy()  # プログラムを終了

    folder_label.bind("<Button-1>", lambda e: open_and_close())

    def quit_app():
        root.destroy()  # プログラムを終了

    tk.Button(completion_dialog, text="完了", command=quit_app).pack(pady=10)

    def on_close():
        root.destroy()  # プログラムを終了

    completion_dialog.protocol("WM_DELETE_WINDOW", on_close)  # ウインドウが閉じられたときの処理

    completion_dialog.update_idletasks()
    completion_dialog.geometry(f"{completion_dialog.winfo_width()}x{completion_dialog.winfo_height()}")
    completion_dialog.mainloop()

def main():
    global root
    root = tk.Tk()
    root.withdraw()  # ルートウィンドウを隠す
    file_path = filedialog.askopenfilename(
        title="解凍するZIPファイルを選択してください",
        filetypes=[("Zip files", "*.zi *.zi_ *.zi_p *.zi p *.zip")]
    )

    if not file_path:
        print("ファイル選択がキャンセルされました。プログラムを終了します。")
        root.destroy()  # ファイル選択がキャンセルされたときにプログラムを終了
        return

    # 拡張子が .zi または .zi_ の場合、.zip に変更
    original_file_path = file_path  # 元のファイル名を保存
    if file_path.endswith('.zi'):
        new_file_path = file_path + "p"
        os.rename(file_path, new_file_path)
        file_path = new_file_path
    elif file_path.endswith('.zi_'):
        new_file_path = file_path[:-1] + "p"
        os.rename(file_path, new_file_path)
        file_path = new_file_path

    # クリップボードからパスワードを取得
    clipboard_data = pyperclip.paste()
    if len(clipboard_data) <= 50:
        initial_password = clipboard_data
    else:
        initial_password = ""

    # パスワード不要なZIPファイルを判定
    success, extracted_files = extract_zip(file_path)
    if not success:
        # パスワードが必要な場合、入力画面を表示
        password = simpledialog.askstring("パスワード", "ZIPファイルのパスワードを入力してください:", initialvalue=initial_password)
        success, extracted_files = extract_zip(file_path, password.encode())
        if not success:
            while True:
                password = simpledialog.askstring("パスワード", "ZIPファイルのパスワードを入力してください:", initialvalue="")
                if password is None:
                    print("パスワードが入力されませんでした。終了します。")
                    root.destroy()  # プログラムを終了
                    break
                else:
                    success, extracted_files = extract_zip(file_path, password.encode())
                    if success:
                        break
                    else:
                        print("パスワードが正しくありません。再試行してください。")

    if success:
        show_completion_dialog(original_file_path, extracted_files)
    else:
        root.destroy()  # エラー発生時にプログラムを終了

    root.mainloop()

if __name__ == "__main__":
    main()
