"""
NEXUS Hybrid: Semi-Formal Code Review
Meta's structured prompting technique for AI code review with 93% accuracy

Based on: Meta Research - Semi-Formal Reasoning for LLM Code Analysis
Features: Patch equivalence, fault localization, code question answering
Accuracy: 93% (vs 78% standard reasoning)
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, List, Any
import os
import logging
from dotenv import load_dotenv
from emergentintegrations.llm.chat import LlmChat, UserMessage

load_dotenv()
logger = logging.getLogger(__name__)

class CodeReviewRequest(BaseModel):
    code: str
    task: str  # "patch_equivalence", "fault_localization", "code_qa"
    context: Optional[Dict[str, Any]] = None
    patch_a: Optional[str] = None
    patch_b: Optional[str] = None
    bug_description: Optional[str] = None
    question: Optional[str] = None

class SemiFormalCodeReviewEngine:
    def __init__(self, db):
        self.db = db
        self.api_key = os.getenv('EMERGENT_LLM_KEY')
        
        # Semi-formal reasoning templates from Meta research
        self.templates = {
            "patch_equivalence": """# SEMI-FORMAL PATCH EQUIVALENCE VERIFICATION

## Task
Determine if Patch A and Patch B produce identical test outcomes WITHOUT executing code.

## Required Certificate Format

### 1. PREMISES (Must explicitly state)
- Test specification: [describe test inputs/outputs]
- Patch A changes: [list exact changes]
- Patch B changes: [list exact changes]
- Relevant context: [imported modules, dependencies]

### 2. EXECUTION TRACE (Must trace step-by-step)
For each test case:
  a) Trace Patch A execution:
     - Function calls in order
     - Variable states at each step
     - Return values
  b) Trace Patch B execution:
     - Function calls in order
     - Variable states at each step
     - Return values

### 3. EDGE CASES (Must check)
- Function name shadowing
- Module-level vs built-in functions
- Type coercions
- Error handling differences

### 4. FORMAL CONCLUSION (Must derive from evidence)
Based ONLY on traced execution:
- Are outputs identical? [YES/NO]
- Confidence: [0-100%]
- Evidence: [cite specific trace steps]

CRITICAL: Do NOT guess based on function names. TRACE actual execution paths.""",

            "fault_localization": """# SEMI-FORMAL FAULT LOCALIZATION

## Task
Pinpoint EXACT lines of code causing the bug.

## Required Certificate Format

### 1. PREMISES
- Bug description: [symptoms, error messages]
- Expected behavior: [what should happen]
- Actual behavior: [what does happen]
- Relevant files: [list all involved files]

### 2. EXECUTION TRACE TO ERROR
Starting from entry point, trace execution:
  Step 1: [function call, file:line]
    - Input values: [list]
    - Local variables: [list]
  Step 2: [next call]
    ...
  Step N: [where error occurs]
    - Why it fails: [explain]

### 3. ROOT CAUSE ANALYSIS
- Faulty assumption: [what code assumes incorrectly]
- Edge case missed: [what scenario wasn't handled]
- Exact line numbers: [file:line]

### 4. FORMAL CONCLUSION
- Root cause: [single sentence]
- Fix required: [describe change needed]
- Confidence: [0-100%]

CRITICAL: Follow ACTUAL execution paths, not guessed behavior.""",

            "code_qa": """# SEMI-FORMAL CODE QUESTION ANSWERING

## Task
Answer question about codebase with rigorous evidence.

## Required Certificate Format

### 1. PREMISES
- Question: [restate question]
- Relevant files: [list files to analyze]
- Key functions/classes: [list]

### 2. CODE INVESTIGATION
For each relevant code section:
  a) Location: [file:line]
  b) Purpose: [what it does]
  c) Dependencies: [what it calls/uses]
  d) Evidence gathering:
     - Trace 3-5 concrete examples
     - Document actual behavior
     - Note edge cases

### 3. SYNTHESIS
- Combine evidence from all sections
- Check for contradictions
- Identify gaps in understanding

