# Competitor Analysis Agent - Setup Instructions

## Issues Found & Solutions

### 1. ✅ Fixed: JSON Parsing Error
The agent was failing to parse results because of markdown code blocks. This has been fixed in `crew.py`.

### 2. ⚠️ Action Required: Configure Real Competitors

**Current Status:** Your `.env` file has placeholder values:
- `COMPETITORS=competitor1,competitor2,competitor3`
- `KEYWORDS=keyword1,keyword2,keyword3`

**To Fix:**
1. Open the `.env` file in this directory
2. Replace with real competitor names (comma-separated, no spaces):
   ```
   COMPETITORS=OpenAI,Anthropic,Google DeepMind,Mistral AI
   ```
3. Replace with real keywords:
   ```
   KEYWORDS=AI agents,LLM,generative AI,GPT,large language models
   ```
4. Save the file

### 3. ⚠️ Action Required: Verify Slack Channel ID

**Current Status:** Your Slack Channel ID is set to `0ja8732` which seems incorrect.

**To Fix:**
1. Open Slack
2. Right-click on the channel where you want reports
3. Click "View channel details" or "Channel settings"
4. Scroll down to find the "Channel ID" (it's usually a longer string like `C01234ABCDE`)
5. Update `.env` file:
   ```
   SLACK_CHANNEL_ID=C01234ABCDE
   ```

**Note:** The Slack bot token looks correct (starts with `xapp-`).

### 4. ✅ Fixed: Better Terminal Output

The agent now displays results more clearly. You'll see:
- Summary of items found
- Detailed list of findings with priority levels
- URLs and sources

## How to Use

### 1. Configure Competitors
```bash
python3 configure_competitors.py
```
This shows your current configuration and instructions.

### 2. Run the Agent
```bash
python3 crew.py
```
This will:
- Search for information about your competitors
- Analyze findings
- Store results in the database
- Send high-priority alerts to Slack (if configured correctly)

### 3. View Stored Results
```bash
python3 view_results.py
```
This displays all intelligence items stored in the database.

### 4. Test Slack Integration
```bash
python3 configure_competitors.py test-slack
```
This sends a test message to verify Slack is working.

## Expected Output

When you run `python3 crew.py`, you should see:

```
🔍 Starting competitive intelligence gathering...
[Agent activity logs...]
✅ Intelligence gathering complete!
💾 Processing and storing results...
✅ Stored X intelligence items
🔴 Found Y high-priority items
📢 Sending immediate alerts for high-priority items...

======================================================================
📊 INTELLIGENCE GATHERING SUMMARY
======================================================================
✅ Total items found: X
🔴 High priority items: Y

📋 DETAILED FINDINGS:
----------------------------------------------------------------------
1. 🔴 [High] CompetitorName
   Title: Finding Title
   URL: https://...
...
======================================================================
```

## Troubleshooting

### No Slack Messages?
1. Check Slack Channel ID is correct (see above)
2. Verify bot has permission to post in the channel
3. Test with: `python3 configure_competitors.py test-slack`

### No Results Found?
1. Make sure competitors are real company names (not placeholders)
2. Check that SerpAPI key is valid
3. Try running again (API rate limits may apply)

### SSL Certificate Error?
This is a system-level issue. The agent will still work, but Slack messages might fail. You can:
- View results using `python3 view_results.py`
- Check the database directly at `./data/intelligence.db`

## Next Steps

1. **Update `.env` with real competitors** (most important!)
2. **Verify Slack Channel ID**
3. **Run the agent**: `python3 crew.py`
4. **Check results**: `python3 view_results.py`
5. **Set up automated runs**: Use `scheduler.py` for daily/weekly reports

