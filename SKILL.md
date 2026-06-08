---
name: fifa-poster
description: 从用户头像和选定球队生成 FIFA 2026 世界杯风格海报（黑/白 "26" 模板 + 3D 卡通人物）。在用户提到"世界杯海报"、"fifa poster"、"做个世界杯图"、或要求从头像生成足球风格海报时调用。
---

# fifa-poster

把用户的头像和选定的国家足球队合成成一张 FIFA World Cup 2026 风格海报。

## 资源

| 文件 | 作用 |
| --- | --- |
| `assets/bg.png` | 背景模板。黑色"2"(上) 和"6"(下) 在白底上。"26"会按球队两色重新着色；周围留白处变成深色背景。 |
| `assets/avatar_prompt.txt` | 3D 卡通人物提示词模板。含两个中文占位符：`<替换成球衣描述>` 和 `<替换成面部特征描述>`。 |

## 工作流（5 步）

### 第 1 步：读头像

用多模态能力读用户提供的头像图片。**硬性失败**条件：
- 没人脸 → 拒绝，让用户换图
- 超过 1 张人脸 → 拒绝，让用户换图

只提取**面部特征**（发际线、肤色、眼形、眉形等），**不要**提取服装和背景。

**特征选择规则（选 2-3 个，不是 8+ 个）**：多模态模型容易过度描述，太多细节会和模板里的"大头大眼大耳小额头"风格打架。读完照片后，从下面 7 个候选维度里只选 2-3 个有代表性的写进提示词：

1. 眼镜（最高优先级 — 最具识别度、最容易夸张；如果有，必选）
2. 肤色（白/黄/棕/黑等）
3. 发色 + 质地（黑色直发、棕色卷发、银色短卷等）
4. 鼻梁高低（高挺、平塌、小翘鼻等）
5. 嘴形 / 大小（笑得很大、樱桃小嘴等）
6. 嘴唇厚度（薄如刀片、丰厚嘟唇等）
7. 眉形 / 弧度（平直浓眉、高挑细眉等）

**冲突规则**：所选特征不能和模板里写死的 Pixar 风格重复。**不要**选"大眼睛"（模板里已有）、"窄额头"（模板里已有）、"小脸"（大头=小脸）。眼形相关特征模板里基本都覆盖了，除非用户有非常特殊的眼形（单眼皮、内双、深眼窝）才需要单独点出。

**夸张规则**：每个特征都要刻意放大，方便 3D 模型渲染。模型会柔化所有细节，所以提示词要往极端推：
- 小塌鼻 → "a very tall, sharply defined roman nose bridge"
- 略黑肤色 → "deep warm brown skin with rich golden undertones"
- 细圆眼镜 → "oversized round black-framed glasses, lenses as big as the eyes"
- 短直发 → "spiky jet-black hair standing straight up in thick tufts"
- 单眼皮 → "large almond eyes with a single, smooth upper lid, no visible crease"
- 薄唇 → "razor-thin pressed lips, almost a single line"
- 粗平眉 → "bold blocky straight brows like two thick brushstrokes"
- 咧嘴笑 → "an enormous wide grin stretching ear to ear"

不要选太泛无法夸张的特征（比如"一张嘴"没有修饰词）。不要超过 3 个。

### 第 2 步：选球队

询问用户要哪支球队（默认主队）。从球队里推出：
- 一个**深**色和一个**浅**色（球衣的两色）
- 一段**球衣描述**（条纹、领口、图案、赞助商标识等）
- **球衣简洁性偏好**：默认给一件干净的球衣，只在领口和袖口用第二色点缀。如果用户明确说"纯球衣 / no logo / no badge"之类，按用户说的做。

参考配色（按需告知用户）：
- 巴西：黄 `(251, 220, 22)` / 绿 `(10, 82, 54)` — 黄色字"26"，绿色背景
- 法国：海军蓝 `(0, 38, 84)` / 白 `(255, 255, 255)` — 白色字"26"，蓝色背景
- 阿根廷：天蓝白条 / 黑 — 蓝色背景
- 德国：黑 / 红 / 金 — 黑色背景
- …等等

### 第 3 步：生成 3D 卡通人物

