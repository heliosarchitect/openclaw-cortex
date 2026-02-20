# Helios Channel Plugins - readStringParam Duplication Analysis

## Executive Summary

After analyzing all readStringParam() usage across Helios channel plugins, I found **no actual duplication of the readStringParam function implementation**. All plugins correctly import the shared utility from `src/agents/tools/common.ts`. However, there are **repetitive parameter extraction patterns** that could be abstracted into shared utilities.

## Files Containing readStringParam Usage

### 1. Core Implementation
- **File**: `src/agents/tools/common.ts` (lines 42-66)
- **Status**: ✅ **Single source of truth** - properly implemented with TypeScript overloads
- **Exports**: Available via plugin-sdk index

### 2. Channel Plugin Files
1. **`src/channels/plugins/slack.actions.ts`**
   - **Import**: `from "../../agents/tools/common.js"`
   - **Usage**: Standard parameter extraction for send, react, edit, delete actions
   - **Lines**: 17, 21-28, 44, 47, 63, 96, 99, 113, 145

2. **`src/channels/plugins/actions/discord/handle-action.ts`**
   - **Import**: `from "../../../../agents/tools/common.js"`
   - **Usage**: Standard parameters + custom `readParentIdParam` helper
   - **Lines**: 21, 28, 32, 36, 43, 49-58, 80-81, 105-106, etc.

3. **`src/channels/plugins/actions/discord/handle-action.guild-admin.ts`**
   - **Import**: `from "../../../../agents/tools/common.js"`
   - **Usage**: Guild administration parameters
   - **Lines**: 22-23, 33, 43, 53, 56-57, 76, 79, 82, 85, 88, etc.

4. **`src/channels/plugins/actions/telegram.ts`**
   - **Import**: `from "../../../agents/tools/common.js"`
   - **Usage**: Standard parameters + custom `readTelegramSendParams` helper
   - **Lines**: 16-22, 26, 105, 113, 127, 147, 152, 169, 172, 189

5. **`src/channels/plugins/actions/signal.ts`**
   - **Import**: `from "../../../agents/tools/common.js"`
   - **Usage**: Signal-specific reaction parameters
   - **Lines**: 91-92, 101, 105-106, 111

## Differences Between Implementations

### ✅ No Function Duplication
All files import `readStringParam` from the shared `common.ts` module. **No duplicate implementations found.**

### 🔄 Repetitive Parameter Patterns
However, there are **repetitive parameter extraction patterns** across plugins:

#### Common Send Message Parameters
```typescript
// Pattern repeated in Slack, Discord, Telegram
const to = readStringParam(params, "to", { required: true });
const content = readStringParam(params, "message", { required: true, allowEmpty: true });
const mediaUrl = readStringParam(params, "media", { trim: false });
const threadId = readStringParam(params, "threadId");
const replyTo = readStringParam(params, "replyTo");
```

#### Message Action Parameters  
```typescript
// Pattern repeated across plugins
const messageId = readStringParam(params, "messageId", { required: true });
const emoji = readStringParam(params, "emoji", { allowEmpty: true });
```

#### Guild/Server Admin Parameters (Discord)
```typescript
// Repeated in Discord guild actions
const guildId = readStringParam(params, "guildId", { required: true });
const userId = readStringParam(params, "userId", { required: true });
```

## Existing Helper Functions

### 1. `readTelegramSendParams()` (telegram.ts:15)
```typescript
function readTelegramSendParams(params: Record<string, unknown>) {
  const to = readStringParam(params, "to", { required: true });
  const mediaUrl = readStringParam(params, "media", { trim: false });
  const message = readStringParam(params, "message", { required: !mediaUrl, allowEmpty: true });
  const caption = readStringParam(params, "caption", { allowEmpty: true });
  const content = message || caption || "";
  const replyTo = readStringParam(params, "replyTo");
  const threadId = readStringParam(params, "threadId");
  // ... returns normalized params object
}
```

