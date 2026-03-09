

## # Session 16: LLM Servers


| 📰 Session Sheet                                  | ⏺️ Recording                           | 🖼️ Slides                                  | 👨‍💻 Repo    | 📝 Homework                                              | 📁 Feedback                        |
| ------------------------------------------------- | -------------------------------------- | ------------------------------------------- | ------------- | -------------------------------------------------------- | ---------------------------------- |
| [Session 16: LLM Servers](https://www.notion.so/) | [Recording!](https://us02web.zoom.us/) | [Session 16 Slides](https://www.canva.com/) | You are here! | [Session 16 Assignment: LLM Servers](https://forms.gle/) | [AIE9 Feedback](https://forms.gle) |


**⚠️!!! PLEASE BE SURE TO SHUTDOWN YOUR DEDICATED ENDPOINT ON FIREWORKS AI WHEN YOU'RE FINISHED YOUR ASSIGNMENT !!!⚠️**

# Build 🏗️

In today's assignment, we'll be creating Fireworks AI endpoints, and then building a RAG application.

- 🤝 Breakout Room #1
  - Set-up Open Source Endpoint (Instructions [here](./ENDPOINT_SETUP.md)) ((This process may take 15-20min.))
  - Test Endpoint and Embeddings with the `endpoint_slammer.ipynb` notebook.
- 🤝 Breakout Room #2
  - Use the Open Source Endpoints to build a RAG LangGraph application

# Ship 🚢

The completed notebook and your RAG app/notebook!

### Deliverables

- A short Loom of either:
  - the notebook and the RAG application you built for the Main Homework Assignment; or
  - the notebook you created for the Advanced Build

# Share 🚀

Make a social media post about your final application!

### Deliverables

- Make a post on any social media platform about what you built!

Here's a template to get you started:

```
🚀 Exciting News! 🚀

I am thrilled to announce that I have just built and shipped a RAG application powered by open-source endpoints! 🎉🤖

🔍 Three Key Takeaways:
1️⃣
2️⃣
3️⃣

Let's continue pushing the boundaries of what's possible in the world of AI and question-answering. Here's to many more innovations! 🚀
Shout out to @AIMakerspace !

#LangChain #QuestionAnswering #RetrievalAugmented #Innovation #AI #TechMilestone

Feel free to reach out if you're curious or would like to collaborate on similar projects! 🤝🔥
```

# Submitting You Homework [OPTIONAL]

## Main Homework Assignment

Follow these steps to prepare and submit your homework assignment:

1. Follow the instructions in `ENDPOINT_SETUP.md`
2. Replace both `model` values in `endpoint_slammer.ipynb` with the `gpt-oss` endpoint you created in Step 1
3. Run the code cells in `endpoint_slammer.ipynb`
4. Respond to the questions in the section below
5. Build a sample RAG
6. Record a Loom video reviewing what you have learned from this session

**⚠️!!! PLEASE BE SURE TO SHUTDOWN YOUR DEDICATED ENDPOINT ON FIREWORKS AI WHEN YOU HAVE FINISHED YOUR ASSIGNMENT !!!⚠️**

## Questions

### ❓ Question #1:

What is the difference between serverless and dedicated endpoints?

#### ✅ Answer:

Serverless
Serverless endpoints provide GPU from a remote host- hugely advantageous if local compute is minimal. Performance varies depending on usage by others because its a shared deployment. Cost is per token e.g., pay-per-use which is great, but use is tightly rate limited. Perfect for prototyping. 

Dedicated
Dedicated endpoints rely on local GPU, so less latency and higher throughput, and the limit on performance is dependent on local GPU. Cost is per GPU second which gets expensive very quickly, thus dedicated doesn't begin to make sense until use volume per GPU second becomes high. Very much best for high volume production. 

*(insert your answer here)*

### ❓ Question #2:

Why is it important to consider token throughput and latency when choosing an LLM for user-facing applications?

#### ✅ Answer:

It's important to take token throughput and latency into consideration when choosing an LLM for several reasons... Latency, which in this case is defined as the time to first token (TTFT), determines perceived responsiveness- low latency feels fast and the model responds quickly, which is what users want. High latancy feels like the model is broken when there's a long dalay before the model begins answering and percieved responsiveness seems slow- users aren't interested in waiting too long so high latency is not looked on very favorably. 

Token throughput is likewise important because it defines how many tokens per second the model generates after it starts, which determines how long it takes the full response to appear once the model begind to respond. This isn't as critical to perceived responesiveness as TTFT, as long as TTFT is fast and user can see that the model is "working".

In terms of cost, high throughput with high user volume means more users per gpu-second which optimizes cost relative to low volume and low throughput, which saves on gpu per second cost but increases token use as requests pile up. 

## Activity 1: RAGAS Evaluation with Cost Analysis

Use RAGAS to evaluate your open-source Fireworks AI powered RAG app against an OpenAI `gpt-4.1-mini` powered equivalent. Compare retrieval quality, answer faithfulness, and end-to-end accuracy across both providers.

Additionally, instrument both pipelines with **LangSmith** to capture token usage and cost per query. Use LangSmith's tracing and cost dashboards to compare the total cost of running each provider at scale. Include your evaluation results, cost breakdown, and analysis in your Loom video.

## Advanced Activity: Local Models

Swap out the Fireworks AI endpoints for **locally-running open-source models** using [Ollama](https://ollama.com/) or another local inference server of your choice. Run both your embedding model and your chat model locally, and rebuild the RAG pipeline on top of them.

- Compare quality and latency between the local setup and your Fireworks AI hosted endpoint.
- Reflect: what are the trade-offs of local models vs. managed endpoints in a production setting?

Include your findings and a demo in your Loom video.