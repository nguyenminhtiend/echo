# AI Tools in Daily Work — Complete Interview Knowledge Base (2026)

> **Scope**: Developer · Tech Lead · Architect · QA · Scrum Master  
> **Standard**: 2026 Industry Practices  
> **Format**: Question → Answer (interview-ready)

---

## TABLE OF CONTENTS

1. Foundations & Landscape
2. AI-Assisted Development (Copilot, Cursor, Claude Code)
3. Claude Code Deep Dive (CLI, Commands, Configuration)
4. MCP — Model Context Protocol
5. Hooks System
6. Skills, Slash Commands & CLAUDE.md
7. Sub-Agents & Agent Teams
8. Prompt Engineering & Context Management
9. Token Usage & Cost Optimization
10. Memory, Compaction & Long Conversations
11. Security & Data Leak Prevention
12. Automation & CI/CD Integration
13. Workflow Design & Agentic Patterns
14. Role-Specific: Developer
15. Role-Specific: Tech Lead
16. Role-Specific: Architect
17. Role-Specific: QA Engineer
18. Role-Specific: Scrum Master / PM
19. RAG, Embeddings & Knowledge Systems
20. Governance, Compliance & Responsible AI
21. Advanced & Emerging Topics (2026 Standard)
22. Scenario-Based Questions
23. 2026 Bleeding-Edge Standards
24. Permission System & Trust Levels
25. Extended Thinking & Reasoning
26. Claude Code Platforms & IDE Integration
27. Git Worktrees & Isolation Patterns
28. Structured Output & JSON Schema
29. OAuth, MCP Authentication & API Security
30. Claude Agent SDK & Custom Agents
31. Batch API & Async Processing
32. Multi-Modal AI in Development
33. AI Code Attribution & Legal Considerations
34. Rate Limiting, Fallbacks & Resilience
35. AI in Incident Response & On-Call
36. Guardrails, Safety & Content Filtering
37. Model Selection Strategy Across Providers
38. Additional Scenario-Based Questions
39. Claude Code Memory & Persistence System
40. Remote Agents, Triggers & Scheduled Execution
41. AI Evaluation Frameworks (Evals) & Quality Measurement
42. Developer Experience Metrics & AI ROI
43. AI for Infrastructure as Code (IaC)
44. Docker, Containers & Sandboxed Agent Execution
45. Prompt Libraries, Registries & Team Knowledge
46. AI Code Debt & Technical Debt Management
47. Advanced Context Window Strategies
48. Claude API Deep Dive (Tool Use, Streaming, Citations)
49. AI-Assisted Database Operations & Migrations
50. Edge AI & On-Device Coding Assistants

---

## 1. FOUNDATIONS & LANDSCAPE

### Q1.1: What are the main categories of AI tools used in software development in 2026?

**A:** The landscape divides into several categories. Code-generation assistants like GitHub Copilot, Cursor, and Claude Code provide inline completions and agentic coding. Chat-based LLMs such as Claude, ChatGPT, and Gemini handle reasoning, analysis, and content generation. Specialized tools include AI-powered testing (Codium/Qodo), code review bots, and documentation generators. Infrastructure tools include MCP servers that connect AI to external services, and orchestration platforms that coordinate multi-agent workflows. The key shift in 2026 is from "AI as autocomplete" to "AI as autonomous agent" — tools now read codebases, run commands, manage git, and connect to external services independently.

### Q1.2: What is the difference between AI-assisted coding and agentic coding?

**A:** AI-assisted coding is reactive — the developer drives and the AI suggests (e.g., tab-completion in Copilot). Agentic coding is proactive — the developer describes a goal and the AI autonomously plans, executes, tests, and iterates. For example, Claude Code can receive "fix all failing tests," then read test output, identify root causes, edit files, re-run tests, and loop until everything passes. The agent decides which tools to use, in what order, without step-by-step human guidance. In 2026, roughly 4% of public GitHub commits (~135,000/day) are authored by Claude Code alone, showing how mainstream agentic coding has become.

### Q1.3: How do you compare Claude Code, GitHub Copilot, and Cursor?

**A:** Copilot excels at inline suggestions within VS Code/JetBrains — it's the best "tab-complete" experience and integrates tightly with the IDE. Cursor is a fork of VS Code with deep AI integration including multi-file editing, a composer mode, and visual diff review — it's ideal for frontend and UI-heavy work. Claude Code is a terminal-native agentic CLI that reads your entire codebase, executes bash commands, manages git, and connects to external services via MCP. Claude Code is strongest for backend work, refactoring, CI/CD automation, and complex multi-step tasks. They are complementary: many teams use Cursor for visual editing and Claude Code for automation, orchestration, and headless tasks.

### Q1.4: What does "AI-native development workflow" mean in 2026?

**A:** It means AI is not bolted on as an afterthought but is central to the SDLC. This includes AI-generated PR descriptions and commit messages, automated code review via AI agents, test generation as part of the development loop, CLAUDE.md files as living architecture documentation that both humans and AI read, hooks that enforce quality standards automatically, MCP integrations that let AI access Jira, Slack, databases, and deployment pipelines, and sub-agents that parallelize work like exploration, testing, and documentation. The workflow shifts from "developer writes code" to "developer directs AI agents and reviews output."

---

## 2. AI-ASSISTED DEVELOPMENT

### Q2.1: How do you effectively use AI code assistants without becoming dependent?

**A:** The key is treating AI as a junior pair programmer, not an oracle. Always review generated code for correctness, security, and style. Understand the code before accepting it — if you cannot explain it, do not merge it. Use AI for boilerplate, repetitive patterns, and exploration, but write critical business logic and security code with full comprehension. Maintain your fundamentals: if you stop being able to code without AI, you cannot effectively review AI output. A good rule: use AI to go faster on things you already know how to do, and as a learning accelerator for things you are exploring.

### Q2.2: What are the risks of AI-generated code?

**A:** The primary risks include hallucinated APIs (the model invents functions or parameters that do not exist), subtle logic errors that look correct on casual inspection, security vulnerabilities such as missing input validation or SQL injection, license contamination if the model reproduces copyrighted code, outdated patterns from training data that predate current best practices, and over-engineering or under-engineering relative to the actual requirements. Mitigation requires code review, automated testing, linting, SAST/DAST scanning, and a culture where AI-generated code is held to the same (or higher) standard as human-written code.

### Q2.3: How should code review change when AI generates most of the code?

**A:** Focus shifts from syntax and style (which AI handles well) to intent verification, architectural alignment, edge cases, and security. Reviewers should ask: does this code actually solve the stated problem? Does it handle error cases? Is it consistent with the project's architecture and conventions? Are there hidden performance implications? Does it introduce unnecessary dependencies? The reviewer's role becomes more like a senior architect verifying design decisions rather than a line-by-line proofreader.

---

## 3. CLAUDE CODE DEEP DIVE

### Q3.1: What is Claude Code and how does it work architecturally?

**A:** Claude Code is Anthropic's agentic CLI tool. It operates as a loop: receive a task, select a tool (file read, bash, web search, MCP call), execute it, observe the result, decide the next action, and repeat until done. Every capability — including file operations, bash execution, and even computer use — runs through a tool layer. Each tool is discrete, permission-gated, and sandboxed. Before any consequential action (writing a file, running a command, making a network request), the system surfaces a trust prompt for user confirmation (unless auto-approved). It connects to Claude models via the Anthropic API and maintains a context window of conversation history.

### Q3.2: What are the key CLI flags and options every user should know?

**A:** Essential flags include: `-p "prompt"` for non-interactive (print/pipe) mode used in scripts and CI; `--model` to select which model to use (opus, sonnet, haiku); `--max-budget-usd` to set a hard spending limit; `--max-turns` to limit agentic loops; `--allowedTools` and `--disallowedTools` to control which tools the agent can use; `--output-format json` for machine-readable output with optional `--json-schema` for structured validation; `--resume` to continue a previous session; `--debug` for troubleshooting API calls and hooks; `-n / --name` to label sessions; `--fallback-model` to specify an alternative when the primary model is rate-limited; and `--worktree` to run in an isolated git worktree. Fast mode (`/fast` in interactive or toggled via settings) uses the same model with faster output optimized for speed — it does NOT switch to a different model.

### Q3.3: What are slash commands in Claude Code?

**A:** Slash commands are built-in shortcuts invoked with `/` during an interactive session. Key commands include: `/compact` to compress conversation history and reclaim context space; `/clear` to reset the conversation entirely; `/effort` to set the model's reasoning effort level; `/agents` to create or invoke sub-agents interactively; `/resume` to continue a previous session; `/init` to generate a CLAUDE.md for the current project; and custom commands defined in `.claude/commands/` as markdown files. Custom commands allow teams to create reusable prompts — for example, `/review` might trigger a comprehensive code review workflow.

### Q3.4: Explain the configuration hierarchy in Claude Code.

**A:** Configuration follows a strict precedence from highest to lowest priority: enterprise policy (managed by admins, cannot be overridden), user-level settings (`~/.claude/settings.json` and `~/.claude/.mcp.json`), project-level settings (`.claude/settings.json` and `.mcp.json` at repo root), and plugins. For conflicting keys, higher-priority settings win. This hierarchy ensures enterprise security policies always take effect, while individual developers can customize their experience within those bounds. CLAUDE.md files follow a similar layering: enterprise > user (`~/.claude/CLAUDE.md`) > project (root `CLAUDE.md`) > subdirectory-specific files.

### Q3.5: What is the difference between interactive mode and headless/print mode?

**A:** Interactive mode is the default terminal experience where you converse with Claude, approve tool uses, and iterate. Print mode (`-p`) runs a prompt non-interactively and outputs the result — designed for scripting, CI/CD pipelines, and automation. In print mode, you typically pre-approve tools via `--allowedTools` since there is no human to click "allow." Print mode supports `--output-format json` for piping structured output into other tools. Headless mode is an extension where sessions can be paused (via the new "defer" permission in hooks) and resumed later, enabling complex approval workflows.

---

## 4. MCP — MODEL CONTEXT PROTOCOL

### Q4.1: What is MCP and why does it matter?

**A:** MCP (Model Context Protocol) is an open standard that lets AI models connect to external tools and data sources through a plugin-like architecture. Instead of hardcoding integrations, you configure MCP servers and the AI gains new capabilities — querying databases, calling APIs, posting to Slack, reading from Notion, managing GitHub issues. MCP standardizes how AI agents discover, authenticate with, and invoke external tools. It matters because it transforms AI from "smart but isolated" to "smart and connected." In 2026, there are 3,000+ MCP server integrations available.

### Q4.2: How do you configure an MCP server in Claude Code?

**A:** You add server configurations to `.mcp.json` at the project root (project-scoped) or `~/.claude/.mcp.json` (user-scoped/global). Each entry specifies the server type, command or URL, and optional environment variables. For example, a GitHub MCP server might use the `gh` CLI, a database MCP server might connect via a stdio process, and a remote service uses an SSE URL. After adding the config, restart Claude Code and the new tools appear automatically. You can verify with `--debug` to see tool discovery.

### Q4.3: When should you use MCP servers vs. direct CLI tools?

**A:** Use direct CLI tools (like `gh`, `aws`, `gcloud`) when a single command works — they are simpler, faster, and consume no extra context. Use MCP servers when you need the AI to have ongoing, structured access to an external service across multiple interactions, when the integration requires authentication flows, when you want the AI to discover available operations dynamically, or when the interaction is bidirectional (the service can also push data back). A practical rule: if you find yourself repeatedly telling the AI "run `gh issue list`," an MCP server for GitHub is worth the setup.

### Q4.4: What is MCP Tool Search and why is it important for token usage?

**A:** MCP Tool Search (lazy loading) allows Claude Code to defer loading tool definitions until they are actually needed. Without it, every MCP server's tool schemas are loaded into context at the start of every conversation, consuming tokens even if those tools are never used. With Tool Search enabled (`ENABLE_TOOL_SEARCH=auto:5`), tool definitions are loaded on demand, reducing context usage by up to 95%. This is critical when you run many MCP servers simultaneously — without lazy loading, you could exhaust your context window before doing any real work.

### Q4.5: What is MCP Elicitation?

**A:** Elicitation is a 2026 feature that allows MCP servers to request structured input from the user mid-task. Instead of the AI guessing or asking a free-form question, the MCP server surfaces an interactive dialog (form fields or browser URL) for the user to provide specific information. This enables more reliable multi-step workflows — for example, an MCP server deploying to production might elicit which environment, region, and version to deploy before proceeding. Hooks (`Elicitation` and `ElicitationResult`) can intercept and override these requests.

---

## 5. HOOKS SYSTEM

### Q5.1: What are hooks in Claude Code and why are they critical?

**A:** Hooks are shell commands that fire automatically at specific points in Claude Code's lifecycle. They guarantee execution — unlike prompts (which the model might ignore), hooks always run. This makes them essential for enforcement: linting, formatting, security checks, commit validation, and compliance rules. If something must happen every time, it belongs in a hook, not in a CLAUDE.md instruction.

### Q5.2: What hook events are available?

**A:** The main hook events are: `PreToolUse` (fires before a tool executes — can validate, modify, or block the action), `PostToolUse` (fires after a tool completes — can process results, run formatters, trigger notifications), `Notification` (fires when Claude produces a notification), `Stop` (fires when Claude finishes its response — useful for post-completion checks), `SubagentStop` (fires when a sub-agent completes), `PostCompact` (fires after conversation compaction), and the newer `Elicitation` and `ElicitationResult` hooks for MCP elicitation. PreToolUse hooks can also return a "defer" decision for headless sessions, pausing execution until a human resumes.

### Q5.3: Give a practical example of a security hook.

**A:** A `PreToolUse` hook on the `Bash` tool can block dangerous commands:

```bash
#!/bin/bash
# .claude/hooks/block-dangerous.sh
INPUT="$1"
if echo "$INPUT" | grep -qE 'rm -rf|sudo|chmod 777|curl.*\|.*sh'; then
  echo "BLOCKED: Dangerous command detected"
  exit 1
fi
```

This prevents the agent from executing destructive commands regardless of how the prompt is phrased. Another common pattern is a pre-commit hook that blocks commits containing `.env`, `.pem`, or credential files. The key insight is that hooks are deterministic — they do not depend on the model's judgment.

### Q5.4: How do hooks differ from CLAUDE.md instructions?

**A:** CLAUDE.md instructions are advisory — the model reads them and tries to follow them, but there is no guarantee, especially in long conversations where instructions may be compacted away. Hooks are enforcement — they are shell scripts that execute unconditionally at the configured event. If a CLAUDE.md says "always run prettier after editing," the model might forget. If a `PostToolUse` hook runs prettier after every file write, it happens 100% of the time. Best practice: use CLAUDE.md for guidelines, preferences, and context; use hooks for anything that must be enforced.

### Q5.5: What is the "defer" permission in hooks?

**A:** Added in early 2026, the "defer" decision allows a `PreToolUse` hook in a headless session to pause execution at a specific tool call. The session suspends and can later be resumed with `claude -p --resume`, at which point the hook re-evaluates. This enables human-in-the-loop approval workflows in CI/CD: for example, an agent running in a pipeline might defer when it wants to deploy to production, waiting for a human to resume and approve.

---

## 6. SKILLS, SLASH COMMANDS & CLAUDE.md

### Q6.1: What is CLAUDE.md and how should you structure it?

**A:** CLAUDE.md is a markdown file that Claude reads at the start of every session to understand your project. It serves as living documentation for both humans and AI. A good CLAUDE.md includes: project overview and architecture description, tech stack and key dependencies, coding conventions and style rules, file structure explanation, common workflows and commands, testing strategy, deployment process, and any domain-specific terminology. Keep it concise — every token in CLAUDE.md consumes context. Update it as the project evolves. Use `/init` to generate an initial version automatically.

### Q6.2: What are Skills in Claude Code?

**A:** Skills are markdown files (SKILL.md) placed in `.claude/skills/` that encode domain expertise for specific tasks. When Claude encounters a relevant task, it reads the skill file and follows its instructions. Skills differ from CLAUDE.md in that they are task-specific rather than project-wide. For example, you might have skills for "database migration," "API endpoint creation," or "React component with tests." Skills can include code templates, step-by-step procedures, and quality checklists. They let you capture team expertise in a form the AI can reliably apply.

### Q6.3: How do custom slash commands work?

