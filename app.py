import math

def analyze(payload):
    stages=payload['stages']
    if not isinstance(stages,list) or not stages: raise ValueError('Provide stages')
    records={}
    for stage in stages:
        name=stage['id']; seconds=stage['seconds']; deps=stage['after']
        if not isinstance(name,str) or not name.strip() or name in records: raise ValueError('Stage IDs must be unique')
        if type(seconds) not in (int,float) or not math.isfinite(seconds) or seconds<0 or not isinstance(deps,list): raise ValueError('Invalid duration or dependencies')
        records[name]=stage
    complete={}; active=set()
    def visit(name):
        if name in complete: return complete[name]
        if name in active or name not in records: raise ValueError('Cyclic or missing dependency')
        active.add(name)
        stage=records[name]
        earlier=[visit(dep) for dep in stage['after']]
        parent=max(earlier,key=lambda r:r['finish']) if earlier else None
        start=parent['finish'] if parent else 0
        result={'id':name,'start':start,'finish':start+stage['seconds'],'path':(parent['path'] if parent else [])+[name]}
        active.remove(name);complete[name]=result
        return result
    for name in records: visit(name)
    last=max(complete.values(),key=lambda r:r['finish'])
    return {'durationSeconds':last['finish'],'criticalPath':last['path'],'stages':list(complete.values())}

if __name__ == "__main__":
    import json
    from pathlib import Path
    import sys
    try:
        path, = sys.argv[1:]
        result = analyze(json.loads(Path(path).read_text(encoding="utf-8")))
        print(json.dumps(result, ensure_ascii=True, allow_nan=False))
    except (OSError, ValueError, TypeError, KeyError, AttributeError, OverflowError) as error:
        print(f"Invalid input: {error}", file=sys.stderr)
        sys.exit(2)