**3a. 优先用本机 MCP/API**：检查用户当前 opencode 会话里有没有可用的文生图工具（`minimax_text_to_image` / 其他）。如果有，按下面规格调用：
- 提示词 = `assets/avatar_prompt.txt` 原文 + 替换两个占位符
- `aspect_ratio`: `"2:3"`（竖版，匹配 bg.png）
- `prompt_optimizer`: `false`（开了会改写光照/比例修饰，把硬边光又带回来）
- `n`: `1`
- 背景必须显式写 **"Solid pure white background"** 或 **"Solid white background"**，**不能**写"transparent"（模型不认，会自动渲染成主色），**不能**写其他颜色（后面的键控步骤假设白底）
- 末尾追加光照 + 比例修饰（写到占位符里，确保 prompt_optimizer 不删）：
  - 光照：`even soft diffused lighting on the face, no harsh shadows, uniform light across the face, low contrast, soft pastel tones`
  - 比例：`head to body ratio 3 to 1, very large head with a small body, the head ends at the chin with no visible neck, the neck is part of the body`
- MCP 返回的是**签名 URL**，不是本地文件。必须 `curl -o <local_path> "<url>"` 下载后再读

**3b. 没有文生图工具时的降级**：把上面拼好的完整英文提示词交给用户，告知用户用任何能生成图片的工具（minimax 网页版、其他 AI 画图工具都行）生成一张 **2:3 竖版、白底、3D 卡通**的人物图。让用户把图片保存到本地后提供路径，再继续第 4 步。

**关键约束（不论 3a 还是 3b）**：
- 球衣**主色不能是白、米白、奶白**（会和白底融合，键控失败）。如果用户选的球队主色是白色（如法国），调换深/浅色配对，让球衣主色变成第二色（法国的海军蓝），白色只用在领口/袖口点缀。
- 球衣不要有 logo、队徽、文字（除非用户明确要求）。默认走"干净纯色 + 第二色领口/袖口"。

### 第 4 步：着色背景

调 `scripts/compose_poster.py`，传入：
- `--bg assets/bg.png`
- `--dark "<深色 R,G,B>"`
- `--light "<浅色 R,G,B>"`

脚本做的事：
- 把 bg.png 的二值图按"黑→浅、白→深"重新着色
- 把"26"缩放到画布 85% 大小，居中放在深色画布上（留呼吸空间让人物略溢出）

不要手动改 bg.png，脚本会读它重新生成。

### 第 5 步：合成海报

继续调 `scripts/compose_poster.py`：
- `--character <第 3 步生成的人物图片路径>`
- `--out <输出目录>`
- `--name <文件名，比如 fifa_poster_brazil.png>`

脚本会做：
1. **4 角泛洪键控** 把人物的白底抠成透明（RGB ≥ 240 视为白）
2. 把人物宽度缩到背景 85% 宽，水平居中，垂直居中（人物比背景高，头会伸出"2"上、身子会伸到"6"下）
3. 在底部 94.5% 高度处加 `FIFA WORLD CUP 2026`（不带 ™）文字，深色填充 + 白色 3-4 px 描边

**输出目录**：当前项目根目录下的 `.output/fifa-poster/`。如果用户当前不在任何项目里（在根目录、`~`、或全局目录），问一次要存哪里；用户没有项目时建议默认存到 `~/Pictures/fifa-poster/`。

## MCP/工具依赖

- **生成图（步骤 3）**：需要文生图 MCP/API。**没有就降级**到手动生成模式，把提示词给用户。
- **拼图（步骤 4+5）**：本地 Python + Pillow。在合成前提示用户 `pip install -r scripts/requirements.txt`。
- **MCP 签名 URL**：`minimax_text_to_image` 返回的是带 `Expires` / `OSSAccessKeyId` / `Signature` 的 OSS URL，**必须**用 `curl -o` 下载到本地后再处理。

## 常见踩坑

- **不要**把"transparent"作为背景写进提示词 → 模型会渲染成主色（比如巴西那次渲染成纯黄底）。
- **不要**让 prompt_optimizer 默认开 → 会把光照/比例修饰改写掉。
- **不要**在步骤 5 里加 LIGHT 像素蒙版 / 鼻尖剪切。整张人物直接合成即可，**人物会部分覆盖"2"、"6"和中间的负空间，这是设计**。
- **不要**写"FIFA WORLD CUP 2026™" → 没有商标符号。
- **不要**在左上角加任何水印/标签。
- **不要**给球衣加 logo/队徽/赞助商文字（除非用户明确要）。
- **不要**选 8+ 个面部特征 → 会和模板的 Pixar 风格打架。

## 用户改默认时的回退

- 用户说"加队徽 / 加赞助商 / 加国旗" → 按用户说的做，但**仍然不要**写"transparent"背景。
- 用户说"换个字体 / 加个名字水印" → 调 `compose_poster.py` 的 `--label` 参数；更花哨的改写脚本里 `add_label` 函数。
- 用户说"我要分两次跑（先生成人物，再合成）" → 可以，步骤 3 完后保存人物图，步骤 4+5 后续再调。
