import json
import codecs
import tkinter as tk
from tkinter import filedialog, messagebox


def unescape_strings(obj):
    if isinstance(obj, str):
        try:
            obj = codecs.decode(obj, "unicode_escape")
        except Exception:
            pass
        try:
            obj = obj.encode("latin1").decode("utf-8")
        except UnicodeDecodeError:
            pass
        return obj
    elif isinstance(obj, list):
        return [unescape_strings(i) for i in obj]
    elif isinstance(obj, dict):
        return {k: unescape_strings(v) for k, v in obj.items()}
    return obj


def extract_texts(node, out, counter):
    if isinstance(node, str) and node.startswith("^") and not node.startswith("^->"):
        key = f"line_{counter[0]:04d}"
        out[key] = node
        counter[0] += 1
    elif isinstance(node, list):
        for item in node:
            extract_texts(item, out, counter)
    elif isinstance(node, dict):
        for v in node.values():
            extract_texts(v, out, counter)


def merge_strings(node, line_iter):
    if isinstance(node, str):
        if node.startswith("^") and not node.startswith("^->"):
            try:
                return next(line_iter)
            except StopIteration:
                return node
        else:
            return node
    elif isinstance(node, list):
        return [merge_strings(i, line_iter) for i in node]
    elif isinstance(node, dict):
        return {k: merge_strings(v, line_iter) for k, v in node.items()}
    return node


def extract_action():
    path = filedialog.askopenfilename(title="Оберіть файл з оригінальним текстом")
    if not path:
        return

    with open(path, "rb") as f:
        raw = f.read().decode("utf-8")

    start_index = raw.find('{"inkVersion"')
    if start_index == -1:
        messagebox.showerror("Помилка", "Не знайдено 'inkVersion' у файлі.")
        return

    json_candidate = raw[start_index:]
    data_clean = unescape_strings(json_candidate)

    try:
        decoder = json.JSONDecoder()
        data, _ = decoder.raw_decode(data_clean)
    except Exception as e:
        messagebox.showerror("JSON помилка", str(e))
        return

    strings = {}
    extract_texts(data, strings, [1])

    out_path = filedialog.asksaveasfilename(defaultextension=".json", title="Куди зберегти strings.json")
    if out_path:
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(strings, f, ensure_ascii=False, indent=2)
        messagebox.showinfo("Готово", f"Збережено {len(strings)} рядків у {out_path}")


def merge_action():
    orig_path = filedialog.askopenfilename(title="Оберіть файл з оригінальним JSON (text.txt)")
    if not orig_path:
        return
    with open(orig_path, "rb") as f:
        raw = f.read().decode("utf-8")

    start_index = raw.find('{"inkVersion"')
    if start_index == -1:
        messagebox.showerror("Помилка", "Не знайдено 'inkVersion' у файлі.")
        return

    json_text = raw[start_index:]
    data_clean = unescape_strings(json_text)
    decoder = json.JSONDecoder()
    data_obj, _ = decoder.raw_decode(data_clean)

    strings_path = filedialog.askopenfilename(title="Оберіть strings1.json")
    if not strings_path:
        return
    with open(strings_path, "r", encoding="utf-8") as f:
        translated_strings = json.load(f)

    line_iter = iter(translated_strings.values())
    data_merged = merge_strings(data_obj, line_iter)

    out_path = filedialog.asksaveasfilename(defaultextension=".json", title="Куди зберегти merged_output.json")
    if out_path:
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(data_merged, f, ensure_ascii=False, separators=(',', ':'))
        messagebox.showinfo("Успіх", f"Збережено merged файл у {out_path}")


root = tk.Tk()
root.title("Ink Translator Tool")
root.geometry("400x200")

extract_btn = tk.Button(root, text="1. Витягнути рядки", command=extract_action, height=2, width=40)
extract_btn.pack(pady=10)

merge_btn = tk.Button(root, text="2. Вставити переклад назад", command=merge_action, height=2, width=40)
merge_btn.pack(pady=10)

root.mainloop()