**A:** Custom commands are markdown files in `.claude/commands/`. The filename becomes the command name (e.g., `.claude/commands/review.md` creates `/review`). The file contains a prompt template that can reference `$ARGUMENTS` for user input. When invoked, Claude reads the file and executes the described workflow. This lets teams create standardized, reusable workflows — like `/deploy staging`, `/review security`, `/generate-migration`, or `/update-docs`. Commands can orchestrate multi-step processes, invoke sub-agents, and reference skills.

### Q6.4: What is the AGENTS.md file?

**A:** AGENTS.md defines sub-agent configurations that Claude can delegate to. Each agent entry specifies a name, description, model preference, allowed tools, and behavioral instructions via frontmatter. You can invoke agents through natural language or the `/agents` menu. AGENTS.md allows you to create specialized roles — a "code-reviewer" agent, a "test-writer" agent, a "documentation" agent — each with its own model, permissions, and instructions. Sub-agents cannot spawn other sub-agents (no recursion), and they report results back to the parent session.

---

## 7. SUB-AGENTS & AGENT TEAMS

### Q7.1: What are sub-agents and when should you use them?

**A:** Sub-agents are independent Claude sessions spawned by the main session to handle focused tasks. They get their own clean context window, do their work, and return a summary to the parent. Use sub-agents when: a task is exploratory and might bloat the main context (e.g., "search the codebase for all uses of this pattern"), when you want parallel execution, when a task needs a different model tier (e.g., using Haiku for simple lookups), or when the work is isolated and the full results are not needed in the main conversation — only the conclusions.

### Q7.2: What is the difference between sub-agents and Agent Teams?

**A:** Sub-agents are hierarchical: they report to a parent and cannot talk to each other. Agent Teams (launched February 2026 with Opus 4.6) are collaborative: multiple independent Claude sessions that can coordinate, message each other, and divide work in parallel. Think of sub-agents as a manager delegating to isolated workers, while Agent Teams are a squad of peers collaborating on a shared objective. Agent Teams are suited for complex tasks like "refactor the authentication module" where one agent handles the backend, another handles tests, and they coordinate on interface contracts.

### Q7.3: How do you optimize cost when using sub-agents?

**A:** Route sub-agents to the cheapest model that can handle the task. Use Haiku for simple exploration, file searching, and data extraction. Use Sonnet for general coding and moderate reasoning. Reserve Opus for complex architectural decisions and nuanced judgment. Set `--max-turns` and `--max-budget-usd` on sub-agents to prevent runaway costs. Also consider: do you actually need a sub-agent? If the task is simple, a direct tool call is cheaper than spawning a new session with its own system prompt overhead.

---

## 8. PROMPT ENGINEERING & CONTEXT MANAGEMENT

### Q8.1: What are the key principles of effective prompting for coding tasks?

**A:** Be specific about the desired output format, language, and framework. Provide examples of the expected result when possible. Include constraints explicitly (e.g., "do not use any external libraries," "must be compatible with Node 18+"). Reference existing code patterns in the project ("follow the same pattern as `src/auth/handler.ts`"). Break complex tasks into steps — ask the AI to plan before implementing. Use positive instructions ("use prepared statements") rather than only negative ones ("don't use string concatenation for SQL"). When working with Claude Code, tell it to read relevant files first before making changes.

### Q8.2: What is "plan mode" and when should you use it?

**A:** Plan mode (sometimes called "think first") is when you ask the AI to create a plan before executing. For example: "Read the codebase, understand the authentication flow, then propose a plan for adding OAuth2 support — but don't make any changes yet." This prevents the AI from charging ahead with a wrong approach. Use plan mode for any non-trivial task: refactoring, new features, architecture changes. Review the plan, provide feedback, then authorize execution. This saves tokens and time by catching misunderstandings early.

### Q8.3: How does the context window work and why does it matter?

**A:** The context window is the total amount of text (measured in tokens) the AI can "see" at once — including the system prompt, CLAUDE.md, conversation history, file contents, and tool outputs. Standard context is 200K tokens; extended context (Opus 4.6) can go up to 1M tokens. When context fills up, earlier information gets compacted or lost, degrading quality. Everything you do costs context: reading a file, running a command, reviewing output. Managing context is one of the most important skills for effective AI tool usage. Strategies include: using `/compact` proactively, keeping sub-agents for exploratory work, using `--max-turns` to limit verbose outputs, and being intentional about which files you ask the AI to read.

### Q8.4: What is conversation compaction and how does it work?

**A:** When the context window approaches its limit, Claude Code automatically compacts the conversation — summarizing earlier exchanges into a condensed form to make room for new content. This preserves the most recent and relevant information but may lose nuances from earlier in the conversation. You can trigger compaction manually with `/compact`. The `PostCompact` hook fires after compaction, letting you run custom logic (like re-injecting critical context). To minimize compaction-related quality loss: keep sessions focused on single tasks, start new sessions for new topics, and put critical information in CLAUDE.md (which is re-read, not compacted).

### Q8.5: What is the /effort command?

**A:** The `/effort` command sets the model's reasoning effort level — how much "thinking" the model does before responding. Lower effort is faster and cheaper for simple tasks; higher effort is better for complex reasoning. This maps to the model's extended thinking feature. Use lower effort for straightforward tasks like formatting, simple edits, and file searches. Use higher effort for architectural decisions, complex debugging, and multi-step reasoning.

---

## 9. TOKEN USAGE & COST OPTIMIZATION

### Q9.1: How do you estimate and control AI costs in a development team?

