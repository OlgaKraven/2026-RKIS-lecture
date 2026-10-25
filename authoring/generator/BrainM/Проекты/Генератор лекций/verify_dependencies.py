#!/usr/bin/env python3
"""Check the pinned lecture-generator resources without network access or writes."""

import hashlib
import json
from pathlib import Path, PurePosixPath
import sys


def main():
    project_dir = Path(__file__).resolve().parent
    repo_root = project_dir.parents[2]
    lock = json.loads((project_dir / "dependencies.lock.json").read_text(encoding="utf-8"))
    if lock["schema_version"] != 1 or lock["path_base"] != "repository-root":
        raise ValueError("Неподдерживаемый формат dependencies.lock.json")

    seen = set()
    failures = []
    total = 0
    for dependency in lock["dependencies"]:
        files = dependency["files"]
        if not files:
            raise ValueError("В зависимости нет закреплённых файлов")
        before = len(failures)
        bundle = repo_root / PurePosixPath(dependency["entrypoint"]).parent
        expected_paths = {item["path"] for item in files}
        for path in bundle.rglob("*"):
            relative = path.relative_to(repo_root).as_posix()
            if "__pycache__" in path.parts or path.name in {".DS_Store", "desktop.ini", "Thumbs.db"}:
                continue
            if path.is_symlink():
                failures.append(f"Символьная ссылка требует отдельной проверки: {relative}")
            elif path.is_file() and relative not in expected_paths:
                failures.append(f"Файл не закреплён в зависимости: {relative}")
        for item in files:
            relative = PurePosixPath(item["path"])
            if relative.is_absolute() or ".." in relative.parts or relative.as_posix() in seen:
                raise ValueError("Недопустимый или повторный путь в dependencies.lock.json")
            seen.add(relative.as_posix())
            path = repo_root.joinpath(*relative.parts)
            try:
                path.resolve().relative_to(repo_root)
            except ValueError:
                raise ValueError("Путь зависимости выходит за пределы проекта") from None
            if not path.is_file():
                failures.append(f"Нет файла: {relative}")
                continue
            content = path.read_bytes()
            total += 1
            if len(content) != item["bytes"] or hashlib.sha256(content).hexdigest() != item["sha256"]:
                failures.append(f"Изменён файл: {relative}")
        if len(failures) == before:
            print(f"OK {dependency['id']}: {len(files)} файлов")

    if failures:
        print("\n".join(failures), file=sys.stderr)
        return 1
    print(f"Все зависимости совпадают: {total} файлов. Сеть и запись файлов не использовались.")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(f"Ошибка проверки зависимостей: {error}", file=sys.stderr)
        sys.exit(1)
