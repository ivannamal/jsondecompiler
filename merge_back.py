import json
from main1 import unescape_strings
# 1. Завантажуємо очищений JSON-обʼєкт
with open("orig text.txt", "rb") as f:
    raw = f.read().decode("utf-8")

start_index = raw.find('{"inkVersion"')
if start_index == -1:
    print("[!] Не знайдено 'inkVersion' у файлі.")
    exit(1)

json_text = raw[start_index:]

data_clean = unescape_strings(json_text)

# data_obj = json.loads(json_text)


decoder = json.JSONDecoder()
data_obj, _ = decoder.raw_decode(data_clean)

# 2. Завантажуємо перекладені рядки
with open("strings1.json", "r", encoding="utf-8") as f:
    translated_strings = json.load(f)

# 3. Створюємо ітератор рядків
line_iter = iter(translated_strings.values())

# 4. Вставляємо рядки рекурсивно
def merge_strings(node):
    if isinstance(node, str):
        if node.startswith("^") and not node.startswith("^->"):
            try:
                return next(line_iter)
            except StopIteration:
                print("[!] Закінчились рядки для вставки.")
                return node
        else:
            return node
    elif isinstance(node, list):
        return [merge_strings(i) for i in node]
    elif isinstance(node, dict):
        return {k: merge_strings(v) for k, v in node.items()}
    return node

# 5. Вставляємо назад
data_merged = merge_strings(data_obj)

# 6. Записуємо у файл
with open("merged_output.json", "w", encoding="utf-8") as f:
    json.dump(data_merged, f, ensure_ascii=False, separators=(',', ':'))

print("[✓] Рядки успішно вставлені назад у merged_output.json")
