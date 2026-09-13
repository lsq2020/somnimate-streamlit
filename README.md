# 眠伴 Streamlit 控制台

Streamlit 版提供用户画像、场景推荐、睡前待办、叫醒计划、可拖动及重置的阶段进度、24 段声音、语音便笺和可选 DeepSeek 文本陪伴。完整 3D、浏览器连续语音与自动阶段旅程通过页面顶部的主站入口提供。

## 本机运行

```bash
python -m pip install -r requirements.txt
streamlit run streamlit_app.py
```

DeepSeek 为可选功能。在本机创建不提交的 `.streamlit/secrets.toml`：

```toml
DEEPSEEK_API_KEY = "你的新密钥"
DEEPSEEK_MODEL = "deepseek-chat"
```

部署到 Streamlit Community Cloud 时，在 Advanced settings → Secrets 填写同样内容。不要把密钥提交到 GitHub。

页面内叫醒不能替代系统闹钟；睡眠数据为演示，不用于诊断。
