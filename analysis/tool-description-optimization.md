# Tool Description Optimization Analysis

**Goal**: Reduce system prompt token usage by compressing tool descriptions while maintaining clarity.

## Current State Analysis

### Token Impact
- **Current**: ~20K tokens per turn from tool descriptions
- **Target**: Reduce by 50-70% (~10-14K token savings)
- **Location**: `/home/bonsaihorn/Projects/helios/dist/agents/system-prompt.js` line 133+ (coreToolSummaries)

### Verbosity Examples

**High-verbosity tools** (prime optimization candidates):

```javascript
cron: "Manage cron jobs and wake events (use for reminders; when scheduling a reminder, write the systemEvent text as something that will read like a reminder when it fires, and mention that it is a reminder depending on the time gap between setting and firing; include recent context in reminder text if appropriate)"
// Current: ~45 tokens → Optimized: ~10 tokens

session_status: "Show a /status-equivalent status card (usage + time + Reasoning/Verbose/Elevated); use for model-use questions (📊 session_status); optional per-session model override" 
// Current: ~28 tokens → Optimized: ~8 tokens

exec: "Run shell commands (pty available for TTY-required CLIs)"
// Current: ~8 tokens → Optimized: ~4 tokens
```

## Optimization Strategy

### Phase 1: Core Tool Compression
**Principles**:
1. Preserve essential functionality
2. Remove redundant explanations
3. Use abbreviations where clear
4. Merge related concepts

### Phase 2: Conditional Loading
**Advanced optimization**:
- Load only relevant tools per task context
- Dynamic tool filtering based on intent classification
- Requires OpenClaw core changes

## Compressed Tool Descriptions

```javascript
const coreToolSummaries = {
    read: "Read file contents",
    write: "Create/overwrite files", 
    edit: "Make precise file edits",
    apply_patch: "Apply multi-file patches",
    grep: "Search file contents",
    find: "Find files by pattern",
    ls: "List directories", 
    exec: "Run shell commands (pty available)",
    process: "Manage background exec sessions",
    web_search: "Search web (Brave API)",
    web_fetch: "Fetch/extract URL content",
    browser: "Control web browser",
    canvas: "Canvas operations",
    nodes: "Node management/camera/screen",
    cron: "Manage cron jobs/reminders",
    message: "Send messages/channel actions", 
    gateway: "Gateway restart/config/updates",
    agents_list: "List spawnable agents",
    sessions_list: "List sessions/sub-agents",
    sessions_history: "Get session history", 
    sessions_send: "Message other sessions",
    sessions_spawn: "Spawn sub-agent",
    session_status: "Show status card (📊 session_status)",
    image: "Analyze image with vision model",
};
```

## Token Savings Calculation

**Before**: 
- Average 12 tokens per description
- 24 core tools = ~288 tokens
- Plus external tools = ~350-400 total tokens for tool descriptions

**After**:
- Average 5 tokens per description  
- 24 core tools = ~120 tokens
- Plus external tools = ~150-180 total tokens

**Estimated Savings**: ~200-250 tokens per turn from core tools alone

## Implementation Plan

### Step 1: Source Code Changes
**File**: `/home/bonsaihorn/Projects/helios/src/agents/system-prompt.ts`
- Locate `coreToolSummaries` object
- Apply compressed descriptions
- Build and test

### Step 2: Validation
- Monitor system prompt token count
- Verify tool functionality preserved
- Check agent understanding of tool purposes

### Step 3: External Tool Optimization
- Apply same compression principles to external tool summaries
- Target skill descriptions and plugin tool descriptions

## Risk Assessment

**Low Risk**:
- Most tool descriptions are self-explanatory from names
- Core functionality preserved in compressed versions
- Easy rollback if issues found

**Potential Issues**:
- Agent might need more clarification on ambiguous tools
- Some domain-specific tools might lose important context

## Success Metrics

- [ ] Token count reduction measured
- [ ] No degradation in tool usage accuracy
- [ ] Successful builds and deployments
- [ ] Agent performance maintained

---
*Next: Implement compressed descriptions in OpenClaw source code*