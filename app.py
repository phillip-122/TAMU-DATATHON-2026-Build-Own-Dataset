"""HOUSE OF MINDS — interactive TAMU Datathon randomness experiment.

Install beside mind_engine.py and your ORIGINAL real_participants.csv.
No timer. Two sections: Generate Randomness and Human or Computer?
No writes to or modifications of the original participant dataset.
"""
from __future__ import annotations

from html import escape
from pathlib import Path

import streamlit as st

from mind_engine import (
    alternations, create_game, longest_run, parse_participants,
    sample_summary,
)

st.set_page_config(
    page_title="House of Minds · Can Humans Be Random?",
    page_icon="🧠", layout="wide", initial_sidebar_state="collapsed",
)

STYLE = """
<style>
  :root { --maroon:#500000; --deep:#321b23; --ink:#25212a; --muted:#77717b;
          --cream:#faf7f2; --paper:#ffffff; --edge:#e9e4df; --gold:#c9a05e; }
  [data-testid="stAppViewContainer"] { background:#faf7f2; }
  [data-testid="stHeader"] { background:#faf7f2; }
  [data-testid="stSidebar"] { display:none; }
  .block-container {max-width:1060px !important; padding-top:1.3rem !important;
                    padding-bottom:3rem !important;}
  html, body, [data-testid="stAppViewContainer"] { color: #25212a; }
  h1, h2, h3, p { letter-spacing:-.015em; }
  .hm-brand { background:linear-gradient(118deg,#321b23 0%,#500000 72%,#723940 100%);
      color:white; border-radius:22px; padding:22px 28px; position:relative;
      overflow:hidden; box-shadow:0 12px 30px rgba(52,14,21,.13); }
  .hm-brand::after {content:'✦'; position:absolute; right:30px; top:-17px;
      font-size:110px; color:rgba(255,255,255,.045); pointer-events:none;}
  .hm-brand h1 { color:#fff9f2 !important; margin:0; font-size:31px; line-height:1.2;
      font-weight:820; letter-spacing:-1px; }
  .hm-brand .sub { color:#e6d1cc; margin-top:7px; font-size:14px; }
  .hm-eyebrow {text-transform:uppercase; font-size:11px; font-weight:800; letter-spacing:2px;
     color:#94674e; margin:12px 0 6px;}
  .hm-heading {font-size:29px; font-weight:820; line-height:1.17; color:#251b21;
     letter-spacing:-.8px; margin:3px 0 6px;}
  .hm-lead {font-size:15px; color:#6d6670; margin:0 0 12px; line-height:1.6;}
  .hm-line {height:1px; background:#e7e0dc; margin:14px 0;}
  .hm-stage {display:flex;gap:7px;margin:12px 0 18px;}
  .hm-stage span {height:5px; flex:1; background:#e8dedb;border-radius:50px;}
  .hm-stage span.active {background:#500000;}
  .hm-card {background:white;border:1px solid #e9e4df;border-radius:19px;
     padding:16px 20px;margin:10px 0;box-shadow:0 4px 22px rgba(33,22,30,.035);}
  .hm-kicker {font-size:11px; font-weight:800; color:#806a62;
     letter-spacing:1.4px;text-transform:uppercase;}
  .hm-coinstrip {display:flex;gap:12px;justify-content:center;flex-wrap:wrap;margin:20px auto;}
  .hm-coin {height:75px;width:75px;display:flex;align-items:center;justify-content:center;
     border-radius:50%;font-size:28px;font-weight:800;border:3px solid;
     box-shadow:inset 0 -5px 0 rgba(0,0,0,.055),0 7px 19px rgba(19,15,20,.07);
     animation:hm-pop .24s ease-out;}
  .hm-coin.h {background:#fff1d2; color:#69330c;border-color:#dcb86a;}
  .hm-coin.t {background:#343746; color:#fff;border-color:#707585;}
  .hm-coin.empty {background:#faf6f1;border:2px dashed #d9cdc7;color:#c8bbb5;box-shadow:none;}
  @keyframes hm-pop {from{transform:scale(.86);opacity:.5}to{transform:scale(1);opacity:1}}
  .hm-numbers {display:flex;gap:10px;flex-wrap:wrap;justify-content:center;margin:14px 0;}
  .hm-number {min-width:50px;padding:12px;border-radius:12px;background:#f6eee7;
      color:#500000;border:1px solid #eadbd4;font-weight:800;text-align:center;}
  .hm-pill {display:inline-block;background:#f2e8dd;border:1px solid #e6d4c7;
      color:#6d3c28;border-radius:999px;padding:5px 11px;font-size:12px;font-weight:700;margin:2px;}
  .hm-primary-stat {font-size:38px;font-weight:850;color:#500000;line-height:1.1;margin:5px 0;}
  .hm-small {font-size:13px;color:#77717b;line-height:1.5;}
  .hm-result {background:#fff;border:1px solid #e9e2dd;border-radius:20px;
      padding:23px;box-shadow:0 8px 30px rgba(20,5,13,.04);margin:14px 0;}
  .hm-result h3 {font-size:19px;margin:0 0 12px;color:#2d2326;}
  .hm-result p {color:#6e6267;font-size:14px;line-height:1.6;}
  .hm-tiles {display:grid;grid-template-columns:repeat(3,1fr);gap:8px;margin-top:12px;}
  .hm-tile {padding:12px;background:#f8f3ed;border-radius:13px;text-align:center;}
  .hm-tile .v {font-size:24px;font-weight:800;color:#500000;}
  .hm-tile .k {font-size:11px;color:#80747b;line-height:1.3;}
  .hm-bar {height:12px;background:#eee8e5;border-radius:10px;overflow:hidden;margin:10px 0;}
  .hm-bar .inner {height:100%;background:linear-gradient(90deg,#500000,#a25c59);border-radius:10px;}
  .hm-reveal {padding:21px 24px;border-radius:19px;background:#fff;border:1px solid #e7e2df;
      margin:15px 0;box-shadow:0 8px 28px rgba(0,0,0,.03);}
  .hm-reveal.good {border-left:6px solid #3d9063;}
  .hm-reveal.bad {border-left:6px solid #b75a4d;}
  .hm-reveal.good, .hm-reveal.bad {animation:hm-reveal-in .32s ease-out;}
  .hm-verdict {display:inline-block;padding:7px 13px;border-radius:999px;
      font-size:14px;font-weight:850;letter-spacing:1px;margin-bottom:12px;}
  .good .hm-verdict {background:#e6f4eb;color:#23613e;}
  .bad .hm-verdict {background:#fcece7;color:#933a2d;}
  .hm-discovery {background:#fff1d2;border:1px solid #e3c78a;border-radius:19px;
      padding:20px 24px;margin:18px 0;}
  .hm-discovery .big {font-size:32px;font-weight:850;color:#500000;line-height:1.2;}
  .hm-discovery p {margin:8px 0 0;color:#654e3c;}
  @keyframes hm-reveal-in {from{transform:translateY(8px);opacity:0}to{transform:translateY(0);opacity:1}}
  @media(prefers-reduced-motion:reduce) {
      .hm-coin, .hm-reveal.good, .hm-reveal.bad {animation:none;}
      .stButton>button {transition:none !important;}
  }
  .hm-reveal .big {font-size:26px;font-weight:850;color:#262027;}
  .hm-foot {font-size:11px;color:#887e83;line-height:1.6;text-align:center;
      border-top:1px solid #e9e3df;padding-top:20px;margin-top:30px;}
  [data-testid="stVerticalBlockBorderWrapper"] {border-color:#e7e1df !important;
      background:#fff !important;border-radius:18px !important;
      box-shadow:0 5px 24px rgba(36,24,26,.03);}
  [data-testid="stMetric"] {background:#fff;border:1px solid #e9e2de;
      border-radius:16px;padding:12px 17px;}
  [data-testid="stMetricValue"] {color:#500000;font-weight:800;}
  .stButton>button {border-radius:13px !important;min-height:43px !important;
      font-weight:700 !important;border:1px solid #ded2cf !important;
      transition:transform .14s ease, box-shadow .14s ease !important;}
  .stButton>button:hover {border-color:#8e6262 !important;
      transform:translateY(-1px);box-shadow:0 6px 16px rgba(70,25,25,.08);}
  button[kind="primary"] {background:#500000 !important;
      color:#fff !important;border-color:#500000 !important;}
  button[kind="primary"]:hover {background:#6c2020 !important;}
  [data-testid="stTextInput"] input {border-radius:12px !important;
      background:#fff !important;color:#25212a !important;}
  @media(max-width:680px) {
     .hm-brand {padding:18px;} .hm-brand h1 {font-size:25px;}
     .hm-coinstrip {gap:6px;} .hm-coin{height:45px;width:45px;font-size:19px;}
     .hm-heading{font-size:24px;} .hm-result{padding:15px;}
     .block-container {padding-left:1rem !important;padding-right:1rem !important;}
  }
</style>
"""
st.markdown(STYLE, unsafe_allow_html=True)