### 4. FORMAL CONCLUSION
- Answer: [direct answer to question]
- Evidence chain: [cite specific code locations]
- Caveats: [what's assumed/unknown]
- Confidence: [0-100%]

CRITICAL: Answer based ONLY on traced code, not documentation."""
        }
    
    def get_capabilities(self) -> Dict:
        return {
            "name": "Semi-Formal Code Review",
            "description": "Meta's structured prompting technique for accurate code analysis",
            "category": "code_analysis",
            "provider": "Meta Research + GPT-5.1",
            "accuracy": "93% (vs 78% standard reasoning)",
            "features": [
                "Patch Equivalence Verification",
                "Fault Localization (Bug Detection)",
                "Code Question Answering",
                "Structured Reasoning Templates",
                "Execution-Free Analysis",
                "No Sandbox Required"
            ],
            "advantages": [
                "2.8x more thorough than standard reasoning",
                "Reduces hallucinations via structured evidence",
                "Handles edge cases (function shadowing, etc.)",
                "Works across languages and frameworks",
                "No code execution needed"
            ],
            "tradeoffs": [
                "2.8x more API calls/tokens",
                "Higher latency due to structured analysis",
                "Can produce confident wrong answers if investigation incomplete",
                "Limited by codebase boundaries (3rd party libs)"
            ],
            "use_cases": [
                "Code Review Automation",
                "Patch Verification before merge",
                "Bug Detection in CI/CD",
                "Security Vulnerability Analysis",
                "Code Quality Assurance"
            ],
            "status": "active",
            "version": "1.0.0"
        }
    
    async def review_code(self, request: CodeReviewRequest) -> Dict:
        """Perform semi-formal code review"""
        try:
            # Select appropriate template
            template = self.templates.get(request.task)
            if not template:
                raise HTTPException(status_code=400, detail=f"Unknown task: {request.task}")
            
            # Build prompt based on task
            if request.task == "patch_equivalence":
                user_prompt = f"""{template}

## YOUR TASK

**Patch A:**
```
{request.patch_a}
```

**Patch B:**
```
{request.patch_b}
```

**Context:**
{request.context or "No additional context provided"}

Now fill out the certificate following the exact structure above. Be rigorous."""

            elif request.task == "fault_localization":
                user_prompt = f"""{template}

## YOUR TASK

**Code to Analyze:**
```
{request.code}
```

**Bug Description:**
{request.bug_description}

**Context:**
{request.context or "No additional context provided"}

Now fill out the certificate following the exact structure above. Trace execution paths."""

            elif request.task == "code_qa":
                user_prompt = f"""{template}

## YOUR TASK

**Code to Analyze:**
```
{request.code}
```

**Question:**
{request.question}

**Context:**
{request.context or "No additional context provided"}

Now fill out the certificate. Gather evidence before answering."""

            else:
                raise HTTPException(status_code=400, detail="Invalid task type")
            
            # Use GPT-5.1 for semi-formal reasoning
            chat = LlmChat(
                api_key=self.api_key,
                session_id=f"code_review_{request.task}",
                system_message="You are a rigorous code analysis expert. Follow semi-formal reasoning templates EXACTLY. Never guess - only derive conclusions from traced execution."
            ).with_model("openai", "gpt-5.1")
            
            # Get structured review
            message = UserMessage(text=user_prompt)
            response = await chat.send_message(message)
            
            # Parse response for key findings
            findings = self._parse_review(response, request.task)
            
            # Store review in database
            await self._store_review(request, response, findings)
            
            return {
                "success": True,
                "task": request.task,
                "analysis": response,
                "findings": findings,
                "method": "semi-formal_reasoning",
                "model": "gpt-5.1",
                "accuracy_benchmark": "93% on patch equivalence"
            }
            
        except Exception as e:
            logger.error(f"Code review error: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    def _parse_review(self, response: str, task: str) -> Dict:
        """Extract key findings from structured response"""
        findings = {
            "premises_stated": "PREMISES" in response,
            "execution_traced": "EXECUTION" in response or "TRACE" in response,
            "edge_cases_checked": "EDGE CASE" in response,
            "formal_conclusion": "CONCLUSION" in response,
            "confidence_provided": "%" in response or "confidence" in response.lower()
        }
        
        # Extract conclusion
        if "FORMAL CONCLUSION" in response:
            conclusion_start = response.find("FORMAL CONCLUSION")
            findings["conclusion"] = response[conclusion_start:conclusion_start+500]
        
        return findings
    
    async def _store_review(self, request: CodeReviewRequest, analysis: str, findings: Dict):
        """Store code review in MongoDB"""
        try:
            from datetime import datetime, timezone
            
            review_doc = {
                "task": request.task,
                "code": request.code[:500],  # Store preview
                "analysis": analysis,
                "findings": findings,
                "method": "semi_formal_reasoning",
                "timestamp": datetime.now(timezone.utc)
            }
            
            await self.db.code_reviews.insert_one(review_doc)
        except Exception as e:
            logger.error(f"Failed to store review: {e}")

def create_code_review_engine(db):
    return SemiFormalCodeReviewEngine(db)

# Route registration
def register_routes(db, get_current_user, require_admin):
    """Register semi-formal code review routes"""
    router = APIRouter(tags=["Code Review"])
    engine = create_code_review_engine(db)
    
    @router.get("/capabilities")
    async def get_capabilities():
        """Get code review capabilities"""
        return engine.get_capabilities()
    
    @router.post("/review")
    async def review_code(request: CodeReviewRequest):
        """Perform semi-formal code review"""
        return await engine.review_code(request)
    
    @router.get("/stats")
    async def get_stats():
        """Get code review statistics"""
        total = await db.code_reviews.count_documents({})
        by_task = await db.code_reviews.aggregate([
            {"$group": {"_id": "$task", "count": {"$sum": 1}}}
        ]).to_list(100)
        
        return {
            "total_reviews": total,
            "by_task": {item["_id"]: item["count"] for item in by_task},
            "method": "semi_formal_reasoning",
            "accuracy": "93% benchmark"
        }
    
    return router

# Global instance
hybrid_code_review = None
def init_hybrid(db):
    global hybrid_code_review
    hybrid_code_review = create_code_review_engine(db)
    return hybrid_code_review
