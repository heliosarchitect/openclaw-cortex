# AUGUR Collector Code Consolidation Plan

**Date**: 2026-02-16  
**Task**: Move collector reference into AUGUR repo  
**Status**: Analysis Complete - Ready for Implementation

## Current State Analysis

### 1. Where Collector Code Currently Lives

**Primary Location**: `/home/bonsaihorn/Projects/augur-collector/`
- **Total Files**: 150+ files (including databases, logs, analysis scripts)
- **Repository**: Has its own Git repository with commit history
- **Size**: ~141GB (mostly databases - enhanced_data.db is 141GB)
- **Key collector scripts identified**:
  - `enhanced_collector.py` - Primary comprehensive collector (order books + trades)
  - `orderbook_collector.py` - Basic WebSocket order book collector
  - `orderbook_rest_collector.py` - REST API polling collector 
  - `orderbook_ws_collector.py` - WebSocket order book collector (fixed version)

**Main AUGUR Project**: `/home/bonsaihorn/Projects/augur-trading/`
- **Integration Evidence**: Already contains `enhanced_data.db` (empty, 0 bytes)
- **WebSocket Usage**: Multiple files already use websockets (augur_pipeline.py, augur_v4_scanner.py, paper_augur.py)
- **Repository**: Main trading system with active development

## 2. Files That Need to Move

### Core Collector Scripts (Priority 1)
```
enhanced_collector.py          - 12.8KB - Main multi-pair collector (order books + trades)
orderbook_collector.py         - 4.3KB  - Basic order book WebSocket collector  
orderbook_rest_collector.py    - 2.6KB  - REST polling collector
orderbook_ws_collector.py      - 6.3KB  - Enhanced WebSocket collector
```

### Supporting Infrastructure (Priority 2)  
```
coinbase_advanced_api.py       - 33.4KB - Coinbase Advanced Trade API client
coinbase_auth.py              - 13.0KB - Authentication utilities
coinbase_websocket_api.py     - 19.1KB - WebSocket API wrapper
coinbase_websocket.py         - 16.8KB - Core WebSocket handler
coinbase_rest_ws_example.py   - 9.2KB  - Usage examples
```

### Configuration & Documentation (Priority 3)
```
.env.example                  - 1.9KB  - Environment configuration template
requirements.txt              - 0.8KB  - Python dependencies
README.md                     - 7.5KB  - Documentation
WEBSOCKET_README.md           - 9.5KB  - WebSocket setup guide
COINBASE_API_README.md        - 7.1KB  - API documentation
```

### Databases (Priority 4 - Handle Carefully)
```
enhanced_data.db              - 141GB  - Main data store (HUGE - needs strategy)
orderbook_data.db             - 38MB   - Order book snapshots  
```

**Database Migration Strategy**:
- **DO NOT** move the 141GB enhanced_data.db directly (too large)
- Create fresh database in new location
- Migrate schema/structure only
- Set up data retention policy (retain last 30 days max)
- Archive old data to external storage if needed

## 3. Proposed Directory Structure

```
~/Projects/augur-trading/collector/
├── core/
│   ├── enhanced_collector.py      # Main collector (renamed from enhanced_collector.py)
│   ├── orderbook_collector.py     # Basic WebSocket collector
│   ├── rest_collector.py          # REST polling collector (renamed)
│   └── websocket_collector.py     # Enhanced WS collector (renamed)
├── api/
│   ├── coinbase_client.py         # Advanced API client (renamed)
│   ├── auth.py                    # Authentication (renamed from coinbase_auth.py)
│   ├── websocket_api.py           # WebSocket wrapper (renamed)
│   └── examples/
│       └── usage_examples.py     # Combined examples
├── config/
│   ├── collector_config.py       # Configuration management (new)
│   ├── .env.example             # Environment template
│   └── requirements.txt         # Dependencies
├── data/
│   ├── enhanced_data.db         # Fresh database (empty start)  
│   ├── orderbook_snapshots.db   # Order book data
│   └── README.md                # Data management guide
├── docs/
│   ├── README.md                # Main documentation
│   ├── websocket_setup.md       # WebSocket guide
│   ├── api_reference.md         # API documentation  
│   └── deployment.md            # Deployment guide
├── scripts/
│   ├── start_collector.py       # Startup script (new)
│   ├── data_cleanup.py          # Data retention (new)
│   └── health_check.py          # Monitoring (new)
└── tests/
    ├── test_collector.py        # Unit tests (new)
    ├── test_websocket.py        # WebSocket tests (new)
    └── test_api.py              # API tests (new)
```

