#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
智能报价系统 一键备份脚本

功能：
- 打包整个代码目录（排除 node_modules/.git/venv），保存为 .tar.gz
- 备份 PostgreSQL 数据库（自定义格式 .dump + 纯SQL .sql）
- 默认将备份放到 ./backups/<timestamp>

使用：
  python backend/scripts/backup_system.py \
    --code-path "." \
    --dest-root "./backups" \
    --db-name device_inventory --db-user device_inventory_user \
    --db-host localhost --db-port 5432 \
    --db-password "$DB_PASSWORD"

说明：
- 若未显式传入 --db-password，会尝试从环境变量 PGPASSWORD 读取
- 需要本机已安装 pg_dump 与 tar
"""

import argparse
import datetime
import os
import subprocess
import sys
from pathlib import Path


def run(cmd, env=None, cwd=None):
    """运行命令并实时输出，失败抛出异常。"""
    print("$", " ".join(cmd))
    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True,
        env=env,
        cwd=cwd,
    )
    for line in proc.stdout:  # type: ignore
        sys.stdout.write(line)
    ret = proc.wait()
    if ret != 0:
        raise RuntimeError(f"命令执行失败，返回码 {ret}: {' '.join(cmd)}")


def ensure_dir(path: Path):
    path.mkdir(parents=True, exist_ok=True)


def backup_code(code_path: Path, dest_dir: Path, ts: str) -> Path:
    out_file = dest_dir / f"智能报价系统_code_{ts}.tar.gz"
    # tar -czf out -C <parent> <dir> with excludes
    parent = code_path.parent
    target = code_path.name
    cmd = [
        "tar",
        "--exclude=*/node_modules/*",
        "--exclude=*/.git/*",
        "--exclude=*/venv/*",
        "-czf",
        str(out_file),
        "-C",
        str(parent),
        target,
    ]
    run(cmd)
    return out_file


def backup_db(db_name: str, db_user: str, db_host: str, db_port: int, db_password: str, dest_dir: Path, ts: str):
    env = os.environ.copy()
    if db_password:
        env["PGPASSWORD"] = db_password

    dump_file = dest_dir / f"{db_name}_{ts}.dump"
    sql_file = dest_dir / f"{db_name}_{ts}.sql"

    # 自定义格式
    run([
        "pg_dump",
        "-U",
        db_user,
        "-h",
        db_host,
        "-p",
        str(db_port),
        "-F",
        "c",
        "-f",
        str(dump_file),
        db_name,
    ], env=env)

    # 纯SQL
    run([
        "pg_dump",
        "-U",
        db_user,
        "-h",
        db_host,
        "-p",
        str(db_port),
        "-F",
        "p",
        "-f",
        str(sql_file),
        db_name,
    ], env=env)

    return dump_file, sql_file


def human_size(path: Path) -> str:
    try:
        out = subprocess.check_output(["du", "-sh", str(path)], universal_newlines=True)
        return out.split("\t")[0].strip()
    except Exception:
        return "-"


def main():
    parser = argparse.ArgumentParser(description="智能报价系统 一键备份")
    parser.add_argument("--code-path", default=".", help="代码根目录")
    parser.add_argument("--dest-root", default="./backups", help="备份根目录")
    parser.add_argument("--db-name", default="device_inventory")
    parser.add_argument("--db-user", default="device_inventory_user")
    parser.add_argument("--db-host", default="localhost")
    parser.add_argument("--db-port", type=int, default=5432)
    parser.add_argument("--db-password", default=os.environ.get("PGPASSWORD", ""))

    args = parser.parse_args()

    code_path = Path(args.code_path).resolve()
    if not code_path.exists():
        print(f"代码目录不存在: {code_path}")
        sys.exit(1)

    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    dest_dir = Path(args.dest_root).expanduser() / ts
    ensure_dir(dest_dir)

    print(f"备份目录: {dest_dir}")

    # 1) 代码备份
    print("\n[1/2] 备份代码...")
    code_tar = backup_code(code_path, dest_dir, ts)

    # 2) 数据库备份
    print("\n[2/2] 备份数据库...")
    dump_file, sql_file = backup_db(
        db_name=args.db_name,
        db_user=args.db_user,
        db_host=args.db_host,
        db_port=args.db_port,
        db_password=args.db_password,
        dest_dir=dest_dir,
        ts=ts,
    )

    size = human_size(dest_dir)
    print("\n备份完成:")
    print(f"- 目录: {dest_dir}")
    print(f"- 体积: {size}")
    print(f"- 代码压缩包: {code_tar.name}")
    print(f"- DB 自定义格式: {dump_file.name}")
    print(f"- DB 纯SQL: {sql_file.name}")


if __name__ == "__main__":
    main()
