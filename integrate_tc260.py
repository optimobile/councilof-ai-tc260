"""
Integration script to add TC260 routes to existing app.py
Run this on Vast.ai server after extracting tc260 files
"""

import sys

# Read existing app.py
with open('app.py', 'r') as f:
    app_content = f.read()

# Check if TC260 already integrated
if 'tc260' in app_content.lower():
    print("✓ TC260 already integrated in app.py")
    sys.exit(0)

# Find the line where we should add the import
import_section = """
# TC260 Integration
from tc260.engine import TC260Engine
from tc260.schemas import VerificationRequest, VerificationReport
"""

# Find the line where we should add the router
tc260_routes = '''

# ============================================================================
# TC260 SAFETY VERIFICATION ROUTES
# ============================================================================

# Initialize TC260 engine
tc260_engine = TC260Engine()

@app.get("/api/v1/tc260")
async def tc260_info():
    """Get TC260 system information"""
    module_info = tc260_engine.get_module_info()
    return {
        "name": "TC260 AI Safety Verification System",
        "version": "0.1.0",
        "status": "operational",
        "modules_loaded": len(module_info),
        "modules": list(module_info.keys())
    }

@app.post("/api/v1/tc260/verify", response_model=VerificationReport)
async def verify_content(request: VerificationRequest):
    """Verify AI-generated content against TC260 safety standards"""
    try:
        report = tc260_engine.verify(request)
        return report
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Verification failed: {str(e)}")

@app.get("/api/v1/tc260/categories")
async def list_categories():
    """List all available TC260 risk categories"""
    module_info = tc260_engine.get_module_info()
    categories = [
        {
            "id": info["category_id"],
            "name": info["category_name"],
            "threshold": info["threshold"]
        }
        for cat_id, info in module_info.items()
    ]
    return {"total": len(categories), "categories": categories}
'''

# Add imports after existing imports
if 'from fastapi import' in app_content:
    # Find the end of imports (first empty line after imports)
    lines = app_content.split('\n')
    import_end = 0
    found_import = False
    for i, line in enumerate(lines):
        if line.startswith('import ') or line.startswith('from '):
            found_import = True
        elif found_import and line.strip() == '':
            import_end = i
            break
    
    # Insert TC260 import
    lines.insert(import_end, import_section)
    app_content = '\n'.join(lines)

# Add routes at the end, before if __name__ == "__main__" if it exists
if 'if __name__' in app_content:
    app_content = app_content.replace('if __name__', tc260_routes + '\n\nif __name__')
else:
    app_content += tc260_routes

# Write updated app.py
with open('app.py', 'w') as f:
    f.write(app_content)

print("✓ TC260 routes added to app.py")
print("✓ Integration complete!")
print("")
print("Restart your server:")
print("  pkill -f uvicorn")
print("  python3 -m uvicorn app:app --host 0.0.0.0 --port 6006 &")