### 2. `readParentIdParam()` (discord/handle-action.ts:14)
```typescript
function readParentIdParam(params: Record<string, unknown>): string | null | undefined {
  if (params.clearParent === true) return null;
  if (params.parentId === null) return null;
  return readStringParam(params, "parentId");
}
```

## Proposed Shared Utility Location

### Recommended: `src/channels/plugins/common-params.ts`

Create a new shared utility module for channel plugins:

```typescript
// src/channels/plugins/common-params.ts
import { readStringParam, readStringArrayParam } from "../../agents/tools/common.js";

export interface StandardSendParams {
  to: string;
  content?: string;
  mediaUrl?: string;
  threadId?: string;
  replyTo?: string;
  filename?: string;
}

export interface MessageActionParams {
  messageId: string;
  emoji?: string;
}

export interface GuildAdminParams {
  guildId: string;
  userId?: string;
  channelId?: string;
}

export function readStandardSendParams(params: Record<string, unknown>): StandardSendParams {
  return {
    to: readStringParam(params, "to", { required: true }),
    content: readStringParam(params, "message", { allowEmpty: true }),
    mediaUrl: readStringParam(params, "media", { trim: false }),
    threadId: readStringParam(params, "threadId"),
    replyTo: readStringParam(params, "replyTo"),
    filename: readStringParam(params, "filename"),
  };
}

export function readMessageActionParams(params: Record<string, unknown>): MessageActionParams {
  return {
    messageId: readStringParam(params, "messageId", { required: true }),
    emoji: readStringParam(params, "emoji", { allowEmpty: true }),
  };
}

export function readGuildAdminParams(params: Record<string, unknown>): GuildAdminParams {
  return {
    guildId: readStringParam(params, "guildId", { required: true }),
    userId: readStringParam(params, "userId"),
    channelId: readStringParam(params, "channelId"),
  };
}
```

## Refactoring Steps

### Phase 1: Create Shared Utility ✅ SAFE
1. Create `src/channels/plugins/common-params.ts` with shared parameter readers
2. Add comprehensive TypeScript types
3. Include JSDoc documentation
4. Add unit tests

### Phase 2: Update Imports (Low Risk)
1. Update each channel plugin to import shared utilities
2. Replace repetitive parameter extraction with shared functions
3. Update import paths to use shared utilities

### Phase 3: Gradual Migration (Safe)
1. **Slack Plugin**: Replace standard patterns with `readStandardSendParams`
2. **Discord Plugin**: Replace with `readStandardSendParams` + `readMessageActionParams` + `readGuildAdminParams`
3. **Telegram Plugin**: Enhance `readTelegramSendParams` to extend `readStandardSendParams`
4. **Signal Plugin**: Replace with `readMessageActionParams`

### Phase 4: Cleanup (Safe)
1. Remove local helper functions (`readTelegramSendParams`, `readParentIdParam`) 
2. Migrate to shared utilities
3. Update tests

## Implementation Safety Assessment

### ✅ SAFE TO PROCEED
- **No breaking changes**: Shared utilities would be additive
- **Gradual migration**: Can be done incrementally, file by file
- **Type safety**: TypeScript ensures parameter compatibility
- **Backwards compatible**: Existing imports continue to work
- **Well-tested foundation**: `readStringParam` is extensively used and tested

### Estimated Impact
- **Files affected**: 5 channel plugin files
- **Lines reduced**: ~50-80 lines of repetitive parameter extraction
- **Maintainability**: ⬆️ Significantly improved
- **Type safety**: ⬆️ Enhanced with proper interfaces
- **Testing**: ✅ Easier to test shared utilities

## Recommendation

**PROCEED with refactoring** - This is a low-risk, high-value improvement that will:
1. Eliminate 50+ lines of repetitive parameter extraction code
2. Improve maintainability and type safety  
3. Create a consistent pattern for future channel plugins
4. Maintain full backwards compatibility

The refactoring should be done incrementally, starting with the shared utility creation and gradually migrating each plugin.