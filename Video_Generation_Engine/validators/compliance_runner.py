from validators.forbidden_terms import scan

def run(script, config):
    for field in script.dict().values():
        if isinstance(field, str):
            scan(field, config["forbidden_terms"])
    return script
