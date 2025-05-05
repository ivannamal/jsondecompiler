import json
import codecs

with open("translation.txt", "rb") as f:
    raw = f.read().decode("utf-8")

start_index = raw.find('{"inkVersion"')
if start_index == -1:
    print("[!] Не знайдено 'inkVersion' у файлі.")
    exit(1)

json_candidate = raw[start_index:]


def unescape_strings(obj):
    if isinstance(obj, str):
        # 1) ordinary \uXXXX escape sequences
        try:
            obj = codecs.decode(obj, "unicode_escape")
        except Exception:
            pass  # nothing to un‑escape

        # 2) fix double‑decoding (mojibake) if possible
        try:
            obj = obj.encode("latin1").decode("utf-8")
        except UnicodeDecodeError:
            pass  # not mojibake – keep as is

        return obj

    elif isinstance(obj, list):
        return [unescape_strings(i) for i in obj]
    elif isinstance(obj, dict):
        return {k: unescape_strings(v) for k, v in obj.items()}
    return obj


data_clean = unescape_strings(json_candidate)

# decoded = bytes(json_candidate, "utf-8").decode("unicode_escape")
decoded = data_clean

# 4. Завантажуємо лише перший JSON-обʼєкт
try:
    decoder = json.JSONDecoder()
    data, _ = decoder.raw_decode(decoded)
except Exception as e:
    print("[!] JSON не вдалося розпарсити:", e)
    print("[DEBUG] JSON початок:", decoded[:500])
    pos = 2475351
    problem_char = decoded[pos]
    print(f"⛔ Проблемний символ: '{problem_char}' | Код: {ord(problem_char)}")
    context = 50
    before = decoded[max(0, pos - context):pos]
    char = decoded[pos]
    after = decoded[pos + 1:pos + context + 1]

    print("⬅️ Перед символом:\n", before)
    print("⛔ Проблемний символ:\n", repr(char), f"| Код: {ord(char)}")
    print("➡️ Після символа:\n", after)

    exit(1)

print("[✓] JSON успішно розпарсено.")


# 5. Витягуємо ^рядки
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


strings = {}
extract_texts(data, strings, [1])

# 6. Зберігаємо в strings.json
with open("strings1.json", "w", encoding="utf-8") as f:
    json.dump(strings, f, ensure_ascii=False, indent=2)

print(f"[+] Витягнуто {len(strings)} рядків у 'strings1.json'")
