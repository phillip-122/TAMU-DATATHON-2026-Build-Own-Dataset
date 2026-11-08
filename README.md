# 🧠 House of Minds
### Can humans actually be random?

**TAMU Datathon 2026 · Build Your Own Dataset Challenge**

House of Minds turns a dataset of **36 real participants** into an interactive experiment. Imagine six coin flips, choose two numbers, and discover how your choices compare with other people's. Then try to tell human choices apart from computer-generated randomness.

> **28 of 36 participants started with Heads.** That's about **78%**, compared with a fair coin's **50%** starting probability. A simple choice reveals an interesting pattern in our sample.

## Our goal

We wanted to explore whether people can deliberately produce randomness, and whether their imagined coin flips reveal enough patterns to distinguish them from independent fair-coin flips. The app lets visitors experience that question themselves, then compare their intuition with collected data and a transparent model.

## Two ways to play

| Experience | What you do | How the dataset powers it |
| --- | --- | --- |
| **Generate Randomness** | Imagine six coin flips and pick numbers from 1–10 and 1–100. | Your personal reveal compares your first flip, side switches, and number choices with the collected responses. |
| **Human or Computer?** | Guess who produced a sequence over ten rounds. | Five sequences come from real participants; five are independently generated fair-coin sequences. Compete against a simple baseline model, with immediate reveals and a scoreboard. |

## The dataset

Explore the responses in **[participants.csv](participants.csv)**.

- **36 unique participants:** imagined Heads/Tails sequences and number selections, with additional timing measurements retained in the CSV.
- **Comparable sequences:** 19 people recorded six flips; 17 recorded longer sequences. The app uses each person's first six recorded flips and preserves the full responses.
- **Separate sources:** human rounds use collected responses. Computer rounds are generated independently and are never added to the human dataset.
- **Session-only answers:** visitors can explore their choices without changing the source CSV.

See the [data dictionary](DATA_DICTIONARY.md) for field definitions.

### Data Collection Methodology

We collected original responses from **36 participants** during TAMU Datathon 2026.

- **Collection dates:** November 7–8, 2026
- **Collection location:** Memorial Student Center (MSC), Room 2300, Texas A&M University
- **Participants:** 36 volunteers attending TAMU Datathon
- **Collection method:** I approached participants individually and asked whether I could ask them a few questions for my project. Each participant agreed before answering.
- **Consent and privacy:** Participation was voluntary, and each person agreed to answer the questions. The published dataset uses anonymous participant numbers rather than names.

Participants were asked to imagine a random sequence of Heads/Tails coin flips, select random numbers from 1–10 and 1–100, and estimate ten seconds without using a clock.

As data collection progressed, I expanded the experiment to include longer coin-flip sequences and additional responses. Because of this, not every participant completed the exact same number of trials.

For the application, I standardized the coin-flip data by using the first six recorded flips from each participant. This allowed me to compare all 36 participants against computer-generated sequences of the same length without fabricating additional observations.

The original responses, including longer sequences and timing measurements, are preserved in `participants.csv`. The application uses the coin-flip sequences and random-number selections, while the timing data remains available for future analysis.

### Why do some fields look unusual?

**The collection grew as the project developed.** We started with a smaller sample and then expanded the questions to collect more data. The CSV preserves those responses rather than making every record look identical.

- **Six flips versus longer sequences:** the collected sequences vary from 6 to 19 flips. We keep each full response, but use only the first six flips in the app so every participant and computer round is compared at the same length.
- **Counting to ten:** we also recorded how many seconds participants took to count to ten, with a second trial in some records. These measurements remain available for future analysis, but the final app focuses on coin sequences and number choices. Its computer rounds have no matching counting task, so the timings are not inputs to the Human or Computer? model.
- **Extra numbers and blank cells:** some participants supplied a second 1–10 choice or an additional number. The app consistently uses the first 1–10 choice and the 1–100 choice. Extra responses and raw entries stay in the CSV; a blank cell means no value is recorded for that field.

This evolving collection is a limitation: participants did not all complete an identical set of questions. Using a shared six-flip prefix makes the game comparable in length, but does not remove possible differences between collection stages.

## A simple, transparent model

The baseline uses **only the first-flip Heads frequency**. Each game holds out five human participants for play and estimates that frequency from the other 31, with smoothing. It compares this pattern with a fair coin's 50/50 probability to predict Human or Computer.

This makes the prediction easy to explain. It also keeps the displayed human examples out of training. With just 36 participants and six flips per example, results are exploratory: either source can produce the same sequence, and a single game's score does not establish general detection accuracy.

## What we found

**We found a pattern in the group, but did not establish a reliable way to determine whether an individual sequence was human-generated or came from a fair random generator.** The 28-of-36 Heads result is an observation about our participants, not a dependable test of who made any particular sequence.

Human and computer sequences can overlap, and six flips provide very little evidence. Our conclusion is limited to this small experiment; it does not prove that human-generated and computer-generated randomness are always indistinguishable. Here, “random” computer sequences mean independently simulated fair-coin flips, not a physical source of true randomness.

## Why it could be useful

- **Teaching probability:** visitors can see how a group pattern differs from a prediction about one person.
- **Exploring intuition:** personal comparisons make bias and uncertainty tangible without labeling someone's answer as right or wrong.
- **Planning better research:** the dataset provides a starting point for a larger study with consistent instructions, longer sequences, and a separate analysis of the counting measurements.

## Run the demo

Requires **Python 3.10+** and an internet connection for the initial dependency installation.

**Windows:** double-click `run_windows.bat`. Keep the terminal open while playing.

**macOS / Linux:** open a terminal in this folder and run:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Open **[localhost:8501](http://localhost:8501)**. No account or cloud service is required.

---

Built with **Python + Streamlit** to make human bias and probability something you can experience, not just read about.
