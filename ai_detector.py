import streamlit as st
import re
import statistics

# ================= 1. 核心偵測邏輯 (Logic) =================
class AIDetector:
    def __init__(self):
        self.basic_rules = {
            "正式邏輯連接詞": {"keywords": ["此外", "然而", "總之", "不僅如此", "值得注意的是", "除此之外"], "weight": 15},
            "機器人語氣": {"keywords": ["作為一個", "這不僅僅是", "讓我們來看看", "在當今社會", "總結來說", "希望這對你有幫助"], "weight": 25}
        }
        
        self.functional_emojis = ["🏮", "💬", "📱", "💡", "✨", "🔥", "🧧", "🚀", "✅", "⚠️", "🏸", "📌", "🚩", "📝", "📊"]
        
        self.combo_features = [
            "有沒有發現", "這時候最需要的", "不需要.*也不用", "不用.*也不用", 
            "就是單純想", "你可能會說", "你可能會覺得", "對，但是", "沒錯",
            "換個方式", "我們在.*等你", "我們在.*見", "期待您的.*", "其實很.*",
            "不只是.*更是"
        ]

        self.human_features = {
            "在地口語": ["傻眼", "扯", "超強", "拜託", "真的很累", "超爽", "鳥事", "真的差很多", "沒在騙"],
            "語助詞": ["齁", "嘛", "啦", "囉", "呀", "吧", "呢", "欸", "喔"]
        }

    def analyze(self, text):
        results = []
        total_score = 0
        
        # 1. 功能型 Emoji 密度與結構偵測 (極限強化)
        found_emojis = [e for e in self.functional_emojis if e in text]
        if len(found_emojis) >= 3:
            # 基礎 Combo 分提高
            emoji_combo_score = 50 + (len(found_emojis) - 3) * 8
            
            # 偵測是否為「圖示清單」結構 (換行多代表正在用圖示分點)
            if text.count('\n') >= 5:
                emoji_combo_score += 25
                results.append(f"🚩 **結構性排版特徵**: 密集圖示結合多段換行結構 (+25)")
            
            total_score += emoji_combo_score
            results.append(f"🚩 **功能型圖示組合**: 偵測到 {len(found_emojis)} 種清單式 Emoji (+{emoji_combo_score})")
        elif len(found_emojis) > 0:
            total_score += len(found_emojis) * 2
            results.append(f"💡 **散落排版圖示**: 僅偵測到 {len(found_emojis)} 個圖示 (+{len(found_emojis)*2})")

        # 2. 基礎文字規則
        for rule_name, info in self.basic_rules.items():
            found = [f"「{w}」" for w in info["keywords"] if text.count(w) > 0]
            if found:
                curr_score = len(found) * info["weight"]
                total_score += curr_score
                results.append(f"📌 **{rule_name}**: {', '.join(found)} (+{curr_score})")

        # 3. 修辭組合特徵
        combo_count = 0
        triggered_words = []
        for pattern in self.combo_features:
            if re.search(pattern, text):
                combo_count += 1
                triggered_words.append(pattern.replace(".*", "..."))
        
        if combo_count >= 3:
            combo_score = 50 + (combo_count - 3) * 12
            total_score += combo_score
            results.append(f"🚩 **高階修辭套路**: 同時出現 {combo_count} 種 AI 常用技巧 (+{combo_score})")
        elif combo_count > 0:
            total_score += combo_count * 5
            results.append(f"💡 **正常修辭使用**: 偵測到 {combo_count} 項修辭 (+{combo_count*5})")

        # 4. 真人補償
        human_bonus = 0
        for feat, words in self.human_features.items():
            found = [w for w in words if w in text]
            if found:
                bonus = len(found) * 10
                human_bonus += bonus
                results.append(f"☘️ **真人特徵**: {', '.join(found)} (-{bonus})")
        total_score -= human_bonus

        # 5. 節奏感分析
        paragraphs = [p.strip() for p in text.split('\n') if len(p.strip()) > 5]
        if len(paragraphs) >= 3:
            lengths = [len(p) for p in paragraphs]
            stdev = statistics.stdev(lengths)
            avg_len = sum(lengths) / len(lengths)
            if stdev < (avg_len * 0.3):
                total_score += 35
                results.append(f"🚩 **段落規律**: 節奏過於均勻 (標差 {stdev:.1f}) (+35)")
            else:
                total_score -= 15
                results.append(f"✅ **段落自然**: 長度起伏較大 (標差 {stdev:.1f}) (-15)")
        
        return total_score, results

# ================= 2. 網頁介面呈現 (UI) =================

st.set_page_config(page_title="AI 文案偵測王 Pro", page_icon="🔍", layout="wide")

st.title("🔍 AI 文案特徵檢測器 (特徵密度強化版)")
st.markdown("本系統採用 **組合特徵門檻** 與 **Emoji 密度分析**，能精準識別「高階偽裝」的 AI 文案。")

with st.sidebar:
    st.header("⚙️ 偵測引擎狀態")
    st.success("✅ Emoji 密度門檻：已開啟")
    st.success("✅ 真人特徵補償：已開啟")
    st.success("✅ 段落節奏統計：已開啟")
    st.write("---")
    st.info("💡 **信心水準說明**：\n當文章同時具備多種功能性 Emoji、整齊段落與特定修辭套路時，分數會快速累積。")

col_input, col_result = st.columns([1.2, 1])

with col_input:
    st.subheader("📝 貼上待測文案")
    user_input = st.text_area("", height=500, placeholder="輸入文案以進行深度特徵分析...")
    analyze_btn = st.button("🚀 執行多重維度掃描", use_container_width=True)

with col_result:
    st.subheader("📊 偵測報告")
    if analyze_btn and user_input.strip():
        detector = AIDetector()
        score, details = detector.analyze(user_input)
        
        # --- 精簡後的門檻判定邏輯 ---
        if score >= 90:
            st.error(f"### 嫌疑得分：{score}")
            st.markdown("#### 🚨 偵測結果：**AI 原始模板 (Raw AI)**")
            st.caption("具備極高密集的 AI 標籤，幾乎確定為機器直接生成。")
        elif score >= 60:
            st.error(f"### 嫌疑得分：{score}")
            st.markdown("#### 🚩 偵測結果：**確定為 AI 生成 (Confirmed AI)**")
            st.caption("具備明顯的 AI 骨架與組合套路。")
        elif score >= 40:
            st.warning(f"### 嫌疑得分：{score}")
            st.markdown("#### ⚠️ 偵測結果：**高度 AI 參與 (Heavy Edit)**")
            st.caption("人機協作特徵明顯，核心排版邏輯仍為 AI 風格。")
        elif score >= 20:
            st.info(f"### 嫌疑得分：{score}")
            st.markdown("#### 💡 偵測結果：**疑似 AI 潤飾 (AI Assisted)**")
            st.caption("以真人寫作為主，但使用了部分 AI 的修辭組合或圖示習慣。")
        elif score > 0:
            st.success(f"### 嫌疑得分：{score}")
            st.markdown("#### ✅ 偵測結果：**表現自然 (Natural Writing)**")
            st.caption("特徵零星，符合人類自然的寫作慣性。")
        else:
            st.success(f"### 嫌疑得分：0 (或負分)")
            st.markdown("#### ✅ 偵測結果：**純真人手寫 (Pure Human)**")
            st.caption("完全避開機器邏輯，充滿個人情緒與口語特徵。")

        st.divider()
        if details:
            st.write("**🔍 特徵分析回報：**")
            for detail in details:
                st.write(detail)
    else:
        st.info("等待輸入文字後點擊掃描...")