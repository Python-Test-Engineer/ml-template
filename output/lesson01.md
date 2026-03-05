# Lesson 01: Multi-Agent Collaboration
## Data Science Detective Agency

> **How to run:**
> ```bash
> uv run python src/lesson01_app.py
> ```
> Then open your browser to **http://127.0.0.1:8000**

---

## What You Will Learn

By the end of this lesson, you will understand:

1. **Multi-agent orchestration** — how a Manager Agent breaks a big task into smaller pieces and hands them to specialist sub-agents.
2. **Message passing** — how agents communicate by sending structured messages through queues (just like real AI pipelines).
3. **Task decomposition** — why splitting work across specialized agents is faster and more reliable than one agent doing everything.
4. **Parallel vs sequential execution** — some agents must wait for others; some can run at the same time.

---

## The Mystery

The Manager Agent receives a dataset of **30 student grade records** and must answer:

- Are there any dirty/invalid rows?
- What are the average grades per subject?
- Which subject do students perform best in?
- What is the final investigative report?

Four specialist sub-agents are dispatched to solve the case.

---

## Agent Architecture

```
                        ┌─────────────────┐
                        │  Manager Agent  │  🕵️  Orchestrator
                        │                 │
                        └──┬──┬──┬──┬────┘
                           │  │  │  │
           ┌───────────────┘  │  │  └─────────────────────┐
           │                  │  │                         │
           ▼                  ▼  │                         ▼
  ┌────────────────┐  ┌──────────────┐          ┌────────────────┐
  │  DataCleaner   │  │ Statistician │          │    Reporter    │
  │  🧹 Sub-agent  │  │ 📊 Sub-agent │          │  📝 Sub-agent  │
  │                │  │              │          │                │
  │ Finds dirty /  │  │ Computes     │          │ Assembles the  │
  │ missing rows   │  │ mean, std,   │          │ final case     │
  │ and anomalies  │  │ min, max     │          │ report         │
  └────────┬───────┘  └──────┬───────┘          └───────┬────────┘
           │                  │                          │
           │    ┌─────────────┘           ┌─────────────┘
           │    │                         │
           │    ▼                         │
           │  ┌────────────────┐          │
           │  │   Visualizer   │          │
           │  │ 🎨 Sub-agent   │          │
           │  │                │          │
           │  │ Produces a     │          │
           │  │ Plotly bar     │          │
           │  │ chart          │          │
           │  └────────┬───────┘          │
           │           │                  │
           └───────────┴──────────────────┘
                       │  All results flow back
                       ▼  to Manager → Reporter
              ┌─────────────────┐
              │   Final Report  │
              │  + Plotly Chart │
              └─────────────────┘
```

### Execution Order

| Phase | Agents | Note |
|-------|--------|------|
| 1 | DataCleaner | Must run first — others need clean data |
| 2 | Statistician → Visualizer | Sequential here; Visualizer needs stats |
| 3 | Reporter | Runs last — needs all previous results |

---

## Dashboard Layout

```
┌─────────────────────────────────────────────────────────────────┐
│  🕵️ Data Science Detective Agency — Lesson 01                   │
├─────────────────────────────────────────────────────────────────┤
│  [▶ Start Investigation]  [↺ Run Again]                         │
├──────────────┬──────────────────────────┬───────────────────────┤
│ 📋 Task Queue│  💬 Live Message Log     │  🤖 Agent Status      │
│              │                          │                       │
│ DataCleaner  │  🕵️ Manager → ALL       │  🧹 DataCleaner       │
│ [⏳ Waiting] │  "Dataset loaded..."     │  [⏳ Waiting]         │
│              │                          │                       │
│ Statistician │  🧹 DataCleaner → ALL   │  📊 Statistician      │
│ [⚡ Working] │  "Starting scan..."      │  [✅ Done]            │
│              │                          │                       │
│ Visualizer   │  📊 Statistician → Mgr  │  🎨 Visualizer        │
│ [✅ Done]    │  "Mean grade: 78.4..."   │  [⚡ Working]         │
│              │                          │                       │
│ Reporter     │  ...                     │  📝 Reporter          │
│ [⏳ Waiting] │                          │  [⏳ Waiting]         │
├──────────────┴──────────────────────────┴───────────────────────┤
│  📊 Investigation Results (appears when all agents are done)    │
│  [Bar Chart]                [Final Report Text]                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Key Concepts Demonstrated

### What happens when you click "Start Investigation":

1. The **Manager Agent** loads the student grades dataset
2. It sends a **task message** to the DataCleaner sub-agent
3. DataCleaner scans for missing/invalid data, sends a **result message** back
4. Manager forwards clean data to Statistician and Visualizer
5. Each agent sends **update messages** while working, **result messages** when done
6. Reporter collects all findings and writes the final report
7. The dashboard **polls for new messages every 600ms** and updates live

### Message Types

| Type | Color | Meaning |
|------|-------|---------|
| `task` | 📋 | Manager assigning work to a sub-agent |
| `update` | 💬 | Agent reporting progress mid-task |
| `result` | 📤 | Agent sending finished output back |
| `complete` | 🏁 | Agent announcing it is done |

---

## Glossary

**Manager Agent**
: The orchestrator that receives the overall goal, breaks it into sub-tasks, dispatches those tasks to sub-agents, and assembles the final result.

**Sub-Agent**
: A specialized agent that handles one specific part of the task (e.g., cleaning data, computing statistics). Sub-agents receive tasks from the manager and send results back.

**Message Queue**
: A channel through which agents send and receive structured messages. Queues decouple agents — a sender doesn't need to wait for the receiver to be ready.

**Orchestration**
: The coordination pattern where a central agent (Manager) controls the flow of work, deciding which agents run when and how their outputs are combined.

**Task Decomposition**
: Breaking a complex problem into smaller, well-defined sub-problems that specialized agents can solve independently.

**Asynchronous Execution**
: Agents can run concurrently (at the same time) when they don't depend on each other's output, making the pipeline faster.

---

## Discussion Questions

1. Why does the DataCleaner have to finish before Statistician can start?
2. What would happen if the Visualizer sent incorrect data to the Reporter?
3. How would you add a 5th agent (e.g., a "Predictor") to this pipeline?
4. In a real AI system, how might agents use actual LLMs instead of simulated behavior?
5. What are the risks of a Manager Agent that doesn't validate sub-agent results?

---

*Generated by the Data Intelligence Researcher project — Lesson 01*
