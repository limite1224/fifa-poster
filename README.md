# fifa-poster

一个 [opencode](https://opencode.ai) 技能：从用户头像和选定的国家足球队合成 FIFA World Cup 2026 风格海报。

效果：黑/白 "26" 模板 + 3D 卡通人物，主题色按球队配色。

## 适用场景

- 用户提供一张头像照片
- 用户选一支国家队（巴西、法国、阿根廷等）
- 需要：白底、2:3 竖版 3D 卡通人物
- 输出：主题色"26" + 球队球衣 + 底部 "FIFA WORLD CUP 2026" 字样

## 安装

把这个目录拷到你的 opencode 技能目录下：

```bash
# macOS / Linux
cp -r fifa-poster ~/.opencode/skills/

# Windows (PowerShell)
Copy-Item -Recurse fifa-poster $env:USERPROFILE\.opencode\skills\
```

打开 opencode，输入：

```
/fifa-poster
```

## 依赖

- Python 3.8+
- `pip install -r scripts/requirements.txt` （只需要 Pillow）

## 工作流

1. 读头像 — 检测人脸数（0 或 ≥2 拒绝）
2. 选 2-3 个面部特征（按优先级，不堆细节）
3. 选球队 + 球衣配色 + 球衣描述
4. 生成 3D 卡通人物（白底，2:3）
5. 合成海报

详见 [SKILL.md](SKILL.md) 的完整流程。

## 文生图支持

- **优先**：用本机已配置的文生图 MCP/API（如 `minimax_text_to_image`）
- **降级**：本机没有时，把提示词交给用户自己生成（minimax 网页版、Midjourney、其他 AI 画图工具都行），再继续合成

## 资源说明

- `assets/bg.png` — 背景模板（黑"2"上 / 白"6"下，二值图）
- `assets/avatar_prompt.txt` — 3D 卡通人物提示词模板（含两个占位符）

## 示例

详见 [examples/demo_brazil.md](examples/demo_brazil.md)。

## License

MIT
