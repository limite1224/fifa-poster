"""
调用 minimax MCP 文生图，生成 3D 卡通人物。

调用方式：
    python generate_character.py \\
        --prompt "完整英文提示词" \\
        --out <输出目录>

注：脚本本身不直接打 MCP——它只是把提示词写到 out/_prompt.txt 旁边，
由调用方（智能体）通过 minimax_text_to_image 工具生成。
这个脚本负责：把 prompt 落盘 + 接受生成结果路径 + 简单校验。
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    print("缺少 Pillow 库。请先运行: pip install -r requirements.txt", file=sys.stderr)
    sys.exit(2)


def main() -> int:
    ap = argparse.ArgumentParser(description="生成 3D 卡通人物（提示词准备）")
    ap.add_argument("--prompt", required=True, help="完整英文提示词")
    ap.add_argument("--out", required=True, help="输出目录")
    args = ap.parse_args()

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    prompt_path = out_dir / "character_prompt.txt"
    prompt_path.write_text(args.prompt, encoding="utf-8")
    print(f"提示词已写入: {prompt_path}")
    print("请用 minimax_text_to_image 或其他文生图工具生成 character.jpeg/jpg，")
    print("放到同一目录后用 compose_poster.py 合成。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
