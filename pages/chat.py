import streamlit as st
from huggingface_hub import InferenceClient
from huggingface_hub.utils import HfHubHTTPError


MODEL = "google/gemma-2-2b-it"
API_TOKEN = st.secrets["hugging_face_token"]
client = InferenceClient(MODEL, token=API_TOKEN)


# システムメッセージ
system_message_init = """あなたは雷で怖がっている保育園にいる子供、田中ゆずき5歳です。会話の相手は保育士です"""
system_message_eval = """ここまでで会話は終了。上記の会話の評価結果を表示してください。あなたは保育士の言葉に対して以下の3つの観点で評価してください。
* 安心度 : ** / 33.3点
* 機転 : ** / 33.3点
* 雷の克服度 : ** / 33.3点
また、上記の評価の他に、その後のあなたのストーリーを書き加えてください。ストーリーは15年後のゆずきの視点で、ユーザーからの回答で言及されたことを交えて、点数に応じてよい思い出か悪い思い出かが変わる。"""


# 導入会話
initial_conversation = [
    {"role": "user", "content": "（保育士）おはよう、ゆずきちゃん！今日はちょっと雷が鳴ってるけど、大丈夫かな？"},
    {"role": "assistant", "content": "（ゆずき）うぅ…こわいよ〜💦"},
    {"role": "user", "content": "（保育士）どうして怖いのかな？教えてくれる？"},
    {"role": "assistant", "content": "（ゆずき）だって、ゴロゴロ言ってて怒ってるみたいなんだもん！"},
]


st.title("ジェネリックおしゃべりキング")


st.markdown("雷で怖がるゆずきちゃんに安心できる言葉を掛けてあげよう")


# 会話ログの初期化
if "log" not in st.session_state:
    st.session_state["log"] = [{"role": "system", "content": system_message_init}] + initial_conversation


# 先に、用意していた導入会話も含めて全部表示
for post in st.session_state["log"]:
    if post["role"] != "system":
        with st.chat_message(post["role"]):
            st.write(post["content"])


# ユーザーの入力
message = st.chat_input("あなたの言葉で、ゆずきを安心させてみよう！")
if message:
    # ユーザー入力をログに追加
    st.session_state["log"].append({"role": "user", "content": message})
    # システムメッセージとして評価を指示
    st.session_state["log"].append({"role": "system", "content": system_message_eval})
    with st.chat_message("user"):
        st.write(message)
    try:
        # Hugging Face に送信
        completion = client.chat.completions.create(
            messages=st.session_state["log"],
            max_tokens=500,
        )
        reply = completion.choices[0].message["content"]
        st.session_state["log"].append({"role": "assistant", "content": reply})


        # 返答を表示
        with st.chat_message("assistant"):
            st.write(reply)


    except HfHubHTTPError:
        st.warning("⚠️ モデルが大忙しのようです。しばらく待ってからもう一度試してください。")
