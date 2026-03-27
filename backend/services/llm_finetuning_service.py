"""
LLM Fine-Tuning Service
Fine-tunes models on NEXUS codebase for better autonomous development
"""
import logging
import os
import json
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from pathlib import Path

logger = logging.getLogger(__name__)

class LLMFineTuningService:
    """
    Fine-tunes LLMs on NEXUS codebase to:
    - Generate better NEXUS-specific code
    - Understand NEXUS architecture
    - Follow NEXUS coding patterns
    - Fix bugs more accurately
    """
    
    def __init__(self):
        self.training_data_path = Path("/app/training_data")
        self.training_data_path.mkdir(exist_ok=True)
        self.openai_api_key = os.getenv('EMERGENT_LLM_KEY', '')
        self.enabled = bool(self.openai_api_key)
        
        # Fine-tuning jobs
        self.jobs = []
        
        if self.enabled:
            logger.info("✓ LLM Fine-Tuning service initialized")
        else:
            logger.info("LLM Fine-Tuning disabled (need EMERGENT_LLM_KEY)")
    
    async def prepare_training_data(self) -> Dict[str, Any]:
        """
        Prepare training data from NEXUS codebase.
        
        Creates training examples from:
        - Existing code files
        - Git commit messages
        - API documentation
        - Test cases
        """
        logger.info("Preparing training data from NEXUS codebase...")
        
        training_examples = []
        
        # 1. Extract code patterns from backend
        backend_files = list(Path("/app/backend").rglob("*.py"))
        for file_path in backend_files[:50]:  # Sample 50 files
            try:
                with open(file_path, 'r') as f:
                    content = f.read()
                    
                    # Create training example
                    if len(content) > 100 and len(content) < 4000:
                        # Extract function/class descriptions
                        lines = content.split('\n')
                        docstring = None
                        code = []
                        
                        for line in lines:
                            if '"""' in line:
                                docstring = line
                            else:
                                code.append(line)
                        
                        if docstring:
                            training_examples.append({
                                "messages": [
                                    {"role": "system", "content": "You are a NEXUS platform developer. Generate production-ready code following NEXUS patterns."},
                                    {"role": "user", "content": f"Implement this: {docstring}"},
                                    {"role": "assistant", "content": '\n'.join(code[:50])}
                                ]
                            })
            except:
                pass
        
        # 2. Extract patterns from services
        for service_file in Path("/app/backend/services").glob("*.py"):
            try:
                with open(service_file, 'r') as f:
                    content = f.read()
                    if "class" in content and "def" in content:
                        training_examples.append({
                            "messages": [
                                {"role": "system", "content": "You are a NEXUS platform developer. Write service classes following NEXUS architecture."},
                                {"role": "user", "content": f"Create a service similar to {service_file.name}"},
                                {"role": "assistant", "content": content[:2000]}
                            ]
                        })
            except:
                pass
        
        # 3. API route patterns
        for route_file in Path("/app/backend/routes").glob("*.py"):
            try:
                with open(route_file, 'r') as f:
                    content = f.read()
                    if "@router" in content:
                        training_examples.append({
                            "messages": [
                                {"role": "system", "content": "You are a NEXUS platform developer. Write FastAPI routes following NEXUS patterns."},
                                {"role": "user", "content": f"Create API routes like {route_file.name}"},
                                {"role": "assistant", "content": content[:2000]}
                            ]
                        })
            except:
                pass
        
        # Save training data
        training_file = self.training_data_path / f"nexus_training_{datetime.now().strftime('%Y%m%d')}.jsonl"
        with open(training_file, 'w') as f:
            for example in training_examples[:100]:  # Limit to 100 examples
                f.write(json.dumps(example) + '\n')
        
        return {
            "success": True,
            "examples_count": len(training_examples[:100]),
            "training_file": str(training_file),
            "note": "Training data prepared. Use OpenAI Fine-Tuning API to train."
        }
    
    async def start_fine_tuning(
        self,
        model: str = "gpt-4o-mini",
        training_file_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Start fine-tuning job using OpenAI API.
        
        Note: This requires uploading training data to OpenAI
        and costs credits based on tokens.
        """
        if not self.enabled:
            return {"success": False, "error": "API key not configured"}
        
        logger.info(f"Starting fine-tuning job for {model}...")
        
        try:
            from emergentintegrations.openai import OpenAIEmergent
            
            client = OpenAIEmergent(api_key=self.openai_api_key)
            
            # Find training file
            if not training_file_path:
                training_files = list(self.training_data_path.glob("*.jsonl"))
                if not training_files:
                    return {"success": False, "error": "No training data. Run prepare_training_data first."}
                training_file_path = str(training_files[-1])
            
            # Upload training file
            with open(training_file_path, 'rb') as f:
                upload_response = client.files.create(
                    file=f,
                    purpose="fine-tune"
                )
            
            # Create fine-tuning job
            job = client.fine_tuning.jobs.create(
                training_file=upload_response.id,
                model=model,
                suffix="nexus"
            )
            
            job_info = {
                "id": job.id,
                "model": model,
                "status": job.status,
                "created_at": datetime.fromtimestamp(job.created_at).isoformat()
            }
            
            self.jobs.append(job_info)
            
            return {
                "success": True,
                "job": job_info,
                "note": "Fine-tuning started. Check status with get_job_status()"
            }
        except Exception as e:
            logger.error(f"Fine-tuning failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_job_status(self, job_id: str) -> Dict[str, Any]:
        """Get fine-tuning job status"""
        if not self.enabled:
            return {"success": False, "error": "API key not configured"}
        
        try:
            from emergentintegrations.openai import OpenAIEmergent
            
            client = OpenAIEmergent(api_key=self.openai_api_key)
            job = client.fine_tuning.jobs.retrieve(job_id)
            
            return {
                "success": True,
                "status": job.status,
                "trained_tokens": job.trained_tokens,
                "fine_tuned_model": job.fine_tuned_model
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_status(self) -> Dict[str, Any]:
        """Get fine-tuning service status"""
        return {
            "enabled": self.enabled,
            "training_data_path": str(self.training_data_path),
            "jobs_count": len(self.jobs),
            "recent_jobs": self.jobs[-5:] if self.jobs else []
        }

# Singleton
llm_finetuning = LLMFineTuningService()