**A:** Track costs at three levels: per-session (use `--max-budget-usd`), per-developer (monthly quotas via API key management), and per-project (aggregate reporting). Strategies to reduce costs include: model tiering (Haiku for simple tasks, Sonnet for general work, Opus for complex reasoning), limiting context loading (don't read unnecessary files), using `/compact` to avoid redundant context, using sub-agents with cheaper models for exploration, setting `--max-turns` to prevent infinite loops, caching (prompt caching reduces costs for repeated system prompts), and using print mode with constrained outputs for CI tasks.

### Q9.2: What is prompt caching and how does it reduce costs?

**A:** Prompt caching allows the API to reuse the processed representation of the system prompt and early conversation turns across requests. If the beginning of your prompt is identical to a recent request, the cached tokens are processed at a significantly reduced cost (often ~90% cheaper). This is particularly effective for: system prompts that include CLAUDE.md content, repeated CI/CD tasks using the same base prompt, and batch processing where many items share the same instructions. Claude Code leverages caching automatically — another reason to keep your CLAUDE.md stable and your system prompt consistent.

### Q9.3: What is model tiering and how do you implement it?

**A:** Model tiering means routing different tasks to different model sizes based on complexity. A practical setup: use Haiku (~$0.25/M input tokens) for linting checks, simple file searches, and data extraction; use Sonnet (~$3/M input tokens) for general coding, test writing, and documentation; use Opus (~$15/M input tokens) for complex architectural reasoning, subtle bug diagnosis, and security audits. In Claude Code, set the model per sub-agent or per-invocation with `--model`. In CI/CD, use Haiku for fast checks and Sonnet for deeper analysis. A team using smart tiering can cut AI costs by 60-80% vs. using Opus for everything.

### Q9.4: What is the Token-Budget Tradeoff for long tasks?

**A:** Every interaction with an AI model has a cost proportional to input + output tokens. For long tasks, the main cost driver is accumulated context — each turn resends the entire conversation history. Strategies: start fresh sessions for new tasks instead of continuing long ones, use sub-agents to offload exploration (only the summary returns to the main context), aggressively compact when context grows large, pipe file contents through grep/awk before sending (send only relevant lines, not entire files), and use `--output-format json` in scripts to get concise, structured responses instead of verbose explanations.

---

## 10. MEMORY, COMPACTION & LONG CONVERSATIONS

### Q10.1: How does AI memory work across sessions?

**A:** By default, each AI session is stateless — the model has no memory of previous conversations. Memory systems layer persistence on top through different mechanisms: CLAUDE.md acts as persistent project memory (always re-read); claude.ai's memory feature extracts key facts from conversations and stores them for future reference; Memory MCP servers provide knowledge-graph-based persistent memory; session resumption (`--resume`) reloads a specific conversation's history; and external tools (databases, files) can store and retrieve state across sessions.

### Q10.2: What problems arise in long conversations and how do you mitigate them?

**A:** The main problems are: context overflow (conversation exceeds the window, triggering compaction with potential information loss), instruction drift (the model gradually "forgets" early instructions as they get further away in context), cost escalation (each turn resends the entire history, making later turns increasingly expensive), and quality degradation (the model's attention to any single piece of information decreases as context grows). Mitigation: keep sessions focused and short, start new sessions for new tasks, use sub-agents for side explorations, compact proactively, put critical rules in CLAUDE.md (re-read, not compacted), and use hooks for enforcement (immune to instruction drift).

### Q10.3: What is the PostCompact hook and why was it added?

**A:** The PostCompact hook fires after conversation compaction completes. It was added because compaction can remove important context that was established early in the conversation. The hook lets you re-inject critical information, update state tracking, or trigger notifications when compaction occurs. For example, you might use it to re-read a critical configuration file or remind the agent of key constraints that should survive compaction.

---

## 11. SECURITY & DATA LEAK PREVENTION

### Q11.1: What are the primary security risks when using AI coding tools?

**A:** The risks include: data leakage (sending proprietary code, secrets, or PII to third-party AI APIs), prompt injection (malicious content in code or repos that manipulates the AI's behavior), credential exposure (AI accidentally committing `.env` files, API keys, or tokens), supply chain attacks (malicious packages recommended or installed by AI — the March 2026 axios supply chain attack on Claude Code's npm package is a real example), unauthorized actions (AI executing destructive commands without proper safeguards), training data contamination (proprietary code being used to train future models — check the provider's data retention policy), and model manipulation through adversarial inputs in the codebase.

### Q11.2: How do you prevent data leaks when using AI tools?

**A:** At the organizational level: use enterprise plans with data retention guarantees (zero data retention / ZDR), enforce API-only access with audit logging, implement network-level controls to restrict which AI services developers can reach, and classify data sensitivity levels. At the project level: use `.gitignore`-style exclusion patterns to prevent sensitive files from being read, configure `deniedMcpServers` to block unauthorized integrations, implement PreToolUse hooks that scan for secrets before any tool execution, use Anthropic's enterprise admin controls for policy enforcement, never put actual secrets in CLAUDE.md — reference environment variable names instead. At the developer level: review tool invocations before approving, avoid pasting customer data into AI chats, use anonymization for realistic test scenarios.

### Q11.3: How do you protect against prompt injection attacks?

**A:** Prompt injection occurs when untrusted content (e.g., a malicious comment in a code file, a crafted issue description, or a README in a cloned repo) contains instructions that manipulate the AI. Defenses include: never fully trusting AI output without review, using hooks to validate actions regardless of what the model "thinks," implementing file-level permissions (restrict which directories the agent can write to), sandboxing AI execution environments, being cautious when AI processes user-supplied content (forms, tickets, external repos), treating any instruction found inside data as suspect, and using the `--disallowedTools` flag to restrict the agent's capabilities when processing untrusted input. The 2026 Claude Code architecture addresses this by requiring explicit trust prompts before consequential actions.

### Q11.4: What security considerations exist around MCP servers?

**A:** MCP servers extend the AI's attack surface. Each server is a potential vector for data exfiltration (the server could send data to unauthorized endpoints), privilege escalation (the server might have more permissions than the AI should), credential theft (servers need auth tokens that could be compromised), and man-in-the-middle attacks (especially with remote SSE-based servers). Mitigations: only use trusted MCP servers, audit server code before deployment, use the `deniedMcpServers` setting to blocklist unauthorized servers, implement network segmentation, rotate credentials regularly, and monitor MCP server traffic for anomalies. Enterprise admins should maintain an approved MCP server list.

### Q11.5: How do you handle API key and secret management with AI tools?

**A:** Never put secrets directly in configuration files, prompts, or CLAUDE.md. Use environment variables and reference them by name. Implement pre-commit hooks (both git hooks and Claude Code hooks) that scan for secret patterns (API keys, tokens, passwords) and block commits. Use tools like `git-secrets`, `trufflehog`, or `gitleaks` in your CI pipeline. For MCP servers that need credentials, use secure credential stores and inject at runtime. Claude Code's recent removal of DNS cache commands from auto-allow shows Anthropic's ongoing attention to information leakage vectors.

### Q11.6: What is the ANTI_DISTILLATION flag found in Claude Code?

**A:** This is a protective mechanism discovered in Claude Code's architecture. When enabled, it injects fake tool definitions into API requests — decoy tools designed to corrupt training data that anyone might try to extract from Claude Code's API traffic. This is a defense against competitors or malicious actors who might try to reverse-engineer or distill the system's capabilities by observing its API calls. It demonstrates the kind of adversarial thinking needed in production AI systems.

---

## 12. AUTOMATION & CI/CD INTEGRATION

### Q12.1: How do you integrate Claude Code into CI/CD pipelines?

**A:** Use print mode (`-p`) with pre-approved tools. Common patterns include: code review on PR (`git diff main | claude -p "review for bugs and security issues" --allowedTools "Read,Grep"`), automated test generation (`claude -p "generate tests for changed files" --allowedTools "Read,Write,Bash" --max-budget-usd 2`), documentation updates (`claude -p "update API docs for changed endpoints"`), changelog generation from commits, security scanning with natural language analysis, and PR description generation. Set `--max-budget-usd` and `--max-turns` to bound cost and prevent infinite loops. Use `--output-format json` when parsing results programmatically.

### Q12.2: How do you use Claude Code for automated code review?

**A:** Pipe the diff into Claude Code in print mode: `git diff main | claude -p "Review this diff for: 1) bugs, 2) security issues, 3) performance concerns, 4) style violations per our CLAUDE.md conventions. Output a JSON report." --output-format json --model sonnet`. For PR-based workflows, trigger this in GitHub Actions on pull_request events. Post the review as a PR comment. Use `--max-budget-usd` to cap costs. For deeper reviews, let the agent read full files for context with `--allowedTools "Read,Grep,Glob"`. This can run alongside (not replacing) human review, catching issues humans commonly miss while humans focus on architectural decisions.

### Q12.3: How do you prevent runaway costs in CI automation?

**A:** Three layers of protection: first, `--max-budget-usd` sets a hard dollar cap per invocation; second, `--max-turns` limits the number of agentic iterations; third, `--tools` or `--allowedTools` restricts which tools the agent can use (e.g., read-only for review tasks). Additionally, use model tiering — Haiku for simple checks, Sonnet for moderate analysis. Monitor aggregate spending through API dashboards. Set up alerts when daily or weekly spend exceeds thresholds. For organizations, enterprise admin controls can enforce spending limits per user or per project.

### Q12.4: Can you use Claude Code as part of a deployment pipeline?

**A:** Yes, but with caution. Use it for pre-deployment checks (review configuration, validate environment variables, check for common deployment issues), generating release notes, and verifying database migration scripts. For actual deployment execution, the "defer" hook mechanism allows a human-in-the-loop: the agent prepares the deployment, a hook defers at the critical step, a human reviews and resumes. Never give an automated AI agent unrestricted deployment permissions to production without human approval gates.

---

## 13. WORKFLOW DESIGN & AGENTIC PATTERNS

### Q13.1: What are the common agentic workflow patterns in 2026?

**A:** The main patterns are: (1) Linear chain — one agent completes steps sequentially (read → analyze → fix → test); (2) Fan-out / fan-in — a parent spawns multiple sub-agents in parallel, then aggregates results; (3) Router — a coordinator analyzes the task and delegates to specialized agents; (4) Human-in-the-loop — the agent works autonomously but pauses at checkpoints for human approval; (5) Continuous agent — runs 24/7 monitoring logs, tickets, or channels and acting on triggers; (6) Critic loop — one agent generates, another reviews, iterating until quality thresholds are met.

### Q13.2: How do you design an effective multi-agent workflow?

**A:** Start by decomposing the task into independent units of work. Assign each unit to an agent with the minimum permissions and model tier needed. Define clear interfaces — what inputs does each agent receive and what outputs does it produce? Implement coordination through file-based state (shared directories), MCP messaging, or parent-child relationships. Add safeguards: budget caps, turn limits, and hooks for enforcement. Monitor with logging and observability tools. Test the workflow end-to-end with representative tasks before deploying. Common mistake: over-architecting — start with a single agent and add complexity only when you hit real limitations.

### Q13.3: What is the "Continuous Agent" pattern?

**A:** A continuous agent is a Claude Code session that runs indefinitely (often on a server), monitoring channels and acting on triggers. Examples include: monitoring a Telegram channel and responding to messages, watching a log file for errors and auto-generating fixes, polling a ticket queue and triaging incoming issues, and running periodic maintenance tasks. The architecture requires: a keep-alive mechanism, hooks for safety (preventing the agent from accumulating dangerous state), MCP servers for external communication, and careful security configuration since it runs unattended. This is an advanced pattern that requires robust error handling and monitoring.

### Q13.4: What is the ReAct pattern?

**A:** ReAct (Reasoning + Acting) is a foundational agent architecture where the model alternates between reasoning steps (thinking about what to do) and action steps (calling tools, reading files, running commands). The model first reasons about the current state and what action would be most useful, then executes that action, then reasons about the result and plans the next step. This loop continues until the task is complete. Claude Code fundamentally operates on this pattern. Understanding ReAct helps you design effective prompts — you can explicitly ask the model to "think step by step about what files to read before making changes."

---

## 14. ROLE-SPECIFIC: DEVELOPER

### Q14.1: How should a developer use AI tools in their daily workflow?

**A:** Morning: pull latest changes, start a Claude Code session, ask it to summarize overnight changes and identify potential issues. During development: use AI for writing boilerplate, generating test cases, exploring unfamiliar APIs, and debugging. For code review: pipe PR diffs through AI for a first-pass review before human review. For documentation: ask AI to generate or update docs for changed code. For debugging: paste error logs and stack traces, ask for root cause analysis. End of day: use AI to generate commit messages and PR descriptions. Key discipline: always review AI output, maintain your understanding of the code, and keep sessions focused.

### Q14.2: How do you debug effectively with AI tools?

**A:** Provide rich context: paste the error message, relevant stack trace, the failing code, and what you expected vs. what happened. Tell the AI about your environment (Node version, OS, relevant config). Ask it to reason about possible causes before jumping to solutions. For complex bugs: let Claude Code read the relevant source files, run the failing test, and analyze the output — it can often trace through call chains that would take a human much longer. For intermittent bugs: ask the AI to add logging/instrumentation to narrow down the issue. Common mistake: asking "why doesn't this work?" with just a code snippet and no error message — always include the actual error.

### Q14.3: How do you use AI for refactoring?

**A:** First, ask the AI to analyze the current code and explain its structure. Then, ask it to propose a refactoring plan (plan mode) — what changes, in what order, and why. Review the plan before authorizing execution. Use the "critic loop" pattern: have the agent refactor, then separately evaluate the result. Ensure tests exist before refactoring (ask the AI to generate them if missing). Use hooks to auto-run tests after each file change. For large refactors: use sub-agents to handle different modules in parallel, then the parent agent resolves integration issues.

---

## 15. ROLE-SPECIFIC: TECH LEAD

### Q15.1: How should a tech lead govern AI tool usage across a team?

**A:** Establish an AI usage policy covering: approved tools and tiers, data classification rules (what can and cannot be sent to AI), code review standards for AI-generated code, spending budgets per developer, required hooks and security checks, CLAUDE.md templates and maintenance ownership, and a feedback loop for sharing effective prompts and patterns. Use enterprise admin controls to enforce policies. Create shared skills and custom commands that encode team standards. Monitor usage and costs. Conduct periodic audits of AI-generated code quality. Foster a culture where AI assists but does not replace human judgment for critical decisions.

### Q15.2: How do you maintain code quality when AI generates a significant portion of the code?

**A:** Three-layer strategy: prevention (CLAUDE.md with coding standards, skills with templates, hooks for linting/formatting), detection (CI pipeline with SAST, test coverage requirements, mandatory human review for critical paths), and monitoring (track defect rates in AI-generated vs. human code, measure test coverage trends, audit for security vulnerabilities). Require that AI-generated code meets the same bar as human code — same review process, same test requirements, same style standards. Teams that relax standards for AI code consistently see quality degradation over time.

### Q15.3: How do you onboard a team to AI-powered development?

**A:** Start with training on fundamental concepts (prompting, context management, security risks). Set up the project's CLAUDE.md collaboratively — this forces the team to document architecture and conventions. Introduce AI tools incrementally: first for documentation and test generation (low risk), then for code review augmentation, then for code generation with review. Create shared custom commands for common workflows. Establish pair-programming sessions where experienced AI users mentor others. Track productivity metrics to demonstrate value. Address fears directly: AI augments developers, it does not replace them — the developer's role shifts toward direction, review, and architecture.

---

## 16. ROLE-SPECIFIC: ARCHITECT

### Q16.1: How can an architect use AI tools for system design?

**A:** Use AI for design exploration: describe the system requirements and constraints, then ask the AI to propose multiple architectural options with tradeoffs. Have it generate architecture diagrams (via Mermaid or PlantUML), API contracts, data models, and sequence diagrams. Use AI to evaluate designs against quality attributes (scalability, security, maintainability). Ask it to identify potential failure modes and suggest mitigation strategies. For technology selection: have AI compare options against your specific requirements. Key discipline: the architect provides the constraints, the AI explores the solution space — the architect makes the final decision.

### Q16.2: How should an architect approach CLAUDE.md as architecture documentation?

**A:** CLAUDE.md should be a living architecture document that serves both humans and AI. Include: system overview with a component diagram reference, key architectural decisions (and their rationale — ADRs), module boundaries and dependency rules, critical invariants that must be preserved, performance and security requirements, and integration patterns with external systems. This is powerful because it means the AI will naturally follow your architecture when generating code. If CLAUDE.md says "all database access goes through the repository layer," the AI will generate repository-pattern code. It turns architecture documents from passive references into active enforcement.

### Q16.3: How do you use AI to evaluate architectural tradeoffs?

**A:** Present the AI with the specific decision context: what are the requirements, what are the constraints, what are the options. Ask it to analyze each option against quality attributes (availability, scalability, security, cost, complexity, team expertise). Ask for real-world examples of each approach at scale. Request it to identify the "hidden costs" of each option — what maintenance burden, what operational complexity, what vendor lock-in. Use it to stress-test your preferred option: "Play devil's advocate — what are the strongest arguments against this approach?" The AI's breadth of knowledge about industry patterns makes it excellent at surfacing considerations you might miss.

---

## 17. ROLE-SPECIFIC: QA ENGINEER

### Q17.1: How can QA engineers leverage AI tools?

**A:** Test case generation: describe the feature and ask for comprehensive test cases including edge cases, boundary conditions, and negative tests. Test automation: have AI write test scripts (Playwright, Cypress, pytest) from test case descriptions. Bug analysis: paste error reports and logs, ask for root cause analysis and reproduction steps. Test data generation: create realistic, varied test data sets. Exploratory testing guidance: describe the feature and ask AI for an exploratory testing charter. Regression risk analysis: pipe a diff through AI and ask "what existing functionality could be affected by these changes?" Coverage analysis: identify untested code paths and generate tests to cover them.

### Q17.2: How do you use AI for test automation effectively?

**A:** Provide the AI with the application's page structure (or component API), the test framework you use, and examples of existing tests that match your conventions. Ask it to generate tests that follow your patterns. For UI tests: describe the user flow in natural language, then ask for the Playwright/Cypress implementation. For API tests: provide the OpenAPI spec and ask for comprehensive endpoint tests. For unit tests: point the AI at the source file and ask for tests covering all branches. Critical: always run the generated tests — AI often generates tests that look right but have subtle assertion errors. Use Claude Code's ability to run tests and self-correct.

### Q17.3: How do you use AI for performance testing and security testing?

**A:** For performance testing: describe the system's performance requirements, have AI generate load test scripts (k6, JMeter, Locust), and analyze the results. Ask AI to identify potential bottlenecks from code review. For security testing: use AI to generate OWASP Top 10 test cases for your endpoints, review authentication and authorization flows, analyze input validation, and identify potential injection points. Have the AI review security configurations (CORS, CSP, rate limiting). Important caveat: AI is a complement to, not replacement for, dedicated security scanning tools (SAST/DAST/IAST).

---

## 18. ROLE-SPECIFIC: SCRUM MASTER / PM

### Q18.1: How can Scrum Masters and PMs use AI tools?

**A:** Sprint planning: use AI to analyze the backlog and suggest sprint compositions based on team velocity, dependencies, and priority. Story refinement: paste rough requirements and have AI generate well-structured user stories with acceptance criteria. Retrospective analysis: feed AI the retro notes and have it identify patterns across sprints. Meeting facilitation: use AI to generate agendas, summarize meeting notes, and extract action items. Stakeholder communication: draft sprint reviews, status updates, and risk reports. Dependency analysis: ask AI to map dependencies between stories and identify potential blockers. Velocity forecasting: provide historical data and ask for projections.

### Q18.2: How do you write effective AI-friendly user stories?

**A:** Structure stories with clear context, action, and outcome. Include explicit acceptance criteria that can be translated into test cases. Specify technical constraints (API contract, database schema, existing patterns to follow). Reference the CLAUDE.md or architecture docs for how this feature fits into the system. Avoid ambiguity — AI struggles with "use best judgment" but excels with "validate email format using RFC 5322, return a 400 error with a specific error code for invalid emails." Attach wireframes or mockups for UI stories. The more precise the story, the more accurately AI can implement it.

### Q18.3: How does AI change the estimation process?

**A:** AI collapses the effort distribution: simple tasks become nearly trivial (AI handles them in minutes), moderate tasks become simple, but complex tasks (novel architecture, ambiguous requirements, critical security) remain complex. This compresses the story point scale. Teams should recalibrate estimates around AI-augmented throughput. Focus estimation on: complexity of the problem (not the coding effort), review and testing effort, integration risk, and the likelihood that AI will need significant human correction. Some teams add a "AI confidence" factor to estimates — how likely is it that AI can handle this with minimal human intervention?

---

## 19. RAG, EMBEDDINGS & KNOWLEDGE SYSTEMS

### Q19.1: What is RAG and when should you use it?

**A:** RAG (Retrieval-Augmented Generation) enhances AI responses by retrieving relevant documents from a knowledge base before generating an answer. Use RAG when: the AI needs access to private/proprietary data not in its training set, information changes frequently and must be current, you need traceable citations for compliance, or the knowledge base is too large to fit in a single context window. RAG architecture involves: chunking documents into segments, generating embeddings (vector representations), storing them in a vector database, retrieving the most relevant chunks based on the query, and including those chunks as context when prompting the LLM.

### Q19.2: What are the key chunking strategies?

**A:** Fixed-size chunking splits text into uniform token-count segments — simple but breaks semantic boundaries. Semantic chunking uses NLP to split at natural boundaries (paragraphs, sections, topics) — preserves meaning but varies in size. Recursive chunking splits hierarchically (by heading, then paragraph, then sentence) until chunks are small enough. For code: split by function/class/file. For documentation: split by section/subsection. Key tradeoffs: smaller chunks are more precise but lose context; larger chunks preserve context but may include irrelevant information. Most teams in 2026 use adaptive chunking that considers both size limits and semantic coherence.

### Q19.3: What is Agentic RAG?

**A:** Agentic RAG combines the RAG retrieval pattern with an agentic loop. Instead of a single retrieve-then-generate step, an agent iteratively queries the knowledge base: retrieve initial results, analyze them, decide if they are sufficient, formulate refined queries, retrieve again, and synthesize. This handles complex multi-part questions that need information from multiple documents. The agent can also decide when to use RAG vs. its own knowledge, route queries to different indexes (e.g., code vs. docs vs. tickets), and validate retrieved information against multiple sources.

### Q19.4: What is Graph RAG?

**A:** Graph RAG combines knowledge graphs with retrieval-augmented generation. Instead of storing flat document chunks, it builds a graph of entities and relationships from the corpus. Queries traverse the graph to find relevant connected information — this is especially powerful for questions that require reasoning across multiple documents (e.g., "Which teams are affected by this API change?" requires understanding org structure, service ownership, and API dependencies). Graph RAG outperforms traditional RAG on complex analytical queries but requires more setup and maintenance.

---

## 20. GOVERNANCE, COMPLIANCE & RESPONSIBLE AI

### Q20.1: What governance framework should organizations implement for AI coding tools?

**A:** A practical governance framework includes: a usage policy (what tools are approved, what data can be shared, who can use what tier), access controls (enterprise admin settings, API key management, network restrictions), audit and monitoring (log all AI interactions, track costs, review generated code quality), data protection (ZDR agreements, on-premise options for sensitive codebases, data classification), quality standards (mandatory review for AI-generated code, test coverage requirements, architectural review for AI-proposed designs), incident response (what to do if AI generates harmful code, data leak procedures), and continuous improvement (feedback mechanisms, periodic policy reviews, training updates).

### Q20.2: How do you ensure compliance with data privacy regulations when using AI?

**A:** First, understand what data flows to the AI provider — map all data paths including MCP server connections. Ensure your provider agreement covers data processing requirements under applicable regulations (GDPR, CCPA, HIPAA). For sensitive industries: use enterprise plans with ZDR, consider on-premise or private cloud deployments, implement data masking/anonymization for any customer data that might appear in code or configs, maintain audit logs of all AI interactions, and implement data residency requirements. For code that handles PII: use hooks to scan for PII patterns before sending files to the AI.

### Q20.3: What is responsible AI development and how does it apply to coding tools?

**A:** Responsible AI in coding means: transparency (team members can see what AI generated and why), accountability (a human is responsible for every piece of merged code, regardless of who/what wrote it), fairness (ensuring AI tools are accessible to all team members, not creating a two-tier system), safety (hooks, permissions, and review processes prevent harmful outcomes), and continuous monitoring (tracking AI tool effectiveness, biases in code suggestions, and impact on team dynamics). It also means being honest about AI's limitations — it can write code that looks correct but contains subtle bugs, and it can perpetuate biases present in its training data.

---

## 21. ADVANCED & EMERGING TOPICS (2026 STANDARD)

### Q21.1: What is Model Context Protocol (MCP) Step-up Authorization?

**A:** MCP step-up authorization allows servers to request elevated permissions mid-session. If a server starts with basic read permissions but encounters an operation requiring write access, it can trigger a re-authorization flow. The user sees a new consent prompt for the elevated scope. This follows the principle of least privilege — servers start with minimal permissions and escalate only when needed. The March 2026 fix addressed a bug where step-up authorization failed when a refresh token already existed.

### Q21.2: What are Plugins in Claude Code?

**A:** Plugins are installable bundles that combine skills, agents, hooks, and MCP configs into a single distributable unit. They solve the "works-on-my-machine" problem by packaging an entire toolchain extension into a versioned, installable package. Install locally with `claude plugin add --path ./my-plugin` or from the marketplace with `claude plugin install my-plugin`. Skills get namespaced (`/pluginName:skillName`) to avoid collisions. Priority if names collide: enterprise > user > project > plugin. Plugins represent the maturation of Claude Code from a tool into a platform with an ecosystem.

### Q21.3: What is Computer Use and how does it work in Claude Code?

**A:** Computer Use is Claude's ability to control a computer — clicking, typing, scrolling, reading screens — as a tool-using agent. In Claude Code's architecture, Computer Use is implemented as an MCP server (`@ant/computer-use-mcp`), not as a special model capability. This means it follows the same permission, hook, and security patterns as any other tool. Use cases include: automated UI testing, filling out web forms, interacting with desktop applications, and tasks that require visual inspection. It runs via browser control (Playwright) with explicit permission gating.

### Q21.4: What is KAIROS?

**A:** KAIROS is an autonomous background agent mode found in Claude Code's architecture. It is feature-flagged — not publicly launched at the time of the code leak but compiled and gated. It represents the evolution toward fully autonomous AI agents that can run independently, manage their own task queues, and operate without continuous human interaction. Understanding KAIROS signals awareness of where the industry is heading: from interactive assistants to autonomous agents that work alongside human teams.

### Q21.5: What is model distillation and why should you care?

**A:** Model distillation is the process of training a smaller, cheaper model to replicate the behavior of a larger, more expensive model. In the context of AI tools: distillation threats mean that API traffic could be captured and used to train competing models (hence the ANTI_DISTILLATION flag in Claude Code). For practitioners: distillation enables cost optimization — a team might distill a fine-tuned Opus model into a Haiku-sized model for high-volume, well-defined tasks, dramatically reducing costs while maintaining quality for those specific use cases.

### Q21.6: What is Mixture of Experts (MoE) and how does it affect tool usage?

**A:** MoE is a model architecture where multiple specialized sub-networks ("experts") exist within a single model, and a router selects which experts to activate for each input. This means larger model capacity without proportionally larger compute costs — only the relevant experts are activated per query. For tool users: MoE models may exhibit different strengths depending on the task type (one "expert" might be specialized in code, another in analysis). Understanding MoE helps when you notice that a model excels at certain tasks but struggles with others — it might be routing to a less specialized expert.

### Q21.7: What is Sparse Checkout in Claude Code worktrees?

**A:** The `worktree.sparsePaths` setting allows `claude --worktree` to check out only specific directories in large monorepos using git sparse-checkout. This is critical for performance in enterprise codebases — instead of cloning a 10GB monorepo, you only check out the directories relevant to your task. This reduces disk usage, speeds up git operations, and limits the files the AI needs to consider, improving both performance and relevance of AI-generated code.

### Q21.8: What is Self-RAG?

**A:** Self-RAG is an advanced retrieval pattern where the model itself decides when retrieval is necessary. Instead of always retrieving (which adds latency and noise) or never retrieving (which limits knowledge), the model evaluates its own confidence and retrieves only when it determines its internal knowledge is insufficient. This reduces unnecessary retrieval calls, improves response speed for questions the model can answer directly, and improves quality for questions that genuinely need external knowledge.

### Q21.9: What are the key observability practices for AI agents in production?

**A:** Monitor at multiple levels: API metrics (request volume, latency, error rates, costs per session), agent behavior (number of turns per task, tool usage patterns, compaction frequency), output quality (defect rates, test pass rates, human correction frequency), and business impact (developer time saved, deployment frequency, incident rates). Use OpenTelemetry (OTEL) integration — Claude Code supports OTEL exporters for logs, metrics, and traces. Build dashboards showing per-developer and per-project AI usage, costs, and quality metrics. Alert on anomalies: sudden cost spikes, high compaction rates (indicating context management issues), or increased error rates.

### Q21.10: What is the LLMOps lifecycle and how does it differ from MLOps?

**A:** LLMOps is the operational practice of managing LLM-based applications in production. It differs from traditional MLOps in several ways: no model training in most cases (you consume API models, not train your own), prompt management replaces model versioning, evaluation is harder (subjective output quality vs. measurable metrics), cost management is token-based (not compute-time-based), and the feedback loop is faster (change a prompt vs. retrain a model). The LLMOps lifecycle: design prompts → test with evaluation datasets → deploy with monitoring → collect feedback → iterate. Tools include prompt registries, A/B testing for prompts, evaluation frameworks, and cost dashboards.

---

## 22. SCENARIO-BASED QUESTIONS

### Q22.1: Scenario — Your CI pipeline runs Claude Code for automated review. One morning, costs spike 10x. What happened and how do you respond?

**A:** Likely causes: a PR with an extremely large diff triggered extensive analysis, the agent entered an infinite loop (e.g., test-fix-test cycle that never converges), a misconfigured `--max-turns` or missing `--max-budget-usd`, or a model API price change. Immediate response: check the CI logs for the specific invocations, identify which job consumed the most tokens, and verify budget caps are in place. Fix: add `--max-budget-usd` to all CI invocations, set `--max-turns` to a reasonable limit (e.g., 5 for reviews), implement cost alerts, and review the triggering PR to understand why analysis was excessive. Longer term: add a pre-check that estimates diff size and skips AI review for trivially large diffs (e.g., generated files).

### Q22.2: Scenario — A developer's CLAUDE.md instruction to "never modify auth code" was ignored by the AI after a long session. Why?

**A:** After many turns, the CLAUDE.md content likely got compacted away — the context window filled up and the compaction algorithm summarized early context (including the CLAUDE.md instructions). The solution is not to rely solely on CLAUDE.md for critical prohibitions. Instead, implement a `PreToolUse` hook on the `Write`/`Edit` tool that checks if the target file is in the `auth/` directory and blocks the modification deterministically. This hook will fire every time, regardless of context length or compaction state. Additionally, keep sessions shorter, use `/compact` proactively, and put the most critical rules at the beginning of CLAUDE.md (compaction tends to preserve recent and prominent content).

### Q22.3: Scenario — You need to migrate a 500-endpoint REST API to a new versioning scheme. How do you approach this with AI tools?

**A:** Break it into phases. Phase 1 — Analysis: use Claude Code to scan all 500 endpoints, catalog their current structure, and produce a mapping document. Use sub-agents in parallel to analyze different service modules. Phase 2 — Planning: based on the catalog, have Claude propose the migration strategy (e.g., URL prefix versioning, header-based, etc.) with a concrete changeset per endpoint. Review this plan with the team. Phase 3 — Execution: use Claude Code to execute changes in batches (e.g., 20 endpoints at a time), with a test suite running after each batch. Use hooks to auto-run tests after every file write. Phase 4 — Validation: use AI to generate comprehensive integration tests for the new versioned API. Phase 5 — Documentation: AI updates OpenAPI specs, README, and client migration guides. Use `--max-budget-usd` on each batch to keep costs predictable.

### Q22.4: Scenario — A junior developer pastes customer PII into a Claude chat to debug a production issue. What are the implications and what processes should prevent this?

**A:** Implications depend on the AI provider's data retention policy and applicable regulations. If the provider processes or stores the data, it may constitute a data breach under GDPR/CCPA/HIPAA. Even with ZDR, the data traversed external networks. Prevention requires multiple layers: training (educate all developers on data classification and AI usage policies), technical controls (enterprise proxies that scan outbound AI requests for PII patterns, hooks that detect and block PII in tool inputs), process controls (require data anonymization for all debugging — use scripts that mask PII before sharing), and incident response (have a documented procedure for AI-related data exposure, including notification obligations).

### Q22.5: Scenario — You're architecting a system that uses AI agents to process customer support tickets. What architecture would you propose?

**A:** The architecture has three tiers. Ingestion: tickets arrive via API/webhook, are classified by a fast model (Haiku) for urgency and category, and PII is detected and masked. Processing: an agentic system retrieves relevant context via RAG (product docs, customer history, past tickets) and generates a draft response. For complex tickets, a sub-agent researches the issue, another drafts the response, and a critic agent reviews for tone and accuracy. Human layer: all responses go through a human review queue (except for pre-approved simple categories like password resets). Feedback: human corrections are logged and used to refine prompts and RAG retrieval. Guardrails: strict token budgets per ticket, response quality scoring, escalation triggers for low-confidence answers, and complete audit logging for compliance.

---

## 23. 2026 BLEEDING-EDGE STANDARDS

### Q23.1: What is Hybrid AI Execution?
**A:** Hybrid AI Execution is the standard pattern of running fast, quantized models (like Llama/Mistral) locally on top-tier developer machines for real-time, privacy-safe autocomplete and linting, while selectively routing complex reasoning tasks (like architectural refactoring) to highly capable cloud models (e.g., Opus) via MCP or CLI. This maximizes speed and privacy while minimizing token spend.

### Q23.2: What is Shadow Mode Execution for AI Agents?
**A:** Running agents against live production traffic defensively without giving them write capabilities (read-only mode). Organizations use this to evaluate an agent's hypothetical decisions—such as triaging tickets, isolating microservices during incidents, or generating code patches—against what human operators actually did, ensuring strict safety compliance before full deployment.

### Q23.3: How does Self-Healing Observability work?
**A:** It connects AI agents directly to OpenTelemetry (OTEL) traces and APM tools like Datadog. When a production exception spikes, the AI autonomously retrieves context from the stack trace, identifies the root cause in the source code, and auto-generates a Pull Request with a fix and corresponding test before human on-call engineers even intervene.

### Q23.4: How does LLM-as-a-Judge act natively in CI/CD?
**A:** Using a faster, cheaper model (such as Haiku or Sonnet) as an automated CI validation step to continuously evaluate PR descriptions, generated test cases, or even code generated by other larger models. It acts as an impartial reviewer enforcing strict CLAUDE.md policies before allowing merges.

### Q23.5: How can QA leverage AI for Mutation Testing?
**A:** Instead of solely writing test cases, QA uses AI agents to deliberately introduce subtle, semantic bugs (mutations) into the codebase. The goal is to verify if the existing automated QA test suite correctly fails and catches the AI's complex injected flaws, ensuring maximum robustness against subtle refactoring errors.

### Q23.6: How is AI shifting velocity forecasting for Scrum Masters?
**A:** Transitioning from manual, bias-prone estimation sessions to probabilistic AI forecasting. The AI analyzes historical ticket completion data, individual developer PR velocities, and codebase complexity metrics (e.g., tech debt scores) to predict highly accurate sprint deliverability timelines without human estimation fatigue.

### Q23.7: What is Context Pinning vs. standard Compaction?
**A:** When AI context windows fill up (even at 1M+ tokens), standard compaction summarizes history, potentially losing fidelity. Context Pinning lets engineers define strict metadata blocks that the AI must *never* compact (such as critical security constraints or API contracts), ensuring vital rules persist flawlessly throughout indefinitely long execution loops.

### Q23.8: How do Air-Gapped MCPs mitigate data leaks natively?
**A:** For the highest compliance requirements (e.g., healthcare, defense), teams deploy fully isolated, internal-network-only MCP servers. This allows AI agents to interact with highly sensitive PII or restricted databases on local infra without the raw data ever touching the public internet or external LLM API payloads.

---

## 24. PERMISSION SYSTEM & TRUST LEVELS

### Q24.1: How does the Claude Code permission system work?

**A:** Claude Code uses a layered permission system that gates every tool invocation. Each tool call is evaluated against: (1) the user's chosen permission mode, (2) enterprise policy overrides, (3) project-level settings, and (4) session-level allowlists. When a tool call is not pre-approved, Claude surfaces a trust prompt requiring explicit human confirmation before execution. This ensures the agent cannot take destructive or sensitive actions without consent. The system distinguishes between read-only operations (low risk), write operations (medium risk), and execution operations (high risk — bash commands, network requests).

### Q24.2: What are the permission modes available?

**A:** Claude Code offers several permission modes: **Default mode** requires manual approval for every write/execute action — safest but most interactive. **Auto-approve mode** (`--dangerously-skip-permissions`) bypasses all prompts — use only in sandboxed/CI environments, never on a developer machine with real credentials. **Selective auto-approve** uses `--allowedTools` and `--disallowedTools` to pre-approve specific tools (e.g., allow Read and Grep but require approval for Bash and Write). **Enterprise policy mode** is set by admins and cannot be overridden by individual users — it defines which tools are always allowed, always denied, or require approval. The best practice for CI/CD is selective auto-approve with the minimum tools needed for the task.

### Q24.3: How do enterprise admin controls enforce security policies?

**A:** Enterprise admins configure policies at the organization level that cascade down to all users. These policies can: restrict which models are available, enforce mandatory hooks (e.g., security scanning before every file write), deny specific MCP servers (`deniedMcpServers`), set maximum budget caps per session or per user, require specific permission modes, block certain tool categories entirely, and enforce data classification rules. Admin policies are the highest priority in the configuration hierarchy — they override user-level, project-level, and plugin settings. This ensures compliance even if individual developers misconfigure their local setup.

### Q24.4: What is the principle of least privilege applied to AI agents?

**A:** Just as with human users and service accounts, AI agents should operate with the minimum permissions needed for the task. For a code review agent: grant Read, Grep, and Glob — deny Write, Bash, and MCP. For a test-runner agent: grant Read and Bash (restricted to test commands) — deny Write. For a documentation agent: grant Read and Write (scoped to docs/) — deny Bash. Use `--allowedTools` in CI, PreToolUse hooks for runtime enforcement, and CLAUDE.md instructions as advisory guidance. Over-permissioned agents are the most common security mistake teams make — the March 2026 npm supply chain incident was exacerbated by agents with unrestricted Bash access.

---

## 25. EXTENDED THINKING & REASONING

### Q25.1: What is extended thinking and how does it work?

**A:** Extended thinking (also called "thinking mode" or "chain-of-thought") allows the model to perform deliberate, step-by-step reasoning before producing its final response. When enabled, Claude generates internal reasoning tokens (visible as a "thinking" block) where it plans its approach, considers alternatives, and works through complex logic. These thinking tokens consume context and cost money but dramatically improve quality for complex tasks — architecture decisions, subtle bug diagnosis, multi-file refactoring plans, and security analysis. The `/effort` command in Claude Code controls reasoning depth.

### Q25.2: When should you use high vs. low reasoning effort?

**A:** **Low effort** (fast, cheap): simple file edits, formatting, renaming, straightforward code generation with clear patterns, data extraction, file search. **Medium effort** (balanced): general coding tasks, writing tests, documentation, standard debugging, code review. **High effort** (thorough, expensive): architectural design decisions, complex multi-step debugging, security audits, performance optimization analysis, unfamiliar codebases, ambiguous requirements. The key insight: reasoning effort has diminishing returns — a simple rename does not benefit from 10,000 thinking tokens. Match effort to task complexity. In CI/CD, default to medium and reserve high for security-critical checks.

### Q25.3: How do thinking tokens affect cost and context?

**A:** Thinking tokens count toward both your cost and your context window. A high-effort response might generate 5,000-20,000 thinking tokens before the actual output — that is real cost (billed at the model's output token rate) and real context consumed. For a session doing many complex operations, thinking tokens can fill context faster than actual code output. Strategies: use `/effort low` for simple tasks within a session, start new sessions for new topics (resetting thinking overhead), and use sub-agents with lower effort for simple delegated tasks. In print mode (`-p`), thinking tokens are not shown in output but still incur cost.

### Q25.4: What is "streaming thinking" and why does it matter?

**A:** Streaming thinking displays the model's reasoning process in real-time as it generates. This provides transparency — you can see the model's approach and interrupt if it's heading in the wrong direction, potentially saving tokens and time. It also builds trust: when you see the model systematically analyzing your code, checking edge cases, and reasoning about tradeoffs, you can validate its process, not just its output. In Claude Code, the thinking block appears above the response. For educational and onboarding purposes, streaming thinking is invaluable — junior developers learn problem-solving approaches by watching the model reason.

---

## 26. CLAUDE CODE PLATFORMS & IDE INTEGRATION

### Q26.1: What platforms is Claude Code available on in 2026?

**A:** Claude Code is available across five platforms: (1) **CLI** — the original terminal-native experience, most powerful for automation and scripting; (2) **Desktop App** — native Mac and Windows applications with a rich UI, conversation history, and visual diff review; (3) **VS Code Extension** — inline AI assistance within VS Code, combining editor integration with Claude Code's agentic capabilities; (4) **JetBrains Extension** — same capabilities in IntelliJ, WebStorm, PyCharm, and other JetBrains IDEs; (5) **Web App** (claude.ai/code) — browser-based interface accessible from any device. All platforms share the same underlying model and capabilities but differ in UI and workflow integration.

### Q26.2: How do IDE extensions differ from the CLI?

**A:** IDE extensions provide visual advantages: inline diff previews, syntax-highlighted code suggestions, click-to-apply changes, integrated terminal output, and direct access to editor features like "go to definition" and diagnostics. The CLI provides power-user advantages: full scripting and piping, CI/CD integration, headless operation, session management, and maximum control over flags and configuration. IDE extensions are better for interactive development (writing features, reviewing changes visually). CLI is better for automation, batch operations, and complex multi-step workflows. Many developers use both — IDE extension for coding sessions, CLI for automation and git operations.

### Q26.3: How does the VS Code extension integrate with editor features?

**A:** The VS Code extension can read editor diagnostics (TypeScript errors, ESLint warnings), access the active file and selection, use "go to definition" and "find references" through the Language Server Protocol (LSP), show inline diffs for proposed changes, and run terminal commands within the editor's integrated terminal. This bidirectional integration means Claude can see the same errors you see, navigate code the same way you do, and propose changes that you can review visually before accepting. The extension also supports the same CLAUDE.md, hooks, and MCP configurations as the CLI.

### Q26.4: What is the Desktop App's advantage over CLI?

**A:** The Desktop App provides a richer experience for long sessions: persistent conversation history with search, visual file diffs with syntax highlighting, drag-and-drop file attachment, screenshot/image input for multi-modal tasks, a project picker for switching between codebases, and a more accessible interface for developers less comfortable with terminals. It also provides session management UI — browsing, resuming, and searching past sessions visually. For teams onboarding to AI tools, the Desktop App has a lower barrier to entry than the CLI.

---

## 27. GIT WORKTREES & ISOLATION PATTERNS

### Q27.1: What are git worktrees in the context of AI agents?

**A:** Git worktrees allow you to check out multiple branches of the same repository simultaneously in different directories, without cloning the repo multiple times. In Claude Code, `--worktree` (or `claude --worktree`) creates an isolated worktree for the agent's work. This means the agent can make changes, create branches, and run tests without affecting your main working directory. If the agent's work is good, you merge it; if not, the worktree is discarded cleanly. This is the standard pattern for safe agentic development in 2026.

### Q27.2: When should you use worktrees?

**A:** Use worktrees when: you want to keep coding while the agent works on a separate task, the agent's task involves risky or experimental changes, you're running multiple agents in parallel on different features, the agent needs to create commits without disrupting your staged changes, or in CI/CD where isolation is mandatory. Do not use worktrees for: quick single-file edits, read-only analysis, or tasks where you need to interact closely with the agent's changes in real-time. Worktrees add setup overhead (~5-10 seconds) so they're not worth it for trivial tasks.

### Q27.3: How do worktrees integrate with sparse checkout?

**A:** For large monorepos, combining worktrees with sparse checkout (`worktree.sparsePaths` in Claude Code settings) is essential. Instead of checking out the entire repo (which could be 10GB+), you specify only the directories relevant to the task. For example, if the agent is working on the auth service in a monorepo, sparse checkout only pulls `services/auth/`, `libs/common/`, and `configs/`. This reduces disk usage, speeds up git operations, and limits the files the AI considers — improving both performance and relevance. This combination is the standard pattern for enterprise monorepo development with AI agents.

### Q27.4: How do you manage multiple parallel agents using worktrees?

**A:** The pattern is: spawn multiple sub-agents, each in its own worktree, working on independent tasks. Each agent creates a feature branch, makes its changes, and commits. The parent agent (or human) then reviews and merges each branch. Key considerations: agents must work on non-overlapping files to avoid merge conflicts, each worktree needs its own set of dependencies installed (node_modules, venv, etc.), and budget caps should be set per-agent. This fan-out pattern can dramatically speed up large tasks — a 10-module refactoring that takes one agent an hour might take 10 parallel agents 15 minutes (including overhead).

---

## 28. STRUCTURED OUTPUT & JSON SCHEMA

### Q28.1: What is structured output and why does it matter for automation?

**A:** Structured output forces the AI to respond in a specific format (typically JSON) that machines can parse reliably. In Claude Code, use `--output-format json` to get JSON responses instead of natural language. For strict schema enforcement, add `--json-schema '{"type":"object","properties":...}'` to validate the output against a JSON Schema. This is critical for automation pipelines where downstream tools expect specific data structures — a code review bot needs structured findings, not prose paragraphs. Without structured output, you need fragile text parsing; with it, you get reliable machine-to-machine communication.

### Q28.2: How do you use JSON Schema validation in Claude Code?

**A:** Pass a JSON Schema with `--json-schema` alongside `--output-format json`. Claude will constrain its output to match the schema exactly. Example: for a code review pipeline, define a schema with `{"type":"object","properties":{"findings":{"type":"array","items":{"type":"object","properties":{"file":{"type":"string"},"line":{"type":"integer"},"severity":{"type":"string","enum":["critical","warning","info"]},"message":{"type":"string"}}}}}}`. The model's output will always be valid against this schema, eliminating parsing errors in your pipeline. This is the foundation of reliable AI automation.

### Q28.3: When should you use structured vs. natural language output?

**A:** Use structured output when: the result feeds into another program, you need consistent formatting across invocations, you're aggregating results from multiple agents, or you need to store/query results in a database. Use natural language when: a human is the primary consumer, the task requires nuanced explanation, you need the model to express uncertainty or caveats, or the output is inherently unstructured (creative writing, exploration). In practice, CI/CD pipelines should almost always use structured output; interactive sessions should almost always use natural language.

---

## 29. OAUTH, MCP AUTHENTICATION & API SECURITY

### Q29.1: How does OAuth 2.1 work with MCP servers?

**A:** MCP servers that access protected resources (GitHub, Slack, databases) need authentication. OAuth 2.1 is the standard protocol: the MCP server redirects the user to the resource provider's authorization page, the user grants access, the provider returns an authorization code, the MCP server exchanges it for access and refresh tokens, and subsequent API calls use the access token. Claude Code manages this flow transparently — when an MCP tool requires auth, the user sees a browser prompt. The key 2026 improvement is PKCE (Proof Key for Code Exchange) which prevents authorization code interception attacks, mandatory in OAuth 2.1.

### Q29.2: What is MCP step-up authorization and when does it trigger?

**A:** Step-up authorization occurs when an MCP server starts with basic permissions but encounters an operation requiring elevated access. For example, a GitHub MCP server might start with read-only scope but need write access to create a PR. Instead of requesting all permissions upfront (violating least privilege), it triggers a re-authorization flow for just the additional scope. The user sees a new consent prompt. This follows the principle of progressive authorization — start minimal, escalate only when needed. A March 2026 bug fix addressed cases where step-up failed when a refresh token already existed.

### Q29.3: How should API keys be managed across MCP servers?

**A:** Never hardcode API keys in `.mcp.json` or any config file. Best practices: use environment variables (`"env": {"API_KEY": "MY_SERVICE_KEY"}` in MCP config, with the actual value in your shell profile or a `.env` file excluded from git), use OS keychain/credential stores for sensitive tokens, rotate keys regularly, use separate keys per MCP server (blast radius containment), implement PreToolUse hooks that validate MCP server identity before allowing privileged operations, and for team setups, use a secrets manager (Vault, AWS Secrets Manager) with runtime injection. Enterprise admins should audit which MCP servers have access to which credentials.

### Q29.4: What are the security considerations for remote MCP servers (SSE/HTTP)?

**A:** Remote MCP servers (connected via SSE or HTTP instead of local stdio) introduce network-level risks: data in transit can be intercepted (always require TLS/HTTPS), the server endpoint could be compromised or impersonated (verify server certificates and use certificate pinning where possible), latency and availability affect agent reliability, and the server operator can see all data sent to and from the AI. Mitigations: use only trusted, audited remote servers, prefer local stdio servers for sensitive data, implement network segmentation, monitor traffic patterns for anomalies, and use the `deniedMcpServers` setting to block unauthorized remote endpoints.

---

## 30. CLAUDE AGENT SDK & CUSTOM AGENTS

### Q30.1: What is the Claude Agent SDK?

**A:** The Claude Agent SDK is a framework for building custom AI agents programmatically using Claude as the reasoning engine. Unlike Claude Code (which is an end-user CLI tool), the Agent SDK is a developer library for embedding agentic AI into your own applications. You define tools the agent can use, configure its behavior, set guardrails, and orchestrate multi-agent workflows. It supports Python and TypeScript, handles tool execution loops, manages context windows, and provides hooks for observability. Use it when Claude Code's built-in capabilities are insufficient and you need custom agent logic.

### Q30.2: How does tool use (function calling) work in the Claude API?

**A:** Tool use allows Claude to call functions you define. You send a list of tool definitions (name, description, input JSON Schema) alongside your prompt. Claude analyzes the task, decides which tools to call, and returns a `tool_use` response with the tool name and input arguments. Your application executes the tool and sends the result back as a `tool_result` message. Claude then either calls another tool or produces a final response. This loop continues until the task is complete. Every Claude Code capability — file reads, bash execution, web search — is implemented as a tool following this exact pattern.

### Q30.3: When should you build a custom agent vs. using Claude Code?

**A:** Use Claude Code when: your workflow fits within its existing tools and configuration (file editing, bash, MCP, git), you need interactive terminal sessions, or you want CI/CD automation with `-p` mode. Build a custom agent when: you need custom tools not available in Claude Code (e.g., proprietary internal APIs), you need to embed AI into a web application or service, you require custom orchestration logic (complex multi-agent coordination, custom retry/fallback), you need fine-grained control over the agentic loop, or you're building a product that includes AI capabilities. Claude Code is for developers using AI; the Agent SDK is for developers building AI-powered applications.

### Q30.4: What are the key components of a custom agent built with the SDK?

**A:** A custom agent consists of: **System prompt** (defines the agent's role, capabilities, and constraints), **Tools** (functions the agent can call — each with a name, description, and JSON Schema for inputs), **Guardrails** (input/output validators that check for safety, correctness, or compliance), **Memory/State** (how the agent maintains context across turns — conversation history, external storage), **Orchestration** (the loop that sends messages, processes tool calls, handles errors, and decides when to stop), and **Observability** (logging, tracing, and metrics for monitoring agent behavior in production). The SDK handles the core loop; you customize the components.

---

## 31. BATCH API & ASYNC PROCESSING

### Q31.1: What is the Batch API and when should you use it?

**A:** The Batch API allows you to submit large numbers of Claude requests as a batch and receive results asynchronously — typically at a 50% cost discount compared to real-time API calls. Use it when: you need to process hundreds or thousands of items (code review across a large codebase, generating documentation for all endpoints, analyzing test coverage for every module), latency is not critical (results can arrive hours later), and cost optimization is a priority. The Batch API is ideal for nightly CI/CD jobs, periodic codebase audits, and bulk content generation.

### Q31.2: How do you design a batch processing pipeline for code analysis?

**A:** Architecture: (1) **Preparation** — scan the codebase, identify items to process, create a manifest of prompts with file paths and instructions; (2) **Submission** — submit the batch via the Batch API, receive a batch ID; (3) **Polling** — periodically check batch status or use webhooks for completion notification; (4) **Processing** — retrieve results, parse structured JSON outputs, aggregate findings; (5) **Reporting** — generate a summary report, create issues for critical findings, update dashboards. Use JSON Schema for structured output to ensure machine-parseable results. Set per-item token limits to prevent any single item from dominating the batch cost.

### Q31.3: What is the cost difference between real-time, batch, and cached requests?

**A:** As of 2026 pricing (Claude Opus): **Real-time** — full price ($15/M input, $75/M output); **Prompt caching (cache hit)** — ~90% reduction on cached input tokens; **Batch API** — 50% discount on both input and output tokens; **Combined (cached + batch)** — the deepest discount, stacking cache hits within batch processing. For a team running nightly code review on a 500-file codebase: real-time might cost $50/run, batch brings it to $25, and with prompt caching (shared system prompt + CLAUDE.md across all items) it drops to ~$10. These savings compound over time — smart batching can reduce annual AI costs by 70%+.

---

## 32. MULTI-MODAL AI IN DEVELOPMENT

### Q32.1: How does multi-modal AI apply to software development?

**A:** Multi-modal AI processes images, screenshots, PDFs, and other non-text inputs alongside code and text. In development contexts: **Screenshot analysis** — paste a bug screenshot and ask "what's wrong with this UI?"; **Design-to-code** — provide a Figma mockup image and generate the HTML/CSS/React implementation; **PDF specification reading** — feed a 50-page product spec PDF and ask the AI to extract requirements or generate user stories; **Diagram understanding** — share architecture diagrams and ask the AI to validate against the actual codebase; **Error screenshot debugging** — paste screenshots of error dialogs, crash screens, or log outputs when text is not easily copyable.

### Q32.2: How does Claude Code handle images and screenshots?

**A:** Claude Code can read image files (PNG, JPG, GIF, WebP) directly using its file reading tools. In the Desktop App, you can drag-and-drop images into the conversation. In the CLI, reference image paths in your prompt. Claude analyzes the visual content and can: describe what's in the image, identify UI bugs or layout issues, generate code to reproduce a design shown in the image, read text from screenshots (OCR-like capability), and compare visual diffs between two screenshots. For PDF files, Claude can read and analyze content, with support for specifying page ranges on large documents (e.g., pages 1-20).

### Q32.3: What are the limitations and best practices for multi-modal input?

**A:** Limitations: image analysis is not pixel-perfect — small text, low contrast, and complex diagrams may be misread. Claude cannot interact with images (no clicking, zooming). Very large images consume many tokens. PDFs beyond ~20 pages per request need pagination. Best practices: provide high-resolution, well-cropped images; supplement images with text descriptions for critical details; for design-to-code, include both the mockup and written specifications; for screenshots with errors, also paste the error text if available; use page ranges for large PDFs rather than loading the entire document.

---

## 33. AI CODE ATTRIBUTION & LEGAL CONSIDERATIONS

### Q33.1: How should AI-generated code be attributed?

**A:** The emerging 2026 standard is to include a `Co-Authored-By` trailer in git commits: `Co-Authored-By: Claude <noreply@anthropic.com>` (or the specific model used). This provides traceability — you can query git history to see how much code was AI-assisted. Some organizations also add comments in generated files or maintain a log of AI-assisted changes. Attribution serves multiple purposes: auditability for compliance, metrics tracking for ROI analysis, quality analysis (comparing defect rates in AI-generated vs. human code), and intellectual property documentation.

### Q33.2: What are the intellectual property implications of AI-generated code?

**A:** The legal landscape in 2026 is still evolving but key principles are: AI-generated code is generally not copyrightable on its own (the human directing the AI holds rights in most jurisdictions), organizations should treat AI as a tool (like a compiler) — the developer using it is responsible, there is a risk of license contamination if the model reproduces copyrighted training data (rare but possible), and organizations should have clear IP policies that address AI-generated code ownership. For open-source projects: AI-generated contributions should comply with the project's license. For proprietary code: ensure your AI provider agreement confirms no rights are claimed over generated output.

### Q33.3: What compliance requirements apply to AI-generated code in regulated industries?

**A:** Regulated industries (finance, healthcare, defense, automotive) have additional requirements: **Traceability** — ability to identify which code was AI-generated and review the prompts/context that produced it; **Validation** — AI-generated code in safety-critical paths must undergo additional testing and formal verification; **Audit logging** — complete records of AI interactions for regulatory review; **Human oversight** — a qualified human must review and approve all AI-generated code before deployment; **Documentation** — maintain records of AI tool versions, models used, and validation procedures. Some regulations (EU AI Act) may classify AI coding tools as limited-risk systems requiring transparency and user notification.

---

## 34. RATE LIMITING, FALLBACKS & RESILIENCE

### Q34.1: How do rate limits work with AI APIs and how do you handle them?

**A:** AI API providers impose rate limits on requests per minute (RPM), tokens per minute (TPM), and tokens per day (TPD). When you hit a limit, you receive a 429 (Too Many Requests) response with a `Retry-After` header. Handling strategies: implement exponential backoff with jitter, use request queuing to smooth burst traffic, distribute load across multiple API keys (where allowed), cache repeated requests (prompt caching), and batch non-urgent requests. In Claude Code, the `--fallback-model` flag automatically switches to an alternative model when the primary is rate-limited — e.g., fall back from Opus to Sonnet.

### Q34.2: What is the fallback model strategy?

**A:** Configure a chain of fallback models from most capable to most available: primary Opus → fallback Sonnet → emergency Haiku. When the primary model returns a rate limit error, Claude Code automatically retries with the next model in the chain. This ensures work continues even during high-demand periods. The tradeoff: fallback models may produce lower-quality output for complex tasks. Best practice: set fallbacks for interactive sessions (developer productivity matters more than perfect quality), but fail-fast for critical CI/CD checks (better to retry later than use a less capable model for security reviews).

### Q34.3: How do you build resilient AI-powered workflows?

**A:** Design for failure at every level: **API level** — fallback models, retry with backoff, request timeouts, circuit breakers that stop calling a failing API after N consecutive errors; **Agent level** — `--max-turns` prevents infinite loops, `--max-budget-usd` caps cost, hooks catch and handle errors; **Pipeline level** — idempotent operations (safe to retry), checkpointing (resume from last successful step), graceful degradation (if AI is unavailable, fall back to manual process or cached results); **Organizational level** — multi-provider strategy (don't depend solely on one AI provider), on-premise/local model fallbacks for critical operations, and regular disaster recovery testing.

---

## 35. AI IN INCIDENT RESPONSE & ON-CALL

### Q35.1: How can AI agents assist during production incidents?

**A:** AI agents can accelerate incident response at every stage: **Detection** — continuous agents monitoring logs/metrics that alert on anomalies before traditional threshold-based alerts fire; **Triage** — paste error logs and stack traces, get immediate root cause analysis and affected component identification; **Investigation** — the agent reads source code, traces call chains, checks recent deployments, and correlates with known issues; **Mitigation** — the agent proposes and (with human approval) executes fixes, rollbacks, or configuration changes; **Communication** — auto-generate incident updates for stakeholders, status page updates, and post-mortem drafts. Critical rule: AI assists, humans approve — never give an unattended agent production write access during an incident.

### Q35.2: How do you use AI for post-mortem analysis?

**A:** Feed the AI the incident timeline, logs, metrics screenshots, and chat transcripts. Ask it to: identify the root cause chain (proximate → contributing → systemic), evaluate whether existing monitoring should have caught the issue earlier, propose concrete action items (with priority and ownership suggestions), identify similar past incidents (via RAG against a post-mortem database), and draft the post-mortem document. AI excels at the tedious parts — correlating timestamps across systems, tracing dependency chains, and ensuring action items are specific and measurable. The human team focuses on judgment calls about organizational and process changes.

### Q35.3: What is the AI-assisted runbook pattern?

**A:** Traditional runbooks are static documents that operators follow step-by-step during incidents. AI-assisted runbooks are dynamic: the AI reads the runbook, interprets the current situation (error messages, metrics, system state), and executes the appropriate steps — adapting to the specific scenario rather than following a rigid script. For example, a "database overload" runbook might have 15 branches depending on the cause; the AI diagnoses the specific cause and follows the right branch, skipping irrelevant steps. Implement this via Claude Code with runbook markdown files as skills, MCP connections to monitoring tools, and hooks requiring human approval for destructive actions.

---

## 36. GUARDRAILS, SAFETY & CONTENT FILTERING

### Q36.1: What are guardrails in the context of AI agents?

**A:** Guardrails are programmatic checks that validate AI inputs and outputs to prevent harmful, incorrect, or policy-violating behavior. They operate at multiple levels: **Input guardrails** validate that the prompt/task is appropriate before the model processes it (e.g., blocking requests to generate malicious code); **Output guardrails** validate the model's response before it's shown or executed (e.g., checking generated code for known vulnerability patterns); **Tool guardrails** validate tool inputs/outputs during agentic execution (this is what Claude Code hooks implement). Unlike the model's own safety training (which is probabilistic), guardrails are deterministic — they always run and always enforce.

### Q36.2: How does Claude's constitutional AI approach affect coding tasks?

**A:** Constitutional AI (CAI) is the training approach where Claude learns to be helpful, harmless, and honest through a set of principles ("constitution") rather than only human feedback. In practice, this means Claude will: refuse to generate malware, exploits, or code designed to harm systems; flag potential security vulnerabilities in generated code; ask for clarification when a request is ambiguous and could have harmful interpretations; and express uncertainty rather than hallucinating APIs or functions. For developers, this means you can trust Claude to err on the side of safety — but you should be specific about your legitimate use case when working on security-related code (penetration testing, security research) to avoid unnecessary refusals.

### Q36.3: How do you implement output validation for AI-generated code?

**A:** Post-generation validation pipeline: (1) **Syntax check** — parse the generated code (compile, lint) to catch syntax errors; (2) **Static analysis** — run SAST tools (Semgrep, CodeQL, Bandit) to detect security vulnerabilities; (3) **Style check** — run formatters and linters (Prettier, ESLint, Ruff) to enforce conventions; (4) **Test execution** — run the test suite to verify correctness; (5) **Dependency check** — verify any new packages against known vulnerability databases; (6) **Custom checks** — project-specific validations (e.g., no direct database queries outside the repository layer). In Claude Code, implement this as PostToolUse hooks on Write/Edit tools. This pipeline should be identical to what human code goes through — AI code gets no shortcuts.

### Q36.4: What is the "tool poisoning" attack and how do you defend against it?

**A:** Tool poisoning occurs when a malicious MCP server provides tool descriptions designed to manipulate the AI's behavior. For example, a compromised MCP server might describe a tool as "safe file reader" but actually exfiltrate data when called. Or it might inject instructions into tool descriptions that override the system prompt. Defenses: only use trusted, audited MCP servers; review tool descriptions (visible via `--debug`); implement network monitoring for MCP server traffic; use enterprise admin controls to whitelist approved servers; and implement PreToolUse hooks that validate tool invocations against expected patterns. The fundamental principle: treat MCP servers as untrusted code and apply the same security review as any third-party dependency.

---

## 37. MODEL SELECTION STRATEGY ACROSS PROVIDERS

### Q37.1: How do you choose between Claude, GPT, Gemini, and open-source models?

**A:** Selection criteria in 2026: **Code quality** — Claude (Opus/Sonnet) and GPT-4o lead for complex coding; Gemini 2.5 Pro excels at large-context tasks; open-source (Llama 4, DeepSeek, Qwen 3) are competitive for standard tasks. **Context window** — Gemini offers 1M+ tokens natively; Claude offers up to 1M with extended context; GPT varies by model. **Cost** — open-source models are cheapest (free to run locally); Haiku/GPT-4o-mini are cheapest cloud options; Opus/GPT-4o are premium. **Privacy** — open-source models run locally with zero data exposure; all cloud providers offer ZDR enterprise plans. **Tool use** — Claude has the most mature tool-use architecture; all providers support function calling. **Speed** — smaller models (Haiku, GPT-4o-mini, Gemini Flash) are fastest. Choose based on your specific requirements, not brand loyalty.

### Q37.2: What is a multi-provider strategy and why implement one?

**A:** A multi-provider strategy uses different AI providers for different tasks or as fallbacks. Reasons: **Resilience** — if one provider has an outage, others keep you running; **Cost optimization** — route to the cheapest provider that meets quality requirements for each task; **Capability matching** — some providers excel at specific tasks (Gemini for long-context, Claude for tool use, local models for privacy); **Vendor lock-in avoidance** — maintaining flexibility to switch providers as the market evolves; **Compliance** — some jurisdictions or clients may require specific providers or data residency. Implementation: abstract the AI layer behind a common interface, implement provider-specific adapters, configure routing rules, and monitor quality across providers.

### Q37.3: When should you use local/open-source models vs. cloud APIs?

**A:** Use local models when: data privacy is non-negotiable (healthcare, defense, legal), you need zero-latency responses (IDE autocomplete, real-time suggestions), you want zero marginal cost at high volume, you're in air-gapped environments, or regulatory requirements mandate on-premise processing. Use cloud APIs when: you need maximum capability (frontier models outperform local ones for complex tasks), you cannot invest in GPU infrastructure, you need the latest model versions immediately, or your volume is moderate (cloud is cheaper than maintaining GPU servers below a certain threshold). The 2026 standard is hybrid: local models for autocomplete and simple tasks, cloud APIs for complex reasoning.

### Q37.4: How do you evaluate model quality for your specific use case?

**A:** Build an evaluation dataset from your actual work: collect 50-100 representative tasks with known-good outputs (code changes, reviews, bug diagnoses). Run each task through candidate models and score results on: correctness (does it produce working code?), relevance (does it address the actual problem?), completeness (does it handle edge cases?), style (does it follow your conventions?), and cost (tokens consumed per task). Automate this with structured output and automated test execution where possible. Re-evaluate quarterly as models improve. The model that's best for your React frontend may not be best for your Rust backend — test per-domain.

---

## 38. ADDITIONAL SCENARIO-BASED QUESTIONS

### Q38.1: Scenario — Your team's AI agent running in CI suddenly starts installing unexpected npm packages. What do you do?

**A:** This could be a prompt injection attack (malicious content in a PR manipulating the agent) or a supply chain attack (a compromised MCP server or dependency suggesting malicious packages). Immediate response: stop all CI runs using the AI agent, review the last N PRs for suspicious content in comments, README files, or code strings that could be prompt injection, audit the agent's tool permissions (it should not have unrestricted `npm install` access), and check MCP server configurations for unauthorized changes. Fix: restrict the agent's Bash tool to a specific allowlist of commands, implement a PreToolUse hook that blocks `npm install`, `pip install`, and similar commands, use a lockfile-based dependency management process where only humans can update dependencies, and add a PostToolUse hook that diffs package.json/package-lock.json after any agent operation.

### Q38.2: Scenario — You're setting up Claude Code for a team of 20 developers with varying skill levels. Design the rollout.

**A:** Phase 1 (Week 1-2): Set up enterprise admin controls — enforce permission policies, set budget caps ($50/dev/month initially), configure mandatory security hooks (secret scanning, destructive command blocking), and create the project CLAUDE.md collaboratively. Phase 2 (Week 3-4): Start with 5 power users — enable them with full capabilities, gather feedback, refine CLAUDE.md and create shared custom commands. Phase 3 (Week 5-8): Roll out to all 20 — start everyone in default permission mode (manual approval), provide training sessions, create a shared library of skills and commands. Phase 4 (Ongoing): Monitor costs and quality, promote power users to more permissive modes, collect and share effective prompts, and hold monthly retrospectives on AI tool effectiveness. Key metric: track AI-assisted vs. non-assisted PR cycle time, defect rates, and developer satisfaction.

### Q38.3: Scenario — An AI agent using extended thinking burns through $200 in tokens on a single debugging session. How do you prevent this?

**A:** Root cause: high reasoning effort on a complex, looping task without budget guards. The agent likely entered a think-debug-fix-test cycle with maximum reasoning at each step, and the accumulated thinking tokens plus growing context drove costs exponentially. Prevention: always set `--max-budget-usd` (e.g., $5 for standard tasks, $20 for complex ones), use `/effort low` for simple steps within a debugging session, start new sessions when context grows large (lower per-turn cost), use sub-agents for exploration (keeps main context lean), implement organizational alerts when any single session exceeds a threshold, and train developers to break large debugging tasks into smaller, focused sessions.

### Q38.4: Scenario — Your organization needs to comply with the EU AI Act. What changes to your AI development workflow are required?

**A:** The EU AI Act (enforcement began 2025-2026) classifies AI systems by risk level. AI coding tools are generally "limited risk" requiring: **Transparency** — developers must know when they're interacting with AI (already obvious with tools like Claude Code), code generated by AI should be attributable (Co-Authored-By tags), and automated decisions affecting users must be explainable. **Documentation** — maintain records of which AI systems are used, their versions, and their purposes. **Human oversight** — humans must review and approve AI-generated code before deployment. **Risk assessment** — document risks associated with AI tool usage (data leakage, code quality, security) and mitigation measures. Practical steps: implement attribution in git commits, maintain an AI tool registry, ensure all AI-generated code goes through human review, and document your AI governance policy.

### Q38.5: Scenario — You need to migrate from GitHub Copilot to Claude Code for your team. What's your strategy?

**A:** Gradual migration, not a hard cutover. Phase 1: Run both tools simultaneously — Copilot for inline completions (its strength), Claude Code for complex tasks, automation, and agentic workflows. This lets developers experience Claude Code's advantages without losing Copilot's IDE suggestions. Phase 2: Invest in Claude Code infrastructure — set up CLAUDE.md, create custom commands and skills that encode your team's patterns, configure MCP servers for your tools (Jira, Slack, monitoring). Phase 3: As developers become comfortable, reduce Copilot reliance and expand Claude Code usage — particularly for code review, test generation, and CI/CD. Phase 4: Evaluate whether Copilot still provides value alongside Claude Code or whether full migration is appropriate. Key: the tools are complementary — many teams keep both, using each for its strengths.

---

## QUICK REFERENCE: KEY TERMS GLOSSARY

| Term | Definition |
|---|---|
| **Agentic** | AI that autonomously plans, acts, observes, and iterates to complete tasks |
| **MCP** | Model Context Protocol — standard for connecting AI to external tools/services |
| **Hook** | Shell command that fires at lifecycle events, guaranteeing execution |
| **Skill** | Markdown file encoding domain expertise for specific task types |
| **Sub-agent** | Independent AI session spawned for focused tasks, reports to parent |
| **Agent Team** | Multiple AI sessions that coordinate and communicate with each other |
| **Context Window** | Total tokens the AI can process at once (200K standard, up to 1M) |
| **Compaction** | Automatic summarization of conversation history when context fills |
| **RAG** | Retrieval-Augmented Generation — enhancing AI with external knowledge |
| **ZDR** | Zero Data Retention — provider agreement not to store/train on your data |
| **Token** | Basic unit of text processing (~4 characters); basis for pricing |
| **Prompt Caching** | Reusing processed prompt prefix to reduce cost on repeated calls |
| **Model Tiering** | Using different model sizes for different task complexities |
| **Print Mode** | Non-interactive CLI mode for scripts and CI/CD (`-p` flag) |
| **CLAUDE.md** | Project documentation file read by Claude at session start |
| **ReAct** | Reasoning + Acting pattern — think then act in a loop |
| **Graph RAG** | RAG using knowledge graphs instead of flat document retrieval |
| **LLMOps** | Operational practices for managing LLM-based applications |
| **Elicitation** | MCP servers requesting structured input from users mid-task |
| **Sparse Checkout** | Checking out only needed directories in large monorepos |
| **Plugin** | Installable bundle combining skills, hooks, agents, and MCP configs |
| **Hybrid Execution** | Routing AI traffic between local edge models and cloud reasoning |
| **Shadow Mode** | Deploying agents read-only to monitor production vs human baseline |
| **Self-Healing Code** | End-to-end autonomous OTEL log parsing to PR patch generation |
| **LLM-as-a-Judge** | Models grading/verifying PRs and other model output natively in CI |
| **Context Pinning** | Enforcing specific context segments to survive compaction safely |
| **Permission Mode** | Trust level configuration controlling which tools require manual approval |
| **Extended Thinking** | Model's internal reasoning tokens generated before the final response |
| **Reasoning Effort** | Configurable depth of model thinking — low/medium/high via `/effort` |
| **Worktree** | Isolated git checkout allowing agents to work without affecting main directory |
| **Structured Output** | Forcing AI responses into machine-parseable formats (JSON) with schema validation |
| **JSON Schema** | Formal definition of expected output structure, enforced via `--json-schema` |
| **OAuth 2.1** | Authentication standard for MCP servers accessing protected resources |
| **PKCE** | Proof Key for Code Exchange — prevents authorization code interception |
| **Agent SDK** | Developer library for building custom AI agents using Claude as reasoning engine |
| **Tool Use** | API pattern where the model calls defined functions and processes their results |
| **Batch API** | Async API for submitting bulk requests at ~50% cost discount |
| **Multi-Modal** | AI capability to process images, screenshots, PDFs alongside text |
| **Co-Authored-By** | Git commit trailer attributing AI-generated code for traceability |
| **Fallback Model** | Alternative model used automatically when primary is rate-limited |
| **Circuit Breaker** | Pattern that stops calling a failing API after N consecutive errors |
| **Guardrails** | Deterministic programmatic checks validating AI inputs and outputs |
| **Constitutional AI** | Training approach using principles for safety rather than only human feedback |
| **Tool Poisoning** | Attack where malicious MCP server descriptions manipulate AI behavior |
| **EU AI Act** | European regulation classifying AI systems by risk level with compliance requirements |
| **Runbook** | Operational playbook for incident response, now AI-assistable via skills |
| **Memory System** | File-based persistent memory that carries context across Claude Code sessions |
| **Remote Agent** | Claude Code session running on cloud infrastructure, triggered via API or schedule |
| **Trigger** | Scheduled remote agent that executes on a cron schedule |
| **Fast Mode** | Same model with faster output optimization — does NOT switch to a different model |
| **Evals** | Evaluation datasets and frameworks for measuring AI output quality systematically |
| **AI Code Debt** | Technical debt introduced by AI-generated code accepted without full understanding |
| **Prompt Registry** | Centralized versioned storage for team-shared prompts and templates |
| **Sandboxed Execution** | Running AI agents in Docker/container isolation for security |
| **Citations** | Model capability to reference specific source passages that informed its response |
| **Streaming** | Real-time token-by-token delivery of model responses via SSE |
| **IaC** | Infrastructure as Code — AI-assisted Terraform, Pulumi, CloudFormation management |
| **Edge AI** | Running AI models locally on developer machines for privacy and speed |
| **Chargeback** | Allocating AI API costs to specific teams, projects, or cost centers |

---

## 39. CLAUDE CODE MEMORY & PERSISTENCE SYSTEM

### Q39.1: How does the Claude Code memory system work?

**A:** Claude Code has a persistent, file-based memory system stored in `~/.claude/projects/<project-path>/memory/`. It maintains an index file (`MEMORY.md`) that catalogs all individual memory files. Each memory is a separate markdown file with YAML frontmatter specifying a name, description, and type. The system is organized by memory types: **user** (who the user is, their role and preferences), **feedback** (corrections and validated approaches — what to do and not do), **project** (ongoing work, goals, deadlines, non-obvious context), and **reference** (pointers to external systems like Jira boards, Slack channels, dashboards). Memory is loaded at session start via MEMORY.md and individual files are read on demand. Critically, memory should NOT duplicate what can be derived from code, git history, or CLAUDE.md — it stores only non-obvious, cross-session context.

### Q39.2: What should and should not be stored in memory?

**A:** **Store:** user role and expertise level (so AI tailors explanations), feedback corrections (so mistakes aren't repeated), project context that isn't in code (deadlines, stakeholder decisions, compliance constraints), and references to external systems. **Do NOT store:** code patterns or architecture (read the code), git history or recent changes (use `git log`), debugging solutions (the fix is in the code), anything in CLAUDE.md, or ephemeral task details. The key insight: memory is for information that helps future conversations but cannot be derived from the current project state. A memory saying "user prefers single bundled PRs for refactors" is valuable; a memory saying "the auth module uses JWT" is not (the code shows that).

### Q39.3: How does memory differ from CLAUDE.md, tasks, and plans?

**A:** These serve different persistence purposes: **CLAUDE.md** is project-wide documentation read at every session start — for architecture, conventions, and team standards. **Memory** is cross-session personal context — user preferences, feedback, and project intel that wouldn't belong in a shared CLAUDE.md. **Tasks** are current-session work tracking — breaking down and monitoring progress on the current job. **Plans** are current-session implementation strategies — architecture decisions and step-by-step approaches for the task at hand. Use CLAUDE.md for "what every developer (and AI) should know about this project." Use memory for "what I learned about working with this specific user on this specific project."

### Q39.4: How should memory be maintained over time?

**A:** Memory is not write-once. Stale memories cause worse problems than no memory — the AI acts on outdated information confidently. Best practices: before acting on a memory, verify it against current code/state (a function mentioned in memory may have been renamed or deleted); update memories when information changes; remove memories that are no longer relevant; avoid duplicates — check existing memories before creating new ones; convert relative dates to absolute dates when saving (so "next Thursday" doesn't become meaningless later); keep MEMORY.md under ~200 lines (it's truncated beyond that); and organize semantically by topic, not chronologically.

---

## 40. REMOTE AGENTS, TRIGGERS & SCHEDULED EXECUTION

### Q40.1: What are remote agents in Claude Code?

**A:** Remote agents are Claude Code sessions that run on cloud infrastructure rather than on a developer's local machine. They are triggered via API calls, webhooks, or scheduled cron expressions. Remote agents enable: 24/7 automation without keeping a laptop open, CI/CD integration at scale, scheduled maintenance tasks (nightly code audits, weekly dependency checks), and event-driven workflows (respond to GitHub webhooks, Slack messages, or monitoring alerts). They run headless (no interactive terminal) and require pre-approved tool permissions since there is no human to click "allow."

### Q40.2: What are triggers and how do you configure them?

**A:** Triggers are scheduled remote agents that execute on a cron schedule. You create them with `claude schedule` or via the triggers API. Each trigger specifies: a cron expression (e.g., `0 9 * * 1` for every Monday at 9am), the prompt to execute, allowed tools, budget caps, and the target project directory. Common use cases: Monday morning codebase health reports, nightly security scans, weekly dependency update PRs, daily standup summaries from git activity, and periodic documentation freshness checks. Triggers use the project's CLAUDE.md and settings, so they follow the same conventions as local sessions.

### Q40.3: What are the security considerations for remote agents?

**A:** Remote agents run unattended, making security critical: **Permissions** — use the absolute minimum tools needed; a review agent needs Read/Grep/Glob only, not Write or Bash. **Secrets** — never embed API keys in trigger configs; use environment variable injection from a secrets manager. **Budget** — always set `--max-budget-usd` and `--max-turns` to prevent runaway costs. **Output** — remote agents can post to Slack, create PRs, or write files; ensure they cannot accidentally expose sensitive data in public channels. **Audit** — log all remote agent executions, inputs, outputs, and costs. **Network** — restrict outbound network access to only required endpoints. The "defer" hook mechanism is especially valuable here — remote agents can pause at critical decision points and wait for human approval before proceeding.

### Q40.4: How do remote agents integrate with existing CI/CD pipelines?

**A:** Two patterns: **Pipeline-triggered agents** — your CI/CD pipeline (GitHub Actions, GitLab CI, Jenkins) invokes Claude Code in print mode as a pipeline step, using the pipeline's compute and passing results back. **Standalone remote agents** — Claude Code runs on dedicated infrastructure (Anthropic's cloud or self-hosted), triggered by webhooks from your CI/CD system. The standalone pattern is better for long-running tasks (the agent keeps its own session alive) and for tasks that span multiple repos. The pipeline-triggered pattern is better for tightly coupled checks (code review on PR, test generation after merge) where results must gate the pipeline.

---

## 41. AI EVALUATION FRAMEWORKS (EVALS) & QUALITY MEASUREMENT

### Q41.1: What are evals and why are they critical in 2026?

**A:** Evals (evaluations) are systematic datasets and frameworks for measuring AI output quality. In 2026, as AI generates a significant portion of production code, "does it feel right?" is no longer sufficient — you need quantitative quality measurement. An eval consists of: a set of representative tasks (inputs), expected outputs or quality criteria (ground truth), a scoring function (automated or model-graded), and a reporting pipeline. Evals answer: "Is our AI setup actually producing good code?", "Did that CLAUDE.md change improve or degrade output?", "Is Opus worth the 5x cost over Sonnet for our tasks?" Without evals, you're flying blind — making prompt/model/config decisions based on vibes rather than data.

### Q41.2: How do you build an eval dataset for a development team?

**A:** Collect 50-100 representative tasks from your actual work, spanning categories: bug fixes, feature implementations, test writing, code review, refactoring, and documentation. For each task, capture: the input (prompt + relevant files), the expected output (or quality rubric), and metadata (complexity, domain, role). Sources: extract from past PRs (the PR description is the "prompt," the final code is the "expected output"), create synthetic tasks from your coding standards, and collect real prompts that produced notably good or bad results. Update the dataset quarterly — it should evolve with your codebase. Store evals in version control alongside the code.

### Q41.3: What scoring methods work for evaluating AI-generated code?

**A:** Three approaches: **Automated scoring** — does the generated code compile? Do tests pass? Does it match expected output exactly? These are objective, cheap, and fast. **Model-graded scoring (LLM-as-a-Judge)** — use a second model (often cheaper, like Haiku) to grade the first model's output against a rubric. This handles subjective quality dimensions (readability, style, architectural alignment) that automated checks miss. **Human scoring** — expert review for the hardest cases: security, architectural decisions, and edge case handling. Best practice: layer all three. Automated tests catch obvious failures, LLM-as-a-Judge catches quality issues, human review validates the eval system itself. Track scores over time to spot regressions.

### Q41.4: How do you use evals to make model/config decisions?

**A:** Run your eval dataset against different configurations and compare: Model A vs. Model B, high vs. low reasoning effort, different CLAUDE.md versions, with vs. without specific skills. For each configuration, measure: correctness rate, average quality score, token usage, latency, and cost per task. Present results as a decision matrix. Example: "Opus scores 92% correctness at $0.45/task; Sonnet scores 87% at $0.08/task — for our code review pipeline, Sonnet is the better value." Re-run evals after model updates (providers release new versions frequently). Automate eval runs in CI so they trigger on CLAUDE.md or skill changes.

### Q41.5: What is red-teaming for AI coding tools?

**A:** Red-teaming is adversarial testing — deliberately trying to make the AI produce harmful, incorrect, or policy-violating output. For coding tools: try prompt injection through code comments, test if the AI can be manipulated into ignoring CLAUDE.md rules, attempt to extract secrets from context, try to get the AI to execute destructive commands, test boundary cases where safety and helpfulness conflict. Red-teaming should be part of your eval suite — include adversarial tasks alongside normal ones. Results inform your hook configurations, permission settings, and CLAUDE.md guardrails. In regulated environments, periodic red-team assessments may be required for compliance.

---

## 42. DEVELOPER EXPERIENCE METRICS & AI ROI

### Q42.1: How do you measure the ROI of AI coding tools?

**A:** Measure across four dimensions: **Velocity** — PR cycle time (time from first commit to merge), deployment frequency, lead time for changes. **Quality** — defect escape rate (bugs reaching production), test coverage trends, code review turnaround time. **Cost** — AI API spend per developer per month, cost per PR, cost per line of code changed. **Satisfaction** — developer survey scores, tool adoption rates, retention impact. Compare metrics before and after AI adoption, controlling for other variables. Common pitfall: measuring only velocity without quality — teams that ship faster but with more bugs are not getting real ROI. A balanced scorecard across all four dimensions gives the true picture.

### Q42.2: What DORA metrics are most affected by AI tools?

**A:** The four DORA metrics (Deployment Frequency, Lead Time for Changes, Change Failure Rate, Mean Time to Recovery) are all positively impacted: **Deployment Frequency** increases as AI accelerates feature development and reduces manual bottlenecks. **Lead Time** decreases as AI-generated code reduces writing time and AI-assisted review speeds up the PR process. **Change Failure Rate** should decrease if AI-generated code is properly tested and reviewed — but can increase if teams skip review for AI code (a common anti-pattern). **MTTR** decreases as AI assists in incident diagnosis, root cause analysis, and fix generation. Track these before and after AI adoption to quantify impact.

### Q42.3: How do you implement cost allocation (chargeback) for AI tools?

**A:** For enterprise teams, AI costs must be attributed to teams, projects, or cost centers. Implementation: use separate API keys per team or project, tag all API requests with team/project metadata, aggregate costs from API provider dashboards, and distribute in monthly reports. For Claude Code specifically: use `--max-budget-usd` per project, track session-level costs via API logging, and use remote agent triggers with project-specific configurations. A common model: set a team-level monthly budget, alert at 80% usage, and require manager approval above budget. This prevents both overspending and artificial frugality (developers avoiding AI to save costs when it would save time).

### Q42.4: What are the common anti-patterns in measuring AI tool effectiveness?

**A:** **Lines-of-code bias** — measuring productivity by LOC generated rewards verbosity, not quality. **Ignoring review cost** — fast AI generation means nothing if humans spend 3x longer reviewing. **Survivorship bias** — only measuring successful AI interactions, ignoring the times developers abandoned AI output and wrote it themselves. **Short-term only** — measuring immediate speed gains without tracking long-term maintainability of AI-generated code. **Individual metrics** — measuring per-developer AI usage creates perverse incentives (gaming usage stats). **Missing counterfactual** — "we shipped 20% more features" doesn't prove AI caused it without a control group or baseline period.

---

## 43. AI FOR INFRASTRUCTURE AS CODE (IaC)

### Q43.1: How can AI tools assist with Infrastructure as Code?

**A:** AI accelerates IaC across the lifecycle: **Generation** — describe infrastructure requirements in natural language ("I need a VPC with 3 subnets, a NAT gateway, and an ALB") and get Terraform/Pulumi/CloudFormation code. **Review** — pipe IaC diffs through AI for security analysis (open security groups, missing encryption, overly permissive IAM), cost estimation, and best practice validation. **Migration** — translate between IaC tools (CloudFormation to Terraform) or upgrade syntax (HCL v0.12 to v1.x). **Troubleshooting** — paste Terraform plan errors and get root cause analysis. **Documentation** — auto-generate architecture descriptions from IaC files. Critical rule: always review AI-generated IaC before applying — a misconfigured security group or IAM policy can expose your entire cloud environment.

### Q43.2: What are the security risks of AI-generated IaC?

**A:** AI-generated IaC introduces unique risks: **Overly permissive policies** — AI tends to generate IAM policies with `*` wildcards for simplicity; always enforce least-privilege. **Default configurations** — AI may use default settings (public S3 buckets, unencrypted volumes) unless explicitly instructed otherwise. **Hardcoded secrets** — AI might embed example credentials or connection strings in config files. **Drift from standards** — AI might generate valid but non-compliant infrastructure that doesn't match your organization's tagging, naming, or network topology standards. Mitigation: use policy-as-code tools (OPA/Rego, Checkov, tfsec) as PostToolUse hooks, maintain IaC modules in CLAUDE.md that the AI should use, and require plan review (`terraform plan`) before any apply.

### Q43.3: How do you use AI for cloud cost optimization?

**A:** Feed the AI your current infrastructure state (Terraform state file, cloud billing reports, utilization metrics) and ask for optimization recommendations. AI can identify: over-provisioned instances (right-sizing opportunities), unused resources (orphaned EBS volumes, idle load balancers), reserved instance vs. spot vs. on-demand opportunities, architecture changes that reduce cost (serverless migration candidates, caching layers that reduce compute), and scheduling opportunities (dev environments that should shut down at night). Use structured output with a JSON schema for actionable recommendations that can feed into ticketing systems.

---

## 44. DOCKER, CONTAINERS & SANDBOXED AGENT EXECUTION

### Q44.1: Why should AI agents run in containers?

**A:** Containers provide isolation — the agent cannot access the host filesystem, network, or processes beyond what's explicitly mounted or exposed. This is essential for: **Security** — if an agent is compromised via prompt injection, damage is contained to the container. **Reproducibility** — the container has a known, consistent environment regardless of the developer's machine. **Resource control** — set CPU, memory, and disk limits to prevent runaway agents from impacting the host. **Cleanup** — discard the container after the task; no residual state left on the host. For CI/CD, containerized agents are the standard — they run in ephemeral environments that are destroyed after each job.

### Q44.2: How do you configure Claude Code to run in a Docker container?

**A:** The standard pattern: create a Dockerfile with your project dependencies, Claude Code CLI, and minimal tooling. Mount the project directory as a volume (read-only if the agent only needs to analyze, read-write if it needs to make changes). Pass API keys via environment variables (never bake them into the image). Set resource limits (`--memory`, `--cpus`). Example CI setup: `docker run --rm -v $(pwd):/workspace -e ANTHROPIC_API_KEY=$KEY claude-code -p "review /workspace" --allowedTools "Read,Grep,Glob" --max-budget-usd 2`. For development: use Docker Compose with a dedicated container for the agent that shares a volume with your editor container.

### Q44.3: What is the security model for containerized AI agents?

**A:** Defense in depth: **Container isolation** — agent runs as non-root, with read-only root filesystem, no privileged capabilities, and restricted syscalls (seccomp profile). **Network isolation** — allow only outbound HTTPS to the AI API endpoint; block all other network access to prevent data exfiltration. **Volume restrictions** — mount only the necessary project directories; never mount Docker socket, SSH keys, or cloud credentials. **Resource limits** — cap CPU, memory, and disk to prevent denial-of-service. **Ephemeral execution** — destroy the container after the task; no persistent state that could be compromised. This layered approach means that even if prompt injection manipulates the agent's behavior, the blast radius is contained to the disposable container.

---

## 45. PROMPT LIBRARIES, REGISTRIES & TEAM KNOWLEDGE

### Q45.1: What is a prompt library and why does a team need one?

**A:** A prompt library is a curated, versioned collection of proven prompts and templates that teams share for common tasks — code review, test generation, API design, debugging, documentation, and more. Without one, each developer crafts prompts from scratch, leading to inconsistent quality and wasted effort. A good prompt library includes: the prompt template, usage instructions, expected output examples, and known limitations. Store it in version control (`.claude/commands/` for Claude Code custom commands, or a shared repo). Treat prompts like code — review changes, track effectiveness, and deprecate underperforming ones.

### Q45.2: How do you version and manage prompts across a team?

**A:** Treat prompts as code artifacts: store in git, review changes via PR, tag releases, and track effectiveness metrics. Structure: one file per prompt with metadata (author, date, model compatibility, task type, effectiveness score). Use Claude Code's custom commands (`.claude/commands/`) as the primary distribution mechanism — when a developer types `/review`, they get the team's battle-tested review prompt, not an ad-hoc one. For cross-project prompts, use a shared repo and symlink or copy commands into project repos. Version prompts against model versions — a prompt optimized for Sonnet 4.6 may need adjustment for future models.

### Q45.3: How do skills differ from prompt libraries?

**A:** Prompt libraries are template collections — static text that gets inserted into conversations. Skills are active domain expertise — they encode procedures, decision trees, quality checklists, and multi-step workflows that Claude follows. A prompt library entry might be: "Review this code for security issues, checking OWASP Top 10." A skill would be: "When reviewing code for security, first identify all input boundaries, then check each against OWASP Top 10, then verify authentication flows, then check for secret exposure, then produce a structured finding report." Skills are richer and more behavioral than prompts. Use prompt libraries for simple, repeatable tasks; use skills for complex workflows where the procedure matters as much as the prompt.

---

## 46. AI CODE DEBT & TECHNICAL DEBT MANAGEMENT

### Q46.1: What is AI code debt?

**A:** AI code debt is a new category of technical debt specific to AI-generated code. It occurs when developers accept AI-generated code without fully understanding it — the code works now but becomes a maintenance burden because no human deeply understands its logic, edge cases, or design decisions. Symptoms: developers cannot explain why a function is implemented a certain way ("the AI wrote it"), AI-generated abstractions that don't fit the project's patterns, copy-paste patterns where the AI duplicated logic instead of using existing utilities, and over-engineered solutions where a simpler approach would suffice. AI code debt accumulates silently because AI output often looks professional and passes tests.

### Q46.2: How do you prevent AI code debt?

**A:** Prevention requires discipline at acceptance time: **Understand before merging** — if you cannot explain the code to a colleague, do not merge it. **Match project patterns** — use CLAUDE.md and skills to ensure AI follows existing conventions, not generic ones. **Prefer simplicity** — explicitly instruct the AI to use the simplest approach; AI tends to over-engineer. **Review for fit** — check that AI code uses existing utilities rather than reimplementing them. **Document intent** — if the AI's approach is non-obvious, add a brief comment explaining why (not what). **Test coverage** — require tests for AI-generated code; tests are documentation of expected behavior. **Periodic audits** — quarterly review of AI-generated code (identifiable via Co-Authored-By tags) to catch accumulated debt.

### Q46.3: How can AI help reduce existing technical debt?

**A:** AI is excellent at debt reduction tasks that are tedious for humans: **Migration** — update deprecated APIs, upgrade dependency versions, migrate syntax patterns (e.g., class components to hooks). **Standardization** — apply consistent error handling, logging, and naming conventions across a codebase. **Documentation** — generate JSDoc/docstrings for undocumented code, create architecture diagrams from source. **Dead code removal** — identify and safely remove unused functions, imports, and files. **Test backfill** — generate tests for legacy code that lacks coverage. **Dependency audit** — analyze dependency tree for vulnerabilities, outdated packages, and redundancies. Use sub-agents to parallelize debt reduction across modules, with hooks running tests after each change to ensure no regressions.

---

## 47. ADVANCED CONTEXT WINDOW STRATEGIES

### Q47.1: What are advanced strategies for managing the context window?

**A:** Beyond basic compaction, advanced strategies include: **Layered reading** — read file summaries first (function signatures, class outlines), only read full implementations when needed. **Targeted grep** — use Grep to find specific patterns instead of reading entire files. **Sub-agent offloading** — delegate exploratory searches to sub-agents whose full output doesn't enter the main context (only the summary does). **Session segmentation** — break a large task into focused sessions, each starting fresh with only the context needed for that phase. **Strategic file ordering** — read the most important files last (recency bias means the model pays more attention to recent context). **Pre-filtering** — use bash pipes to extract relevant portions of large files before reading them into context.

### Q47.2: How does extended context (1M tokens) change strategy?

**A:** Extended context (available on Claude Opus 4.6) expands the window to ~1M tokens, but this does NOT eliminate the need for context management. Reasons: cost scales linearly with context size (each turn resends everything), attention quality degrades for information in the middle of very large contexts ("lost in the middle" effect), and compaction still occurs — just later. Strategy with extended context: use it for tasks that genuinely need broad context (large refactors, cross-module analysis, comprehensive code reviews) but don't use it as an excuse to dump everything in. The model is more effective with 200K of well-curated context than 800K of everything including irrelevant files. Extended context is a safety net, not a strategy.

### Q47.3: What is context poisoning and how do you prevent it?

**A:** Context poisoning occurs when low-quality or misleading information enters the context window and degrades the model's output quality. Sources: reading outdated documentation, including irrelevant files that confuse the model's understanding, error messages from failed commands that the model fixates on, and chat history from earlier failed approaches that bias the model toward the same mistakes. Prevention: start fresh sessions for new approaches (don't carry failed attempt history), use `/clear` when switching tasks, be selective about which files to read (not everything in the directory), and use sub-agents for exploratory work so failed investigations don't pollute the main context. If you notice quality degrading mid-session, it's often cheaper to start fresh than to fight context pollution.

### Q47.4: How does the PostCompact hook help preserve critical context?

**A:** The PostCompact hook fires after automatic or manual compaction. Since compaction can lose nuances from early in the conversation, this hook lets you re-inject critical information. Patterns: re-read the CLAUDE.md (it's small and sets the tone for everything after), re-read a "session state" file that tracks key decisions made so far, log a warning to alert the developer that compaction occurred, or trigger a custom summary that captures domain-specific context the generic compactor might miss. Example hook script: read a `.claude/compaction-context.md` file containing invariants that must always be present.

---

## 48. CLAUDE API DEEP DIVE (TOOL USE, STREAMING, CITATIONS)

### Q48.1: How does tool use (function calling) work in the Claude API?

**A:** Tool use follows a multi-turn conversation loop: (1) You send a `messages` request with a `tools` array — each tool has a `name`, `description`, and `input_schema` (JSON Schema). (2) Claude analyzes the user's request and returns a `tool_use` content block with the tool `name` and `input` arguments. (3) Your application executes the tool and sends the result as a `tool_result` content block in a new user message. (4) Claude processes the result and either calls another tool or produces a final `text` response. This loop repeats until the task is complete. Key design principles: tool descriptions are the primary way Claude understands what tools do (make them clear and specific), input schemas constrain the arguments (use enums, required fields, descriptions), and the tool result should be concise (large results waste context).

### Q48.2: What is streaming and why does it matter for developer tools?

**A:** Streaming delivers the model's response token-by-token via Server-Sent Events (SSE) instead of waiting for the complete response. Benefits: **Perceived speed** — users see output immediately instead of waiting seconds for a full response. **Early interruption** — if the model is heading in the wrong direction, you can stop it before it generates thousands of useless tokens (saving money). **Progress indication** — for long responses, streaming shows the model is working (vs. a blank screen). **Thinking visibility** — extended thinking blocks stream in real-time, letting you validate the model's reasoning process. In Claude Code, streaming is enabled by default in interactive mode. For API integrations, use `stream=true` in the messages request and process `content_block_delta` events.

### Q48.3: What are citations and how do they improve trustworthiness?

**A:** Citations allow Claude to reference specific passages from provided source documents that informed its response. When you provide documents (via tool results, uploaded files, or context), Claude can cite specific paragraphs or sections, making its responses traceable and verifiable. This is critical for: **Compliance** — regulated industries need audit trails for AI-assisted decisions. **Trust** — developers can verify that the AI's code review comment is based on an actual coding standard, not a hallucination. **RAG quality** — citations show which retrieved documents the model actually used vs. ignored. Enable citations by including `citations: {enabled: true}` in your API request. The response includes source reference markers tied to specific input passages.

### Q48.4: How do you handle errors and retries with the Claude API?

**A:** Robust error handling for production: **429 (Rate Limited)** — read the `retry-after` header, implement exponential backoff with jitter, switch to fallback model if available. **529 (Overloaded)** — the API is under heavy load; back off more aggressively, try again in 30-60 seconds. **400 (Invalid Request)** — check your request format; common causes are exceeding max tokens, invalid tool schemas, or malformed messages array. **500 (Internal Error)** — retry with backoff; if persistent, check Anthropic's status page. Best practices: use a retry library with configurable backoff, set a maximum retry count (3-5), log all errors with full request context for debugging, implement circuit breakers that stop retrying after N consecutive failures, and always set timeouts on API calls (model responses can take up to 60+ seconds for complex tasks with extended thinking).

### Q48.5: What is the Messages Batches API and how does it work?

**A:** The Messages Batches API (Batch API) lets you submit up to 10,000 messages requests as a single batch, processed asynchronously at a 50% cost discount. Workflow: (1) Create a JSONL file with individual message requests, each with a `custom_id`. (2) Submit via `POST /v1/messages/batches`. (3) Poll the batch status or use webhooks for completion notification. (4) Retrieve results — each result is keyed by `custom_id` and contains the full message response. Use cases: nightly codebase audits, bulk documentation generation, mass test case creation, large-scale code migration analysis. Combine with prompt caching for even deeper discounts — if all batch items share the same system prompt, cached tokens are processed at ~10% of standard cost.

---

## 49. AI-ASSISTED DATABASE OPERATIONS & MIGRATIONS

### Q49.1: How can AI assist with database migrations?

**A:** AI accelerates every phase: **Schema design** — describe your data model requirements and get SQL DDL with proper indexes, constraints, and normalization. **Migration script generation** — describe the change ("add a `status` enum column to `orders` with default 'pending'") and get an idempotent migration script with rollback. **Migration review** — pipe migration scripts through AI for review: check for missing indexes on foreign keys, data loss risks, locking behavior on large tables, and rollback safety. **Data migration** — generate scripts that transform data as part of schema changes. **Testing** — generate migration test cases that verify both up and down migrations. Critical rule: always review AI-generated migrations against a production-like database; AI may miss database-engine-specific behaviors (MySQL vs. PostgreSQL locking differences, for example).

### Q49.2: What are the risks of AI-generated database operations?

**A:** Database operations are uniquely dangerous because they can cause: **Data loss** — an AI-generated `ALTER TABLE` might drop a column or truncate data during type conversion. **Downtime** — locking operations on large tables can block production traffic for minutes or hours. **Irreversibility** — unlike code changes, database changes often cannot be rolled back cleanly (you can't un-delete data). **Performance degradation** — missing or incorrect indexes, full table scans, or N+1 query patterns. Mitigation: never run AI-generated SQL against production directly, always test on a staging database with production-like data volume, use migration frameworks (Flyway, Alembic, Prisma Migrate) that enforce ordering and rollback, and implement PreToolUse hooks that block direct `psql`, `mysql`, or database CLI commands.

---

## 50. EDGE AI & ON-DEVICE CODING ASSISTANTS

### Q50.1: What is edge AI for development and why is it growing in 2026?

**A:** Edge AI runs models locally on developer machines (using GPU, Apple Silicon Neural Engine, or CPU). In 2026, quantized models (4-bit, 8-bit) like Llama 4, Mistral, Qwen 3, and DeepSeek run efficiently on consumer hardware. Benefits: **Zero latency** — autocomplete suggestions appear in <100ms vs. 500ms+ for cloud APIs. **Zero cost** — after hardware investment, no per-token charges. **Total privacy** — code never leaves the machine, critical for classified, regulated, or pre-patent work. **Offline capability** — works on planes, in secure facilities, and during API outages. Limitations: local models are less capable than frontier cloud models for complex reasoning; they excel at autocomplete, simple refactoring, and code navigation but struggle with architectural decisions and nuanced debugging.

### Q50.2: How does hybrid AI execution work in practice?

**A:** The 2026 standard setup: a local model (e.g., Llama 4 8B quantized) handles real-time IDE autocomplete, simple code navigation, and basic refactoring — tasks where speed matters more than depth. A cloud model (Claude Opus/Sonnet) handles complex tasks: multi-file refactoring, architectural decisions, security reviews, and debugging subtle issues — tasks where quality matters more than speed. Routing is either explicit (developer chooses) or automatic (IDE plugin routes based on task complexity heuristics — short completions go local, multi-file edits go cloud). This hybrid approach gives developers the best of both worlds: instant suggestions for routine work, deep reasoning for hard problems, and privacy by default.

### Q50.3: How do you evaluate local vs. cloud model quality for your use case?

**A:** Build a task-specific eval set (see Section 41). Run the same tasks through local and cloud models. Compare: **Correctness** — does the code work? **Completeness** — does it handle edge cases? **Style** — does it match project conventions? **Speed** — time from prompt to response. **Cost** — amortized hardware cost vs. API cost per request. Common findings: local models match cloud models for autocomplete and simple tasks (>90% equivalent), fall behind on multi-step reasoning (60-70% equivalent), and significantly trail on novel/complex problems (40-50% equivalent). Use these numbers to set your routing threshold — tasks below the local model's capability ceiling go local, everything else goes to cloud.

---

## ADDITIONAL INTERVIEW SCENARIOS (COMPREHENSIVE)

### Q-S1: Scenario — A developer commits code with Co-Authored-By: Claude, but the code has a critical security vulnerability. Who is responsible?

**A:** The human developer who committed and approved the merge is responsible. AI tools are instruments — like a compiler or linter, they assist but do not bear accountability. The Co-Authored-By tag is for traceability, not liability transfer. This is why code review standards should not be relaxed for AI-generated code. The developer's responsibility includes: understanding the code they commit, running security scans, ensuring test coverage, and validating against project security standards. Organizations should document this in their AI usage policy: "AI-generated code must meet the same review, testing, and security standards as human-written code. The committing developer is accountable for all code they merge."

### Q-S2: Scenario — Your AI agent needs to access a production database for debugging. How do you set this up safely?

**A:** Never give AI agents direct production database access. Instead: (1) Create a read-only replica or snapshot specifically for debugging. (2) Build an MCP server that provides structured query access with row-limit enforcement, query timeout, PII masking, and audit logging. (3) Configure PreToolUse hooks that block any SQL mutation commands (INSERT, UPDATE, DELETE, DROP, ALTER). (4) Use parameterized queries only — the MCP server should reject raw SQL string concatenation. (5) Set up network isolation — the MCP server runs in a restricted network segment with access only to the read replica. (6) Log every query for compliance audit. This gives the AI the diagnostic access it needs while preventing data modification, exposure, or exfiltration.

### Q-S3: Scenario — Your team's AI-generated test suite has 95% coverage but keeps missing real bugs. What's wrong?

**A:** This is "coverage theater" — a known anti-pattern with AI-generated tests. The AI optimizes for line coverage (easy to measure) rather than behavior coverage (hard to measure). Common issues: tests assert that functions return *something* without validating correctness, tests mirror the implementation logic (testing the code does what it does, not what it should do), tests don't cover error paths, edge cases, or race conditions, and tests use mocked dependencies that don't reflect real behavior. Fix: add mutation testing (Section 23.5) to verify tests actually catch bugs, require tests to assert specific business logic outcomes, write test descriptions before implementations ("should reject orders with negative quantities"), and use AI to generate adversarial test cases specifically designed to break the code.

### Q-S4: Scenario — You're evaluating whether to build a custom agent with the Agent SDK or use Claude Code for an internal developer portal. How do you decide?

**A:** Decision matrix: **Use Claude Code** if the portal needs are covered by its existing capabilities (file operations, bash, MCP, git), the users are developers comfortable with CLI/IDE, the workflows can be encoded as custom commands and skills, and you need rapid iteration without building infrastructure. **Use Agent SDK** if you need a web-based UI for non-developer users, custom authentication and authorization flows, integration with your existing application stack, custom tool implementations beyond what MCP provides, fine-grained control over the agentic loop (custom retry logic, state machines), or multi-tenant isolation (different teams seeing different tools). In practice: prototype with Claude Code (fast), validate the concept, then migrate to Agent SDK if you need productization beyond what Claude Code provides.

### Q-S5: Scenario — An AI agent in your CI pipeline creates a PR that passes all automated checks but introduces a subtle race condition. How do you prevent this systemically?

**A:** Layer defenses: **Static analysis** — add concurrency-aware linters (ThreadSanitizer for C++, go vet for Go, SpotBugs for Java) to the CI pipeline. **AI-specific review** — after the agent creates the PR, run a separate AI review step specifically focused on concurrency: "Review this diff for race conditions, deadlocks, atomicity violations, and shared state access without synchronization." **Mutation testing** — inject concurrency mutations (remove locks, reorder operations) and verify tests catch them. **Architecture rules** — encode concurrency patterns in CLAUDE.md (e.g., "all shared state must go through the message bus, never use direct shared memory"). **Human review gate** — for code touching concurrent systems, require human review regardless of automated check results. The fundamental insight: automated checks are necessary but insufficient for concurrency; defense in depth is the only reliable approach.