def locate_csv() -> Path | None:
    base = Path(__file__).resolve().parent
    for relative in (
        "real_participants.csv", "data/real_participants.csv", "participants.csv",
        "data/participants.csv", "human_behavior.csv", "data/human_behavior.csv",
    ):
        target = base / relative
        if target.is_file():
            return target
    return None


def load_real_data() -> list[dict]:
    """Load ONLY original local CSV or user's uploaded CSV; never use demo humans."""
    if "uploaded_real_data" in st.session_state:
        return st.session_state["uploaded_real_data"]
    path = locate_csv()
    if path is None:
        st.error("I can't find your original participant CSV in this app folder.")
        st.info("Place your original `real_participants.csv` beside `app.py`, "
                "or upload the file below for this browser session. "
                "No human data will be fabricated.")
        upload = st.file_uploader("Upload your real participant CSV", type=["csv", "tsv"])
        if upload:
            try:
                st.session_state["uploaded_real_data"] = parse_participants(upload.getvalue())
                st.rerun()
            except ValueError as exc:
                st.error(f"Data format problem: {exc}")
        st.stop()
    try:
        return parse_participants(path.read_bytes())
    except ValueError as exc:
        st.error(f"Please check {path.name}: {exc}")
        st.caption("The original data was not modified. The app refuses to replace it with fake data.")
        st.stop()