## 4. Migration Implementation Plan

### Phase 1: Setup (30 minutes)
1. Create directory structure in `~/Projects/augur-trading/collector/`
2. Initialize Git submodule or merge strategy
3. Copy core collector scripts with renamed files
4. Update import paths and references

### Phase 2: Integration (45 minutes)  
1. Move API client code and authentication
2. Create unified configuration system
3. Update database paths to use new location
4. Test basic collector functionality

### Phase 3: Documentation & Testing (30 minutes)
1. Consolidate and update documentation
2. Create startup/deployment scripts
3. Add health monitoring
4. Implement data retention policies

### Phase 4: Data Migration (Variable - depends on needs)
1. Export recent data from old enhanced_data.db (last 7 days)
2. Import into new database location
3. Set up automated cleanup to prevent 141GB accumulation
4. Archive or delete old collector directory after verification

## 5. Integration Points

### Existing AUGUR Code That Uses WebSockets:
- `augur_pipeline.py` - Line 245: WebSocket connection to Coinbase
- `augur_v4_scanner.py` - Uses Coinbase WebSocket for scanning
- `paper_augur.py` - WebSocket integration for paper trading

### Consolidation Opportunities:
- **Unified WebSocket client**: Replace individual WebSocket implementations
- **Shared authentication**: Centralize Coinbase API authentication 
- **Common data schemas**: Standardize data storage across AUGUR modules
- **Centralized configuration**: Single source for API keys, pairs, settings

## 6. Benefits of Consolidation

1. **Single Source of Truth**: All collector code in one location
2. **Shared Infrastructure**: Reuse authentication, WebSocket handling, etc.
3. **Easier Maintenance**: Updates and improvements in one place
4. **Better Integration**: Tighter coupling with AUGUR trading logic
5. **Reduced Duplication**: Eliminate redundant WebSocket implementations
6. **Improved Testing**: Centralized test suite for data collection
7. **Cleaner Architecture**: Clear separation between collection and analysis

## 7. Risks & Mitigation

**Risk**: Breaking existing functionality
- **Mitigation**: Maintain backward compatibility, thorough testing

**Risk**: Database migration complexity
- **Mitigation**: Start fresh, implement retention policy from day 1

**Risk**: Import path changes  
- **Mitigation**: Update all references, use relative imports

**Risk**: Configuration drift
- **Mitigation**: Create centralized config management

## 8. Post-Migration Tasks

1. Update all AUGUR modules to use centralized collector
2. Remove redundant WebSocket code from other modules
3. Set up monitoring and alerting for data collection
4. Create backup/recovery procedures
5. Document new architecture for team
6. Archive old augur-collector directory

## 9. Timeline Estimate

- **Immediate (1-2 hours)**: Core file migration and basic integration
- **Short-term (1 day)**: Full testing and documentation  
- **Medium-term (1 week)**: Legacy cleanup and optimization
- **Long-term (ongoing)**: Monitoring and maintenance

## Next Steps

1. ✅ **COMPLETED**: Analysis and planning
2. **NEXT**: Execute Phase 1 (directory setup and core file moves)
3. **THEN**: Test integration with existing AUGUR systems
4. **FINALLY**: Update LBF task status and notify completion

---

**Analysis completed**: 2026-02-16 19:48 EST  
**Ready for implementation**: Core collector scripts identified and migration plan finalized