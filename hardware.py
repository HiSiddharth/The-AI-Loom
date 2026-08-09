import requests
import logging

from config import LM_STUDIO_HOST

logger = logging.getLogger("MiniPlatform")

def unload_all_models():
    logger.info("[VRAM MANAGER] Clearing all models from memory...")
    try:
        res = requests.get(f"{LM_STUDIO_HOST}/api/v0/models")
        if res.status_code == 200:
            for m in res.json().get("data", []):
                if instance_id := m.get("id"):
                    logger.info(f"-> Unloading instance: {instance_id}")
                    requests.post(f"{LM_STUDIO_HOST}/api/v1/models/unload", json={"instance_id": instance_id})
        logger.info("[SUCCESS] VRAM completely cleared.")
    except Exception as e:
        logger.warning(f"Unload skipped/failed: {e}")

def unload_model_by_identifier(model_identifier):
    logger.info(f"[VRAM MANAGER] Unloading model: {model_identifier}...")
    try:
        res = requests.get(f"{LM_STUDIO_HOST}/api/v0/models")
        if res.status_code == 200:
            for m in res.json().get("data", []):
                if model_identifier in m.get("id", "") or model_identifier in m.get("identifier", ""):
                    requests.post(f"{LM_STUDIO_HOST}/api/v1/models/unload", json={"instance_id": m.get("id")})
                    logger.info(f"[SUCCESS] Unloaded {model_identifier}")
                    return
        requests.post(f"{LM_STUDIO_HOST}/api/v1/models/unload", json={"model": model_identifier})
    except Exception as e:
        logger.warning(f"Selective unload error: {e}")

def load_model(model_identifier):
    logger.info(f"[VRAM MANAGER] Loading model into VRAM: {model_identifier}...")
    try:
        res = requests.post(f"{LM_STUDIO_HOST}/api/v1/models/load", json={"model": model_identifier, "flash_attention": True})
        if res.status_code == 200:
            logger.info(f"[SUCCESS] Loaded {model_identifier}")
        else:
            logger.error(f"[ERROR] Load failed: {res.text}")
    except Exception as e:
        logger.error(f"[ERROR] Connection error while loading {model_identifier}: {e}")