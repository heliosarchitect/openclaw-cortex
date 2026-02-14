# WEMS MCP Registry & Awesome-MCP-Servers Submission Guide

## Phase 1: Package Configuration Update

1. **Update pyproject.toml** - Add the MCP name field:
   ```toml
   [project]
   # ... existing fields ...
   mcpName = "io.github.heliosarchitect/wems"
   ```

2. **Republish to PyPI** with updated metadata:
   ```bash
   python -m build
   python -m twine upload dist/*
   ```

## Phase 2: MCP Registry Submission

### Prerequisites Met ✅
- Python package: ✅ wems-mcp-server published on PyPI
- GitHub repo: ✅ heliosarchitect/wems-mcp-server 
- GitHub account: ✅ heliosarchitect

### Steps to Submit:

1. **Install mcp-publisher**:
   ```bash
   # macOS/Linux
   curl -L "https://github.com/modelcontextprotocol/registry/releases/latest/download/mcp-publisher_$(uname -s | tr '[:upper:]' '[:lower:]')_$(uname -m | sed 's/x86_64/amd64/;s/aarch64/arm64/').tar.gz" | tar xz mcp-publisher && sudo mv mcp-publisher /usr/local/bin/
   
   # Or via Homebrew
   brew install mcp-publisher
   ```

2. **Create server.json** (file already created: `wems-server.json`):
   - Copy the provided `wems-server.json` to your WEMS project directory
   - Rename it to `server.json`

3. **Authenticate with MCP Registry**:
   ```bash
   mcp-publisher login github
   ```
   - Follow the device code flow
   - Authorize the application on GitHub

4. **Publish to MCP Registry**:
   ```bash
   mcp-publisher publish
   ```

## Phase 3: Awesome-MCP-Servers PR

### Target Repository: wong2/awesome-mcp-servers

1. **Fork the repository**:
   - Go to: https://github.com/wong2/awesome-mcp-servers
   - Click "Fork"

2. **Add WEMS entry**:
   - Edit the README.md file
   - Find the appropriate category (likely "Monitoring" or "Environment & Nature")
   - Add the prepared entry (see `awesome-mcp-servers-entry.md`)

3. **Create Pull Request**:
   - Title: "Add WEMS - World Event Monitoring System"
   - Description: 
     ```
     Adding WEMS (World Event Monitoring System) - a real-time natural hazard monitoring MCP server.
     
     **Key Features:**
     - Real-time monitoring of earthquakes, tsunamis, volcanoes, and solar events
     - Free tier (earthquakes ≥4.5 magnitude) and Premium tier ($29/mo) with full access
     - Data from authoritative sources: USGS, NOAA, Smithsonian GVP
     - Zero-configuration setup with webhook alerts
     - Published on PyPI: https://pypi.org/project/wems-mcp-server/
     - GitHub: https://github.com/heliosarchitect/wems-mcp-server
     
     This adds value to the MCP ecosystem by providing access to critical real-time natural hazard data with a freemium model that makes basic monitoring accessible to all users.
     ```

## Phase 4: Marketing Amplification (Optional)

1. **Tweet announcement** highlighting the freemium model
2. **LinkedIn post** targeting enterprise risk management audience  
3. **Reddit post** in r/MachineLearning or relevant communities
4. **Discord announcements** in MCP/AI communities

## Expected Timeline

- **Phase 1**: 1-2 hours (package update + republish)
- **Phase 2**: 30 minutes (registry submission)
- **Phase 3**: 30 minutes (awesome-mcp-servers PR)
- **Total**: ~3 hours end-to-end

## Success Metrics

- ✅ Package appears in MCP Registry search
- ✅ PR merged in awesome-mcp-servers
- ✅ Increased PyPI downloads
- ✅ GitHub stars/forks growth

## Notes

- The freemium model is highlighted in both submissions to differentiate WEMS
- Geographic filtering and webhook capabilities are key selling points
- Enterprise risk management is a high-value use case to emphasize