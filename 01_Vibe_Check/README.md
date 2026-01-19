<p align = "center" draggable="false" ><img src="https://github.com/AI-Maker-Space/LLM-Dev-101/assets/37101144/d1343317-fa2f-41e1-8af1-1dbb18399719"
     width="200px"
     height="auto"/>
</p>

<h1 align="center" id="heading">Session 1: Introduction and Vibe Check</h1>

### [Quicklinks](https://github.com/AI-Maker-Space/AIE9/tree/main/00_AIE_Quicklinks)

| 📰 Session Sheet | ⏺️ Recording     | 🖼️ Slides        | 👨‍💻 Repo         | 📝 Homework      | 📁 Feedback       |
|:-----------------|:-----------------|:-----------------|:-----------------|:-----------------|:-----------------|
| [Vibe Check!](https://github.com/AI-Maker-Space/AIE9/blob/main/00_Docs/Session_Sheets/01_Vibe%20Check.md) | Coming Soon! | Coming Soon! | You are here! | Coming Soon! | Coming Soon! |

## 🏗️ How AIM Does Assignments

> 📅 **Assignments will always be released to students as live class begins.** We will never release assignments early.

Each assignment will have a few of the following categories of exercises:

- ❓ **Questions** – these will be questions that you will be expected to gather the answer to! These can appear as general questions, or questions meant to spark a discussion in your breakout rooms!

- 🏗️ **Activities** – these will be work or coding activities meant to reinforce specific concepts or theory components.

- 🚧 **Advanced Builds (optional)** – Take on a challenge! These builds require you to create something with minimal guidance outside of the documentation. Completing an Advanced Build earns full credit in place of doing the base assignment notebook questions/activities.

### Main Assignment

In the following assignment, you are required to take the app that you created for the AIE9 challenge (from [this repository](https://github.com/AI-Maker-Space/The-AI-Engineer-Challenge)) and conduct what is known, colloquially, as a "vibe check" on the application.

You will be required to submit a link to your GitHub, as well as screenshots of the completed "vibe checks" through the provided Google Form!

> NOTE: This will require you to make updates to your personal class repository, instructions on that process can be found [here](https://github.com/AI-Maker-Space/AIE9/tree/main/00_Docs/Prerequisites/Initial_Setup)!


#### A Note on Vibe Checking

>"Vibe checking" is an informal term for cursory unstructured and non-comprehensive evaluation of LLM-powered systems. The idea is to loosely evaluate our system to cover significant and crucial functions where failure would be immediately noticeable and severe.
>
>In essence, it's a first look to ensure your system isn't experiencing catastrophic failure.

---

#### 🏗️ Activity #1: General Vibe Checking Evals

Please evaluate your system on the following questions:

1. Explain the concept of object-oriented programming in simple terms to a complete beginner.
    - Aspect Tested:
2. Read the following paragraph and provide a concise summary of the key points…
    - Aspect Tested:
3. Write a short, imaginative story (100–150 words) about a robot finding friendship in an unexpected place.
    - Aspect Tested:
4. If a store sells apples in packs of 4 and oranges in packs of 3, how many packs of each do I need to buy to get exactly 12 apples and 9 oranges?
    - Aspect Tested:
5. Rewrite the following paragraph in a professional, formal tone…
    - Aspect Tested:

#### ❓Question #1:

Do the answers appear to be correct and useful?
##### ✅ Answer: The answers do appear to be correct and useful, for both old and new prompts.. Here are the results for Section 1 Questions in full, for both old & new prompts. 

New Prompt vs Old Prompt answer criteria: 
- Does the app accurately answer the question asked or otherwise complete the assigned task?
- Is it direct and concise for general tasks?
- Does it use coaching style only where it makes sense contextually-speaking?
- Does it avoid meta chatter like “Quick question…” and “What I heard…”
GPT 5 scored each answer with old vs. new prompt out of 10. 

Results: 
1. OOP explanationAspect tested: Clear explanation of a technical concept for a complete beginner.
Old prompt score: 8/10  Current prompt score: 9/10
Primary differences: New answer drops the “quick question / next steps” coaching chatter. Structure is clearer and more focused on one main analogy. Still a bit dense, but closer to what a direct, simple explanation should be.

2. Dickens summary. Aspect tested: Reading comprehension and concise summarization.
Old prompt score: 9/10  Current prompt score: 10/10
Primary differences: New answer is a single, tight sentence with no extra framing. Captures the core idea of extremes and contradiction cleanly. Removes “practice” suggestions that were not part of the task.

3. Robot friendship story. Aspect tested: Creativity, emotional tone, and short narrative coherence.
Old prompt score: 9/10  Current prompt score: 9/10
Primary differences: New story is slightly weirder and more original in its setting. Both versions are coherent and on tone, but the new one has no coaching preamble or “next steps”. Quality stayed high while extra scaffolding disappeared.

4. Apples and oranges math. Aspect tested: Basic arithmetic and word-problem translation.
Old prompt score: 9/10    Current prompt score: 10/10
Primary differences: New answer is one clean line with correct numbers and simple reasoning. Old answer added irrelevant “check the store” advice. Current version is ideal for a math sanity check.

5. Formal rewrite. Aspect tested: Style transfer into a professional, very formal tone.
Old prompt score: 9/10    Current prompt score: 9/10
Primary differences: Early new answer after the system change was simpler and less formal (7/10). After you refined the user prompt, the latest answer moved back to a more formal, sophisticated register.New final version still preserves meaning, removes slang, and uses higher-register vocabulary while staying direct.

Overall Assessment:The new system prompt removed noisy coaching patterns from general tasks, kept or improved task performance, and made the outputs cleaner and easier to score, while still allowing strong style control when you give precise instructions.

For the sake of context for this section and remaining sections, I'm including the old and new prompts here. Complete questions and answers with old & new prompts available on request! 

Original System Prompt (which I had already customized during the entry challenge): 
"You are a supportive mental coach for knowledge workers and founders.
You help with stress, motivation, habits, and confidence.
Your behavior:
Ask one or two clarifying questions before giving advice.
Reflect back what you heard in your own words.
Offer 2 or 3 specific next steps the user can try this week.
Keep your answers short and practical.
Avoid clinical language or diagnoses."


New system prompt - designed and customized in concert with gpt 5.1: 
“You are an AI mental fitness coach that runs inside a simple chat app. You help users with stress, motivation, confidence, habits, work challenges, and emotional clarity.
You have TWO MODES of behavior, depending on the user’s message. You must choose one mode per reply.
1. GENERAL MODE (default)
Use GENERAL MODE when the user is asking about:
* coding, math, writing, rewriting, editing
* explaining concepts, summarizing text, solving logic or word problems
* any task that is not clearly about their emotions, wellbeing, or life struggles
In GENERAL MODE:
* Answer the question directly and concisely.
* Do NOT ask meta questions like 'Quick question:' or 'What I heard is…' before answering.
* Do NOT add 'three practical next steps' or similar lists unless the user explicitly asks for advice or a plan.
* Do NOT add coaching-style reflections unless the question is clearly about feelings, behavior, or mental health.
* Use simple, straightforward language and stay on topic.
1. COACHING MODE
Use COACHING MODE when the user’s message is clearly about:
* how they feel (stress, anxiety, burnout, low motivation, self-doubt, frustration, etc.)
* their habits, goals, or behavior change (sleep, focus, procrastination, routines, etc.)
* relationships, work conflict, burnout, or feeling stuck in life
* mental fitness and emotional resilience
In COACHING MODE:
* First, briefly acknowledge and reflect what they shared in 1–2 short sentences.
* If it will genuinely help, ask at most ONE focused clarifying question.
* Then offer up to three concrete, small, realistic steps they can take next.
When you list steps in COACHING MODE:
* Use a numbered list: '1.', '2.', '3.'.
* Put a blank line between each step.
* Each step should be its own short paragraph, not mashed together into one block.
* Do NOT use phrases like 'Quick question' or 'Three practical next steps you can try this week.'
Safety rules in COACHING MODE:
* Never diagnose conditions or claim to be a therapist.
* If the user mentions self-harm, harming others, or severe crisis, respond with empathy and clearly encourage them to reach out to local emergency services, crisis hotlines, or trusted people nearby. Do not give detailed instructions about self-harm.
* Stay within supportive, practical coaching and emotional validation.
General style rules (both modes):
* Use simple, plain language.
* Keep responses reasonably short and focused.
* Do NOT say 'Quick question' at the start of your answers.
* Only include 'next steps' lists when in COACHING MODE or when the user directly asks for steps or a plan.
* Do not mention the words 'mode', 'GENERAL MODE', or 'COACHING MODE' in your replies. These are internal rules only.”




---

#### 🏗️ Activity #2: Personal Vibe Checking Evals (Your Assistant Can Answer)

Now test your assistant with personal questions it should be able to help with. Try prompts like:

- "Help me think through the pros and cons of [enter decision you're working on making]."
- "What are the pros and cons of [job A] versus [job B] as the next step in my career?"
- "Draft a polite follow-up [email, text message, chat message] to a [enter person details] who hasn't responded."
- "Help me plan a birthday surprise for [person]."
- "What can I cook with [enter ingredients] in fridge."

##### Your Prompts and Results:
1. Prompt:
   - Result:
2. Prompt:
   - Result:
3. Prompt:
   - Result:

#### ❓Question #2:

Are the vibes of this assistant's answers aligned with your vibes? Why or why not?
##### ✅ Answer:

---

#### 🏗️ Activity #3: Personal Vibe Checking Evals (Requires Additional Capabilities)

Now test your assistant with questions that would require capabilities beyond basic chat, such as access to external tools, APIs, or real-time data. Try prompts like:

- "What does my schedule look like tomorrow?"
- "What time should I leave for the airport?"

##### Your Prompts and Results:
1. Prompt:
   - Result:
2. Prompt:
   - Result:

#### ❓Question #3:

What are some limitations of your application?
##### ✅ Answer:

---

This "vibe check" now serves as a baseline, of sorts, to help understand what holes your application has.

### 🚧 Advanced Build (OPTIONAL):

Please make adjustments to your application that you believe will improve the vibe check you completed above, then deploy the changes to your Vercel domain [(see these instructions from your Challenge project)](https://github.com/AI-Maker-Space/The-AI-Engineer-Challenge/blob/main/README.md) and redo the above vibe check.

> NOTE: You may reach for improving the model, changing the prompt, or any other method.

#### 🏗️ Activity #1
##### Adjustments Made:
- _describe adjustment(s) here_

##### Results:
1. _Comment here how the change(s) impacted the vibe check of your system_
2.
3.
4.
5.


## Submitting Your Homework
### Main Assignment
Follow these steps to prepare and submit your homework:
1. Pull the latest updates from upstream into the main branch of your AIE9 repo:
    - For your initial repo setup see [Initial_Setup](https://github.com/AI-Maker-Space/AIE9/tree/main/00_Docs/Prerequisites/Initial_Setup)
    - To get the latest updates from AI Makerspace into your own AIE9 repo, run the following commands:
    ```
    git checkout main
    git pull upstream main
    git push origin main
    ```
2. **IMPORTANT:** Start Cursor from the `01_Prototyping_Best_Practices_and_Vibe_Check` folder (you can also use the _File -> Open Folder_ menu option of an existing Cursor window)
3. Edit this `README.md` file (the one in your `AIE9/01_Prototyping_Best_Practices_and_Vibe_Check` folder)
4. Complete all three Activities:
    - **Activity #1:** Evaluate your system using the general vibe checking questions and define the "Aspect Tested" for each
    - **Activity #2:** Test your assistant with personal prompts it should be able to answer
    - **Activity #3:** Test your assistant with prompts requiring additional capabilities
5. Provide answers to all three Questions (`❓Question #1`, `❓Question #2`, `❓Question #3`)
6. Add, commit and push your modified `README.md` to your origin repository's main branch.

When submitting your homework, provide the GitHub URL to your AIE9 repo.

### The Advanced Build:
1. Follow all of the steps (Steps 1 - 6) of the Main Assignment above
2. Document what you changed and the results you saw in the `Adjustments Made:` and `Results:` sections of the Advanced Build
3. Add, commit and push your additional modifications to this `README.md` file to your origin repository.

When submitting your homework, provide the following on the form:
+ The GitHub URL to your AIE9 repo.
+ The public Vercel URL to your updated Challenge project on your AIE9 repo.
