from __future__ import annotations

def merge_dicts(dict1, dict2):
    result = dict1.copy()
    for key, value in dict2.items():
        if key in result:
            if isinstance(result[key], (int, float)) and isinstance(value, (int, float)):
                result[key] += value
            else:
                result[key] = value  # или raise ValueError
        else:
            result[key] = value
    return result