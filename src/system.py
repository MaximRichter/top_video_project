import platform
import subprocess
import logging

def detect_codec() -> str:
    os_name = platform.system()
    try: 
        if os_name == "Windows":
            result = subprocess.run(
                ["wmic", "path", "win32_VideoController", "get", "name"],
                capture_output=True, text=True
            )
        else: 
            result = subprocess.run(
                ["lspci"],
                capture_output=True, text=True
            )
        gpu_info = result.stdout.lower()
    except Exception as e:
        gpu_info = ""
    if "nvidia" in gpu_info:
        codec = "h264_nvenc"
    elif "amd" in gpu_info or "radeon" in gpu_info:
        if os_name == "Linux":
            codec = "h264_vaapi"
        else: 
            codec = "h264_amf"
    elif "intel" in gpu_info:
        codec = "h264_qsv"
    else:
        codec = "libx264"

    return codec