def initialize_state() -> None:
    defaults = {
        "section": "generate", "step": "coin", "flips": [],
        "num_small": None, "num_large_draft": "", "game": None,
        "round_index": 0, "revealed": False, "guess": None,
        "player_score": 0, "model_score": 0,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


def navigate(section: str) -> None:
    st.session_state["section"] = section


def set_step(step: str) -> None:
    st.session_state["step"] = step


def add_flip(value: str) -> None:
    if len(st.session_state["flips"]) < 6:
        st.session_state["flips"] = st.session_state["flips"] + [value]


def undo_flip() -> None:
    st.session_state["flips"] = st.session_state["flips"][:-1]


def clear_flips() -> None:
    st.session_state["flips"] = []


def choose_small(n: int) -> None:
    st.session_state["num_small"] = n


def save_large() -> None:
    st.session_state["num_large_draft"] = st.session_state.get("large_number_widget", "")


def large_number() -> int | None:
    s = str(st.session_state.get("large_number_widget",
                                 st.session_state.get("num_large_draft", ""))).strip()
    if not s.isdigit():
        return None
    n = int(s)
    return n if 1 <= n <= 100 else None


def numbers_done() -> None:
    save_large()
    if st.session_state["num_small"] is not None and large_number() is not None:
        st.session_state["step"] = "results"


def restart_generate() -> None:
    st.session_state["flips"] = []
    st.session_state["num_small"] = None
    st.session_state["num_large_draft"] = ""
    st.session_state.pop("large_number_widget", None)
    st.session_state["step"] = "coin"
    st.session_state["section"] = "generate"


def start_game(participants: list[dict]) -> None:
    st.session_state["game"] = create_game(participants)
    st.session_state["round_index"] = 0
    st.session_state["revealed"] = False
    st.session_state["guess"] = None
    st.session_state["player_score"] = 0
    st.session_state["model_score"] = 0
    st.session_state["section"] = "guess"


def make_guess(value: str) -> None:
    if st.session_state["revealed"]:
        return
    item = st.session_state["game"]["rounds"][st.session_state["round_index"]]
    st.session_state["guess"] = value
    st.session_state["revealed"] = True
    if item["source"] == value:
        st.session_state["player_score"] += 1
    if item["prediction"] == item["source"]:
        st.session_state["model_score"] += 1


def next_round() -> None:
    st.session_state["round_index"] += 1
    st.session_state["revealed"] = False
    st.session_state["guess"] = None


def coin_html(seq: str, placeholders: bool = True) -> str:
    tiles = []
    for c in seq:
        classes = "h" if c == "H" else "t"
        tiles.append(f'<div class="hm-coin {classes}">{c}</div>')
    if placeholders:
        tiles.extend('<div class="hm-coin empty">·</div>' for _ in range(max(0, 6-len(seq))))
    return '<div class="hm-coinstrip">' + "".join(tiles) + '</div>'


def stepbar(step: str) -> None:
    num = {"coin": 1, "numbers": 2, "results": 3}[step]
    st.markdown('<div class="hm-stage">' +
                ''.join('<span class="active"></span>' if i <= num else '<span></span>'
                        for i in range(1, 4)) + '</div>', unsafe_allow_html=True)


def render_header(participants: list[dict]) -> None:
    count = len(participants)
    st.markdown(
        f'<div class="hm-brand"><h1>✦ House of Minds</h1>'
        f'<div class="sub">Can humans actually be random? &nbsp;·&nbsp; '
        f'An interactive experiment powered by <b>{count} real participants</b></div></div>',
        unsafe_allow_html=True,
    )
    st.write("")
    st.caption(f"THE DATA · {count} real participants supplied the human responses. "
               "Both games use their first six recorded flips; computer sequences "
               "are generated independently as fair-coin flips.")
    a, b = st.columns(2, gap="small")
    a.button("01   ·   Generate Randomness", key="nav_generate",
             type="primary" if st.session_state["section"] == "generate" else "secondary",
             use_container_width=True, on_click=navigate, args=("generate",))
    b.button("02   ·   Human or Computer?", key="nav_guess",
             type="primary" if st.session_state["section"] == "guess" else "secondary",
             use_container_width=True, on_click=navigate, args=("guess",))
    st.write("")


def render_generate(participants: list[dict]) -> None:
    step = st.session_state["step"]
    stepbar(step)
    if step == "coin":
        st.markdown('<div class="hm-eyebrow">Challenge 01 / 02</div>'
                    '<div class="hm-heading">Think like a coin.</div>'
                    '<div class="hm-lead">Without flipping a real coin, imagine six random flips. '
                    'Make each choice one at a time.</div>', unsafe_allow_html=True)
        with st.container(border=True):
            count = len(st.session_state["flips"])
            st.caption(f"YOUR SEQUENCE · {count} OF 6")
            st.markdown(coin_html("".join(st.session_state["flips"])), unsafe_allow_html=True)
            c1, c2 = st.columns(2, gap="medium")
            c1.button("H  ·  HEADS", use_container_width=True, type="primary",
                      on_click=add_flip, args=("H",), disabled=count == 6, key="btn_h")
            c2.button("T  ·  TAILS", use_container_width=True, type="primary",
                      on_click=add_flip, args=("T",), disabled=count == 6, key="btn_t")
            c3, c4 = st.columns(2)
            c3.button("↶  Undo last", use_container_width=True,
                      on_click=undo_flip, disabled=count == 0)
            c4.button("Reset sequence", use_container_width=True,
                      on_click=clear_flips, disabled=count == 0)
        a, b = st.columns([1, 1])
        with b:
            st.button("Continue  →", type="primary", use_container_width=True,
                      disabled=count != 6, on_click=set_step, args=("numbers",))
        st.caption("Your choices won't be compared with the original participants until after the final step.")

    elif step == "numbers":
        st.markdown('<div class="hm-eyebrow">Challenge 02 / 02</div>'
                    '<div class="hm-heading">Pick the first number that feels random.</div>'
                    '<div class="hm-lead">Choose one integer in each range. There are no '
                    'right answers; trust your first instinct.</div>', unsafe_allow_html=True)
        with st.container(border=True):
            st.markdown('**1. Choose a number from 1–10**')
            chosen = st.session_state["num_small"]
            for start in (1, 6):
                cols = st.columns(5, gap="small")
                for col, n in zip(cols, range(start, start+5)):
                    col.button(str(n), key=f"pick_{n}", use_container_width=True,
                               type="primary" if n == chosen else "secondary",
                               on_click=choose_small, args=(n,))
            if chosen is not None:
                st.caption(f"Your selection: {chosen} · You can change it anytime.")
            st.markdown('<div class="hm-line"></div>', unsafe_allow_html=True)
            st.markdown('**2. Choose a number from 1–100**')
            if "large_number_widget" not in st.session_state:
                st.session_state["large_number_widget"] = st.session_state["num_large_draft"]
            st.text_input("Enter your number (no preselected value)",
                          key="large_number_widget", placeholder="1 to 100",
                          max_chars=3, on_change=save_large)
            raw = str(st.session_state.get("large_number_widget", "")).strip()
            if raw and large_number() is None:
                st.warning("Please enter a whole number between 1 and 100.")
            elif large_number() is not None:
                st.caption(f"Selected: {large_number()} · You can change it anytime.")
        a, b = st.columns(2)
        a.button("←  Back to coin flips", use_container_width=True,
                 on_click=set_step, args=("coin",))
        b.button("Reveal my results  →", type="primary", use_container_width=True,
                 disabled=(chosen is None or large_number() is None),
                 on_click=numbers_done)

    else:
        render_results(participants)


def result_card(title: str, body: str) -> None:
    st.markdown(f'<div class="hm-result"><h3>{escape(title)}</h3>{body}</div>',
                unsafe_allow_html=True)


def render_results(participants: list[dict]) -> None:
    flips = "".join(st.session_state["flips"])
    small = st.session_state["num_small"]
    raw_large = str(st.session_state.get("num_large_draft", "")).strip()
    large = int(raw_large) if raw_large.isdigit() and 1 <= int(raw_large) <= 100 else None
    if len(flips) != 6 or small is None or large is None:
        st.warning("Complete the two challenges before viewing results.")
        st.button("Return to the experiment", on_click=set_step, args=("coin",))
        return
    summary = sample_summary(participants)
    n = summary["n"]
    first_count = summary["heads_first"] if flips[0] == "H" else n-summary["heads_first"]
    switches = alternations(flips)
    longest = longest_run(flips)
    st.markdown('<div class="hm-eyebrow">Your personal reveal</div>'
                '<div class="hm-heading">How human is your randomness?</div>'
                '<div class="hm-lead">Your responses, compared with real collected '
                'human choices and a fair-coin baseline.</div>', unsafe_allow_html=True)
    st.markdown(coin_html(flips, placeholders=False), unsafe_allow_html=True)
    st.markdown(
        '<div class="hm-discovery"><div class="hm-kicker">The pattern in our dataset</div>'
        f'<div class="big">{summary["heads_first"]} of {n} started with Heads.</div>'
        f'<p>That’s <b>{summary["heads_first"]/n:.0%}</b> of the real participants, '
        'compared with a fair coin’s 50% starting probability. '
        'This describes our small sample; it does not predict every person.</p></div>',
        unsafe_allow_html=True,
    )
    a, b = st.columns(2, gap="medium")
    with a:
        first_label = "Heads" if flips[0] == "H" else "Tails"
        body = (f'<div class="hm-kicker">First instinct</div>'
                f'<div class="hm-primary-stat">{first_label}</div>'
                f'<p><b>{first_count} of {n}</b> original participants also started '
                f'with {first_label} ({first_count/n:.0%}). A fair coin would start '
                f'with either side 50% of the time.</p>'
                f'<div class="hm-bar"><div class="inner" '
                f'style="width:{100*first_count/n:.1f}%"></div></div>')
        result_card("Your first choice", body)
    with b:
        body = ('<div class="hm-tiles">'
                f'<div class="hm-tile"><div class="v">{flips.count("H")}/6</div><div class="k">Heads</div></div>'
                f'<div class="hm-tile"><div class="v">{switches}/5</div><div class="k">Side switches</div></div>'
                f'<div class="hm-tile"><div class="v">{longest}</div><div class="k">Longest streak</div></div>'
                '</div>'
                f'<p>Participants averaged <b>{summary["mean_alternations"]:.2f}</b> '
                f'switches per sequence. A fair coin averages <b>2.5</b> switches '
                f'across five transitions. A single sequence cannot prove randomness.</p>')
        result_card("Your six flips", body)
    a, b = st.columns(2, gap="medium")
    with a:
        total = summary["small_n"]
        if total:
            observed = summary["small_counts"][small]
            comparison = (f'{observed} of {total} participants chose {small} '
                          f'({observed/total:.0%}). Uniform random selection '
                          f'would choose each number about 10% of the time.')
        else:
            comparison = "This field wasn't available in the original CSV."
        result_card("Your number · 1–10",
                    f'<div class="hm-primary-stat">{small}</div><p>{comparison}</p>')
    with b:
        total = summary["large_n"]
        if total:
            observed = summary["large_counts"][large]
            comparison = (f'{observed} of {total} participants chose {large}. '
                          'With 100 possible choices and a small sample, '
                          'many numbers may never appear—even under a fair generator.')
        else:
            comparison = "This field wasn't available in the original CSV."
        result_card("Your number · 1–100",
                    f'<div class="hm-primary-stat">{large}</div><p>{comparison}</p>')
    st.info("**Takeaway:** Human choices can show biases, but six flips and two "
            "number choices cannot establish whether an individual is random. "
            "The original data is small, so these comparisons are exploratory.")
    a, b, c = st.columns([1, 1, 1])
    a.button("←  Edit numbers", on_click=set_step, args=("numbers",),
             use_container_width=True)
    b.button("Start over", on_click=restart_generate, use_container_width=True)
    c.button("Play Human or Computer  →", on_click=navigate, args=("guess",),
             use_container_width=True, type="primary")


def render_game(participants: list[dict]) -> None:
    if st.session_state["game"] is None:
        start_game(participants)
    game = st.session_state["game"]
    idx = st.session_state["round_index"]
    rounds = game["rounds"]
    st.markdown('<div class="hm-eyebrow">Section 02 / Human vs machine</div>'
                '<div class="hm-heading">Human or Computer?</div>'
                '<div class="hm-lead">A real participant imagined this sequence, or a '
                'computer generated six independent fair coin flips. Can you tell which?</div>',
                unsafe_allow_html=True)
    x, y, z = st.columns(3, gap="small")
    x.metric("YOU", f'{st.session_state["player_score"]} correct')
    y.metric("THE MODEL", f'{st.session_state["model_score"]} correct')
    completed = min(idx + int(st.session_state["revealed"]), len(rounds))
    z.metric("ROUNDS COMPLETED", f'{completed} / {len(rounds)}')

    if idx >= len(rounds):
        st.markdown('<div class="hm-reveal"><div class="hm-kicker">Game complete</div>'
                    '<div class="big">Can you outsmart the machine?</div></div>',
                    unsafe_allow_html=True)
        a, b = st.columns(2)
        a.metric("Your accuracy", f'{st.session_state["player_score"]}/{len(rounds)}')
        b.metric("Model accuracy", f'{st.session_state["model_score"]}/{len(rounds)}')
        st.info("The model only uses a first-flip pattern learned from other "
                "participants (not the five human examples shown in this game). "
                "Six-flip sequences can arise from either source. High accuracy "
                "in one ten-round game is not evidence of broad prediction skill.")
        a, b = st.columns(2)
        a.button("↻  Play again", use_container_width=True, type="primary",
                 on_click=start_game, args=(participants,))
        b.button("←  Generate Randomness", use_container_width=True,
                 on_click=navigate, args=("generate",))
        return

    item = rounds[idx]
    st.markdown('<div class="hm-eyebrow" style="text-align:center">'
                f'ROUND {idx+1} OF {len(rounds)}</div>', unsafe_allow_html=True)
    st.markdown(coin_html(item["sequence"], placeholders=False), unsafe_allow_html=True)
    if not st.session_state["revealed"]:
        st.markdown('<div style="text-align:center;color:#75676c;font-weight:700;'
                    'margin:4px 0 14px">Who made these six flips?</div>',
                    unsafe_allow_html=True)
        left, human, computer, right = st.columns([.35, 1, 1, .35], gap="medium")
        human.button("👤  HUMAN", type="primary", key="guess_human",
                     use_container_width=True, on_click=make_guess, args=("HUMAN",))
        computer.button("💻  COMPUTER", type="primary", key="guess_computer",
                        use_container_width=True, on_click=make_guess, args=("COMPUTER",))
        st.caption("Computer sequences are simulated fair-coin draws. "
                   "Human sequences come directly from the original participant CSV.")
    else:
        correct = st.session_state["guess"] == item["source"]
        state_cls = "good" if correct else "bad"
        title = "That's right!" if correct else "Not this time."
        source_desc = ("a real participant in the collected dataset" if item["source"] == "HUMAN"
                       else "a computer making independent fair-coin flips")
        p_human = item["p_human"]
        st.markdown(
            f'<div class="hm-reveal {state_cls}">'
            f'<div class="hm-verdict">{"✓ CORRECT" if correct else "✕ INCORRECT"}</div>'
            f'<div class="hm-kicker">Source revealed</div>'
            f'<div class="big">{title} &nbsp; It was {item["source"].title()}.</div>'
            f'<p>This sequence was made by {source_desc}.</p>'
            f'<span class="hm-pill">Your guess: {st.session_state["guess"].title()}</span>'
            f'<span class="hm-pill">Model guess: {item["prediction"].title()}</span>'
            f'<span class="hm-pill">Model P(human): {p_human:.0%}</span>'
            f'</div>', unsafe_allow_html=True)
        first = "Heads" if item["sequence"].startswith("H") else "Tails"
        st.caption(f"Why did the model guess that? It only knows how frequently "
                   f"people started with {first} in its separate training participants. "
                   f"It's a simple baseline, not a reliable lie detector. "
                   f"The sequence had {alternations(item['sequence'])} side switches.")
        a, b = st.columns([1, 1])
        a.button("↻  Restart game", on_click=start_game, args=(participants,),
                 use_container_width=True)
        b.button("View final results  →" if idx + 1 == len(rounds) else "Next round  →",
                 on_click=next_round, type="primary", use_container_width=True)
    with st.expander("Where do the sequences and predictions come from?"):
        st.markdown(f"**Human examples:** randomly sampled from the {len(participants)} "
                    "original, anonymized participant rows. Five are held out from "
                    "the predictor's training for each game.\n\n"
                    "**Computer examples:** six independent random H/T bits per sequence.\n\n"
                    f"**Model:** a smoothed first-flip frequency estimated from "
                    f"{game['train_n']} remaining participants (training Heads rate "
                    f"{game['train_head_rate']:.0%}). It doesn't memorize or classify by "
                    "matching full sequences.\n\n"
                    "**Important:** This is a small demonstration, not proof that "
                    "humans and random generators are generally distinguishable.")


def main() -> None:
    participants = load_real_data()
    initialize_state()
    render_header(participants)
    if st.session_state["section"] == "generate":
        render_generate(participants)
    else:
        render_game(participants)
    n_long = sum(p.get("original_sequence_length", 6) > 6 for p in participants)
    st.markdown(
        f'<div class="hm-foot">House of Minds · TAMU Datathon 2026 · '
        f'{len(participants)} original human participants · '
        f'using the first six recorded flips for comparable sequences '
        f'({n_long} original sequences were longer) · '
        'computer data is simulated fair-coin randomness · '
        'new player answers remain in the current browser session</div>',
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
