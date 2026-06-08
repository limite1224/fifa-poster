# 示例：巴西队海报（一次完整调用）

> **占位符说明**：示例中的所有路径都用了占位符，使用前请先替换成你自己的实际路径。

## 占位符

| 占位符 | 含义 | 建议设置方式 |
| --- | --- | --- |
| `<avatar>` | 用户头像图片路径 | 由用户在调用时提供 |
| `<output_dir>` | 临时生成图和最终海报的输出目录 | 例如 `~/Pictures/fifa-poster/` |

在跑下面的命令前，先设置环境变量：

```bash
# macOS / Linux
export OUTPUT_DIR=~/Pictures/fifa-poster
mkdir -p "$OUTPUT_DIR"

# Windows (PowerShell)
$env:OUTPUT_DIR = "$env:USERPROFILE\Pictures\fifa-poster"
New-Item -ItemType Directory -Force -Path $env:OUTPUT_DIR
```

下面所有命令都把 `<output_dir>` 替换成你的实际目录（例如 `$OUTPUT_DIR` 或 `%OUTPUT_DIR%`）。

---

## 用户

> /fifa-poster

## 智能体

> 请提供一张头像照片。

用户上传了 `<avatar>.jpg`（一张人脸照片）。

## 步骤 1：读头像

读到一张人脸。候选特征：
1. 眉形（粗、平直 → 选）
2. 肤色（略偏黄 → 选）
3. 发色 + 质地（黑色短直发 → 选）
4. 鼻梁（中等 → 不选，模板覆盖）
5. 嘴形（普通 → 不选，太泛）
6. 嘴唇厚度（中等 → 不选，模板覆盖）
7. 眼镜（无 → 跳过）

**写进提示词的特征（3 个）**：
- bold blocky straight brows like two thick brushstrokes
- warm light olive skin
- short jet-black straight hair with wispy bangs falling across the forehead

## 步骤 2：选球队

> 巴西

配色：
- 深色 = 巴西绿 `(10, 82, 54)`
- 浅色 = 巴西黄 `(251, 220, 22)`

球衣描述（用户没有特别偏好，按默认）：
> plain bright yellow t-shirt with a green ribbed crew neck collar and green sleeve cuffs, no logos, no text, no badges, no symbols, no patterns, completely clean plain jersey. The fabric has a subtle mesh texture.

## 步骤 3：生成 3D 卡通人物

本机有 `minimax_text_to_image`，调用：

```python
minimax_text_to_image(
    model="image-01",
    prompt="""Pixar 3D style, big-head big-eyes and big-ears,the forehead is small and narrow, Q-version chibi portrait of the person, front-facing, three-quarter bust framing, open smile with visible white teeth, soft skin shading, large expressive eyes,
plain bright yellow t-shirt with a green ribbed crew neck collar and green sleeve cuffs, no logos, no text, no badges, no symbols, no patterns, completely clean plain jersey. The fabric has a subtle mesh texture. Solid pure white background (mandatory, do not use any other color, do not use transparent). Match the lighting and color palette of the.Preserve the subject's facial features, hairline, and skin tonebold blocky straight brows like two thick brushstrokes, warm light olive skin, short jet-black straight hair with wispy bangs falling across the forehead. even soft diffused lighting on the face, no harsh shadows, uniform light across the face, low contrast, soft pastel tones. head to body ratio 3 to 1, very large head with a small body, the head ends at the chin with no visible neck, the neck is part of the body.""",
    aspect_ratio="2:3",
    n=1,
    prompt_optimizer=False,
    output_directory="<output_dir>"
)
```

返回的是**签名 URL**（不是本地文件），下载到本地：

```bash
curl -o <output_dir>/character_brazil.jpeg "<signed_url>"
```

人物文件：`<output_dir>/character_brazil.jpeg`

## 步骤 4+5：合成海报

```bash
# 把 <output_dir> 替换成实际路径
python <skill_dir>/scripts/compose_poster.py \
  --character <output_dir>/character_brazil.jpeg \
  --bg <skill_dir>/assets/bg.png \
  --dark "10,82,54" \
  --light "251,220,22" \
  --out <output_dir> \
  --name fifa_poster_brazil.png
```

`<skill_dir>` 是技能安装位置，默认是 `~/.opencode/skills/fifa-poster`（Windows 下为 `%USERPROFILE%\.opencode\skills\fifa-poster`）。

输出：`<output_dir>/fifa_poster_brazil.png`
