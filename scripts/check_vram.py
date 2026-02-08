#!/usr/bin/env python3
"""Check VRAM and report what's available for new tasks."""
import subprocess
import json

def get_vram_status():
    result = subprocess.run(
        ['nvidia-smi', '--query-gpu=memory.used,memory.total,memory.free', '--format=csv,noheader,nounits'],
        capture_output=True, text=True
    )
    used, total, free = map(int, result.stdout.strip().split(', '))
    
    # Thresholds
    COMFYUI_SDXL = 20000  # ~20GB for SDXL
    COMFYUI_SD15 = 8000   # ~8GB for SD1.5
    OLLAMA_PHI3 = 3000    # ~3GB for phi3:mini
    OLLAMA_LLAMA3 = 8000  # ~8GB for llama3.2
    
    print(f"🎮 VRAM: {used}MB used / {total}MB total / {free}MB free")
    print()
    
    if free >= COMFYUI_SDXL:
        print("✅ ComfyUI SDXL: GO")
    elif free >= COMFYUI_SD15:
        print("⚠️  ComfyUI SDXL: NO (use SD1.5)")
        print("✅ ComfyUI SD1.5: GO")
    else:
        print("❌ ComfyUI: NO (need to free VRAM)")
    
    if free >= OLLAMA_LLAMA3:
        print("✅ Ollama llama3.2: GO")
    elif free >= OLLAMA_PHI3:
        print("✅ Ollama phi3:mini: GO")
    else:
        print("❌ Ollama: NO (model already loaded?)")
    
    return {'used': used, 'total': total, 'free': free}

if __name__ == '__main__':
    get_vram_status()
