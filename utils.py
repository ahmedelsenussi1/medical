from datetime import datetime

def ensure_json_serializable(obj):
    """Make sure the object is JSON serializable"""
    if obj is None:
        return None
    if isinstance(obj, (str, int, float, bool)):
        return obj
    if isinstance(obj, datetime):
        return obj.isoformat()
    if isinstance(obj, dict):
        return {k: ensure_json_serializable(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [ensure_json_serializable(item) for item in obj]
    # If the object is another type, try to convert it to string
    try:
        return str(obj)
    except:
        return None