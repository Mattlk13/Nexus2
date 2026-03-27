# Router Refactoring Implementation Guide

## Problem Statement
The current `/app/backend/routes/hybrid_services.py` file has grown to **1773 lines** with manual routes for 32 hybrid services. This creates:
- **High maintenance burden** - Every new hybrid requires ~50 lines of router code
- **Merge conflict risk** - Multiple developers editing the same massive file
- **Poor scalability** - Cannot easily scale to 100+ hybrids
- **Code duplication** - Similar route patterns repeated 32 times

## Solution: Dynamic Route Loading

### Phase 1: Parallel System (RECOMMENDED - Zero Risk)
Run old and new routers side-by-side:

**Step 1**: Keep existing `/routes/hybrid_services.py` unchanged
**Step 2**: Add new dynamic router as `/routes/dynamic_hybrid_router.py` ✅ DONE
**Step 3**: Mount both routers in `server.py`:
```python
# server.py
from routes.hybrid_services import create_hybrid_router as create_legacy_router
from routes.dynamic_hybrid_router import create_dynamic_hybrid_router

# Legacy router (all 32 hybrids manually defined)
legacy_router = create_legacy_router(db)
app.include_router(legacy_router, prefix="/api/hybrid")

# New dynamic router (auto-discovers hybrids)
dynamic_router, loaded = create_dynamic_hybrid_router(db)
app.include_router(dynamic_router, prefix="/api/v2/hybrid")  # Different prefix!
```

**Benefits**:
- Zero risk - old system continues working
- Test new system at `/api/v2/hybrid/*`
- Gradual migration - move hybrids one-by-one
- Rollback is instant (just remove v2 router)

---

### Phase 2: Hybrid Service Self-Registration

Each hybrid service file gains a `register_routes()` function:

**Before** (Current):
```python
# nexus_hybrid_privacy.py
class PrivacyEngine:
    def __init__(self, db):
        self.db = db
    
    def get_capabilities(self):
        return {"name": "Privacy Hybrid"}
    
    async def scan_secrets(self, repo_url: str):
        return {"found": 5}
```

**After** (Self-Registering):
```python
# nexus_hybrid_privacy.py
from fastapi import APIRouter, Depends

class PrivacyEngine:
    def __init__(self, db):
        self.db = db
    
    def get_capabilities(self):
        return {"name": "Privacy Hybrid"}
    
    async def scan_secrets(self, repo_url: str):
        return {"found": 5}

def register_routes(db, get_current_user, require_admin):
    """Called by dynamic router to get this hybrid's routes"""
    router = APIRouter()
    engine = PrivacyEngine(db)
    
    @router.get("/capabilities")
    async def capabilities():
        return engine.get_capabilities()
    
    @router.post("/scan-secrets")
    async def scan(repo_url: str, user: dict = Depends(get_current_user)):
        return await engine.scan_secrets(repo_url)
    
    return router
```

**Migration Steps**:
1. Pick one hybrid (e.g., `nexus_hybrid_privacy.py`)
2. Add `register_routes()` function to it
3. Test at `/api/v2/hybrid/privacy/capabilities`
4. If works, remove from legacy router
5. Repeat for all 32 hybrids

---

### Phase 3: Complete Migration

Once all 32 hybrids are self-registering:

**Step 1**: Update `server.py`:
```python
from routes.dynamic_hybrid_router import create_dynamic_hybrid_router

dynamic_router, loaded = create_dynamic_hybrid_router(db)
app.include_router(dynamic_router, prefix="/api/hybrid")  # Use original prefix

logger.info(f"✅ Loaded {len(loaded)} hybrid services dynamically")
```

**Step 2**: Archive old router:
```bash
mv /app/backend/routes/hybrid_services.py /app/backend/routes/LEGACY_hybrid_services.py.bak
```

**Step 3**: Celebrate! 🎉
- Router code: 1773 → ~150 lines (91% reduction!)
- Add new hybrid: Create 1 file (not edit 2 files + 50 lines)
- Zero merge conflicts
- Infinite scalability

---

## Implementation Checklist

### ✅ Completed:
- [x] Created `dynamic_hybrid_router.py`
- [x] Created example self-registering hybrid
- [x] Wrote migration documentation

### 🔄 In Progress:
- [ ] None

### ⏳ TODO (Next Agent):
1. [ ] Test dynamic router with 1 hybrid (privacy recommended)
2. [ ] Add `register_routes()` to 1-2 more hybrids
3. [ ] Verify both routers work in parallel
4. [ ] Migrate all 32 hybrids (can be gradual)
5. [ ] Switch to dynamic router only
6. [ ] Delete legacy router file

---

## Estimated Time
- **Testing**: 30 minutes
- **Migrating 5 hybrids**: 1 hour
- **Migrating all 32**: 3-4 hours
- **Total**: 4-5 hours for complete migration

## Risk Level
- **Phase 1 (Parallel)**: 🟢 ZERO RISK
- **Phase 2 (Gradual Migration)**: 🟢 LOW RISK
- **Phase 3 (Complete Switch)**: 🟡 MEDIUM RISK (test thoroughly first)

---

## Benefits Summary
| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| Router Lines | 1773 | ~150 | 91% reduction |
| Files to Edit (New Hybrid) | 2 files | 1 file | 50% less work |
| Lines to Add (New Hybrid) | ~50 lines | ~20 lines | 60% less code |
| Scalability | Limited | Infinite | ♾️ |
| Merge Conflicts | High | None | 100% reduction |

---

## Next Hybrid Addition (With New System)

**Old Way**:
1. Create `/services/nexus_hybrid_example.py` (150 lines)
2. Edit `/services/nexus_ultimate_controller.py` (+3 lines)
3. Edit `/routes/hybrid_services.py` (+1 import, +1 init, +50 lines of routes)
4. Test
5. **Total: 3 files edited, 204 lines added**

**New Way**:
1. Create `/services/nexus_hybrid_example.py` with `register_routes()` (170 lines)
2. Test
3. **Total: 1 file created, 170 lines added, AUTO-DISCOVERED! ✨**

---

## Migration Priority

**High Priority** (Easy wins):
1. `nexus_hybrid_privacy` - 3 endpoints
2. `nexus_hybrid_social_impact` - 3 endpoints
3. `nexus_hybrid_accessibility` - 3 endpoints

**Medium Priority**:
4-20. All other 13 new hybrids (3-5 endpoints each)

**Low Priority** (Complex):
21-32. Original hybrids with many dependencies

**Recommended**: Start with 3 high-priority, test thoroughly, then do the rest in batch.

---

_Created: March 25, 2026_
_Status: Ready for implementation_
_Risk: LOW (parallel system ensures zero downtime)_
