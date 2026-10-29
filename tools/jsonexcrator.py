def jsonexcrator(raw_ai_response: str) -> str:
    start_idx = raw_ai_response.find("{")
    end_idx = raw_ai_response.rfind("}") + 1

    if start_idx != -1 and end_idx != -1:
        clean_ai_json = raw_ai_response[start_idx:end_idx]
    else:
        clean_ai_json = '{"actions": []}'

    return clean_ai_json
