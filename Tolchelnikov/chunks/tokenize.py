import os
import re

def split_markdown(input_file, max_chars=150000, min_chars=500):
    """
    Разрезает Markdown на части по max_chars.
    - Результаты сохраняются в папку, где лежит сам скрипт.
    - Дробит огромные блоки без заголовков.
    - Склеивает слишком маленькие финальные части с предыдущими.
    """
    # Папка, где лежит сам скрипт — теперь это целевая папка для вывода
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Поиск исходного файла (в папке скрипта или уровнем выше)
    path_options = [
        os.path.join(script_dir, input_file),
        os.path.join(script_dir, "..", input_file),
        input_file
    ]
    
    input_path = next((p for p in path_options if os.path.exists(p)), None)
    if not input_path:
        print(f"Ошибка: Файл '{input_file}' не найден.")
        return

    with open(input_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Сначала разбиваем по заголовкам первого уровня
    sections = re.split(r'(?=# )', content)
    
    # 2. Если секция без заголовков больше лимита — дробим её принудительно по строкам
    refined_sections = []
    for sec in sections:
        if len(sec) > max_chars:
            lines = sec.splitlines(keepends=True)
            sub_sec = ""
            for line in lines:
                if len(sub_sec) + len(line) > max_chars:
                    refined_sections.append(sub_sec)
                    sub_sec = line
                else:
                    sub_sec += line
            if sub_sec:
                refined_sections.append(sub_sec)
        else:
            refined_sections.append(sec)

    # 3. Собираем финальные чанки, соблюдая лимит
    chunks = []
    current_chunk = ""
    for sec in refined_sections:
        if len(current_chunk) + len(sec) > max_chars and current_chunk:
            chunks.append(current_chunk)
            current_chunk = sec
        else:
            current_chunk += sec
    if current_chunk:
        chunks.append(current_chunk)

    # 4. Фильтр "ерунды": если последний кусок слишком мал, приклеиваем его назад
    if len(chunks) > 1 and len(chunks[-1]) < min_chars:
        last_fragment = chunks.pop()
        chunks[-1] += last_fragment

    # Получаем базовое имя файла (без пути и расширения)
    base_name = os.path.splitext(os.path.basename(input_path))[0]
    
    # Сохранение: берем script_dir как базу
    for i, chunk in enumerate(chunks, 1):
        output_file = os.path.join(script_dir, f"{base_name}_part_{i}.md")
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(chunk.strip() + "\n")
        print(f"Создан файл: {output_file} ({len(chunk)} знаков)")

if __name__ == "__main__":
    # Вызов функции
    split_markdown("Talmud-2.1.6_raw.md", max_chars=150000)