from pathlib import Path
from typing import List


def delete_file(path: Path) -> None:
    """Пробует удалить файл и выводит ошибку при неудаче."""
    try:
        path.unlink()
        print(f"[Удалено] {path}")
    except Exception as e:
        print(f"[Ошибка удаления] {path}: {e}")


def convert_py_to_txt(files: List[str], delete_original: bool = False) -> List[str]:
    converted_files = []

    for file_path in files:
        path = Path(file_path)
        if not path.exists() or path.suffix != '.py':
            continue

        try:
            content = path.read_text(encoding='utf-8')
            new_path = path.with_name(f"{path.stem}.txt")
            new_path.write_text(content, encoding='utf-8')
            converted_files.append(str(new_path))

            if delete_original:
                delete_file(path)

        except Exception as e:
            print(f"[Ошибка конвертации] {file_path}: {e}")

    return converted_files


def convert_txt_to_py(files: List[str], delete_original: bool = False) -> List[str]:
    converted_files = []

    for file_path in files:
        path = Path(file_path)
        if not path.exists() or path.suffix != '.txt':
            continue

        try:
            content = path.read_text(encoding='utf-8')
            new_path = path.with_name(f"{path.stem}.py")
            new_path.write_text(content, encoding='utf-8')
            converted_files.append(str(new_path))

            if delete_original:
                delete_file(path)

        except Exception as e:
            print(f"[Ошибка конвертации] {file_path}: {e}")

    return converted_files
