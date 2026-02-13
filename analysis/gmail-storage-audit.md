# Gmail & Drive Storage Audit — bonsaihorn@gmail.com
<!-- AI.TOC: Gmail & Drive Storage Audit — bonsaihorn@gmail.com — Read lines 1-20 for navigation.
  §1 Executive Summary                          → lines 7-21
  §2 DRIVE AUDIT                                → lines 22-81
  §3 GMAIL AUDIT                                → lines 82-153
  §4 Recommended Cleanup Actions (ordered by    → lines 154-170
  §5 Estimated Total Recoverable Storage        → lines 171-180
  §6 Key Observations                           → lines 181-191
  Total: 191 lines | Sections: 6
-->
**Date:** 2026-02-09  
**Status:** READ-ONLY audit. Nothing modified or deleted.

---

## Executive Summary

| Area | Estimated Storage | Notes |
|------|------------------|-------|
| **Google Drive** | ~450 MB | 1 massive audio file (282 MB) dominates |
| **Gmail (attachments >5M)** | ~500 MB–1 GB | 103 threads with large attachments |
| **Gmail (bulk/promotions)** | Moderate | 500+ promotion threads (paginated — likely 1,000+) |
| **Spam** | Unknown (200+ threads) | Should be auto-purged but isn't fully clear |
| **Trash** | **Empty** ✅ | No threads in trash |

**Biggest win: Drive cleanup of 1 audio file = ~282 MB freed instantly.**  
**Second biggest win: Bulk-deleting promotional/Black Friday emails = hundreds of threads cleared.**

---

## DRIVE AUDIT

### Top 20 Largest Files (sorted by size)

| # | File | Size | Type | Modified | Notes |
|---|------|------|------|----------|-------|
| 1 | `motor_reconnection.wav` | **282.6 MB** | Audio (WAV) | 2025-12-21 | ⚠️ MASSIVE — single biggest storage hog |
| 2 | `20150520_165247.jpg` (Phone pics) | 5.2 MB | JPEG | 2016-03-10 | Old phone photo |
| 3 | `20160209_150838.jpg` (Phone pics) | 5.3 MB | JPEG | 2016-03-10 | Old phone photo |
| 4 | `20160201_082536.jpg` (Phone pics) | 5.3 MB | JPEG | 2016-03-10 | Old phone photo |
| 5 | `20151229_182146.jpg` (Phone pics) | 5.5 MB | JPEG | 2016-03-10 | Old phone photo |
| 6 | `20160107_202510.jpg` (Phone pics) | 5.1 MB | JPEG | 2016-03-10 | Old phone photo |
| 7 | `20160102_140032.jpg` (Phone pics) | 5.4 MB | JPEG | 2016-03-10 | Old phone photo |
| 8 | `20160224_062853.jpg` (Phone pics) | 5.3 MB | JPEG | 2016-03-10 | Old phone photo |
| 9 | `20160205_114211.jpg` (Phone pics) | 5.1 MB | JPEG | 2016-03-10 | Old phone photo |
| 10 | `20150812_104150.jpg` (Phone pics) | 5.1 MB | JPEG | 2016-03-10 | Old phone photo |
| 11 | `20151221_123809.jpg` (Phone pics) | 5.1 MB | JPEG | 2016-03-10 | Old phone photo |
| 12 | `20150813_121620.jpg` (Phone pics) | 5.4 MB | JPEG | 2016-03-10 | Old phone photo |
| 13 | `20150518_124214.jpg` (Phone pics) | 5.0 MB | JPEG | 2016-03-10 | Old phone photo |
| 14 | `20150522_120005.jpg` (Phone pics) | 5.3 MB | JPEG | 2016-03-10 | Old phone photo |
| 15 | `20160301_162710.jpg` (Phone pics) | 5.0 MB | JPEG | 2016-03-10 | Old phone photo |
| 16 | `20150828_103509.jpg` (Phone pics) | 5.0 MB | JPEG | 2016-03-10 | Old phone photo |
| 17 | `DJI_0031.JPG` | 4.8 MB | JPEG | 2021-05-09 | Drone photo |
| 18 | `Horn, Matthew - 38 USC 5103 Response.pdf` | 4.1 MB | PDF | 2000-05-20 | VA legal document ⚠️ |
| 19 | `20200211_210046.jpg` | 3.8 MB | JPEG | 2021-01-27 | Photo |
| 20 | `20150813_193911.jpg` (Phone pics) | 3.7 MB | JPEG | 2016-03-10 | Old phone photo |

### Phone Pics Folder
- **50 JPEG photos** from 2015-2016, totaling **~160 MB**
- All uploaded on 2016-03-10 (batch upload)
- Has **more pages** (paginated) — likely 100+ photos total

### Duplicate Files Found

| File Name | Count | Size Each | Total Waste |
|-----------|-------|-----------|-------------|
| `202508081804.pdf` | **2 copies** (1 as PDF, 1 as ZIP — same 1.18 MB) | 1.18 MB | ~1.18 MB |
| `CoinbaseWalletBackups` (folder) | **2 identical folders** | Unknown | Possible duplicate content |

### Untitled/Junk Documents
- **4× "Untitled document"** (Google Docs, 2018-2023) — likely scratch notes
- **3× "Untitled spreadsheet"** (Google Sheets, 2016-2020) — likely scratch
- These don't count against storage (Google Workspace files are "free" in storage)

### Drive Categories

| Category | Files | Est. Size | Notes |
|----------|-------|-----------|-------|
| **Audio** | 1 | 282.6 MB | `motor_reconnection.wav` — dominates storage |
| **Phone pics (old)** | 50+ | ~160 MB+ | 2015-2016, backed up in batch |
| **Personal photos** | 5 | ~17 MB | DJI drone, screenshots, etc. |
| **Legal/VA documents** | 3 | ~6.4 MB | VA 4138, 5103 Response, Notice of Disagreement |
| **PDFs (misc)** | 4 | ~4.5 MB | Chainsaw manual, order receipts, etc. |
| **Office docs** | 4 | ~0.4 MB | Resume, exam, spreadsheets |
| **3D printing** | 1 | 0.1 MB | STL file |
| **Takeout backup** | 1 | 2.3 MB | Classic Sites backup |
| **Config/data** | 3 | ~0.06 MB | JSON, TXT files |

---

## GMAIL AUDIT

### Large Emails (has:attachment larger:5M)
- **103 threads** with attachments over 5MB
- Mostly self-sent photos/videos and personal correspondence
- Notable senders: Matthew to self (photos, videos, scans), JT, Robert Tiller, Chris Bowlds
- Spans 2017-2024 — many are "email as file transfer" from before cloud sharing was common

### Bulk Email Categories Safe to Delete

#### 1. 🏷️ Promotions (category:promotions)
- **500+ threads** (paginated — estimated **1,000-2,000+ total**)
- ALL UNREAD — Matthew does not engage with these
- Top senders seen in sample:
  - Tuckernuck, Concealed Carry, Tiffany & Co., Swanson, Newegg
  - Eden Brothers, Michaels, Bon Charge, Baker Creek Seeds
  - Ruby Tuesday, Death Wish Coffee, Liquid I.V., Ty Ty Nursery
  - Palmetto State Armory, Weldmonger, Experian, Truth Social
  - Total Wine, Panda Drum, Proflowers, Fast-Growing-Trees
  - Dollar General, Cigars International, Mann Lake, BJ's
  - Uncle Jim's Worm Farm, Beretta USA, Rumble
- **Verdict: SAFE TO BULK DELETE** — all promotional, all unread

#### 2. 🖤 Black Friday / Cyber Monday
- **69 threads** with "Black Friday" or "Cyber Monday" in subject
- Date range: primarily Nov 25 – Dec 3, 2025
- ALL UNREAD
- Senders: Trump Merch (×6!), Panda Drum (×6), Mann Lake, Uncle Jim's Worm Farm, Newegg, Chewy, Palmetto State Armory, Joovv, ByteByteGo, etc.
- **Verdict: SAFE TO BULK DELETE** — expired promotions, all unread

#### 3. 🐙 GitHub Notifications
- **130 threads** total
- Most are auto-notifications for repos Matthew watches/forked:
  - `JonathanFly/bark` — 15+ issue notifications (never responded)
  - `muellerberndt/mini-agi` — 6+ issue notifications (never responded)
  - `linuxmint/linuxmint` — Fastly Repository issue #658 (100+ messages per thread!)
  - `bonsaihorn/guicreators` — **15 CI failure notifications** from 2024-05-17 (all from same day)
  - Security advisories for bonsaihorn repos (aiohttp, torch, transformers, jupyterlab)
  - Spam issues (discord invite spam, fake security vulnerabilities)
- **Verdict: SAFE TO BULK DELETE** — auto-notifications, not active participation. Consider unsubscribing from watched repos too.

#### 4. 📬 groups.io (TheRheumatoidFactor)
- **500+ threads** (paginated — estimated **800-1,500+ total**)
- Group: **TheRheumatoidFactor** — a rheumatoid arthritis support group
- Content breakdown:
  - ~60% automated calendar notifications (birthday reminders, holiday notices, guidelines)
  - ~30% posts from "Gilly Gmail" (most active poster)
  - ~10% other members (Shannon, Kitty, Lanie)
- **Matthew's participation:** `to:groups.io` returned 50 threads BUT these appear to be reply-tos from the group, not messages Matthew actually sent. No evidence of Matthew posting to the group — he appears to be a passive subscriber.
- **Verdict: MOSTLY SAFE TO DELETE** — calendar/birthday notifications are definitely deletable. Group posts could be kept if Matthew wants to read them, but he appears not to engage. Consider unsubscribing from the group entirely if he doesn't use it.

#### 5. 🇺🇸 Trump Campaign Emails
- **100+ threads** (paginated)
- Multiple per day during campaign/holiday periods
- Subjects: "Special Black Friday Deal" (×6 during one week!), "Halftime Update from your favorite President", "Trump Platinum Club"
- **Verdict: SAFE TO BULK DELETE** — political fundraising spam

#### 6. 📰 Substack Newsletters
- **100+ threads** (paginated)
- Including ByteByteGo and others
- **Verdict: Review individually** — some may have value (ByteByteGo = tech content)

#### 7. 🗑️ Spam
- **200+ threads** (paginated — likely more)
- Mix of: Polish Pottery, Mann Lake, Nexo crypto airdrop scams, Mopar warranty scams, Gateway Pundit sponsors, etc.
- **Verdict: SAFE TO PURGE ALL** — it's spam

### Trash
- **Empty** ✅ — nothing to clean here

---

## Recommended Cleanup Actions (ordered by impact)

| Priority | Action | Est. Freed | Difficulty |
|----------|--------|-----------|------------|
| 🥇 **1** | **Delete `motor_reconnection.wav`** from Drive (or download locally first) | **~283 MB** | Easy — single file |
| 🥈 **2** | **Purge all spam** (200+ threads) | **~50-200 MB** | Easy — bulk action |
| 🥉 **3** | **Delete all Promotions** (1,000+ threads, all unread) | **~100-500 MB** | Medium — bulk by label |
| **4** | **Delete Black Friday emails** (69 threads) | **~5-20 MB** | Easy — search + delete |
| **5** | **Delete GitHub notifications** (130 threads, incl. 15 duplicate CI failures) | **~10-30 MB** | Easy — search + delete |
| **6** | **Delete groups.io calendar/birthday notifications** (~300+ threads) | **~10-30 MB** | Medium — need to filter |
| **7** | **Review & delete Phone pics folder** (160+ MB of 2015-2016 photos) | **~160 MB** | Medium — review first, may have sentimental value |
| **8** | **Delete duplicate `202508081804.pdf`** (keep one copy) | **~1.2 MB** | Easy |
| **9** | **Delete Trump campaign emails** (100+ threads) | **~10-30 MB** | Easy — search + delete |
| **10** | **Unsubscribe from unused mailing lists** | Prevents future buildup | Ongoing |

---

## Estimated Total Recoverable Storage

| Category | Conservative | Aggressive |
|----------|-------------|------------|
| Drive cleanup | ~284 MB | ~445 MB (incl. phone pics) |
| Gmail cleanup | ~200 MB | ~800 MB |
| **Total** | **~484 MB** | **~1.2 GB** |

---

## Key Observations

1. **Drive is relatively clean** — only ~450 MB used total. The single WAV file is 63% of all Drive storage.
2. **Gmail is the real problem** — thousands of unread promotional emails accumulating since ~2017.
3. **Matthew doesn't read promotional email** — every single promotion thread was marked UNREAD.
4. **Email-as-file-transfer pattern** — many of the large attachment emails (2017-2022) are Matthew emailing photos/files to himself or family. These could be archived locally.
5. **groups.io is high-volume, low-value** — birthday reminders for people in a support group Matthew doesn't actively participate in.
6. **Two duplicate CoinbaseWalletBackups folders** — should verify contents and delete one.
7. **No active trash** — good hygiene there.
8. **Trump campaign sends 3-6 emails per day during events** — consider unsubscribing.
