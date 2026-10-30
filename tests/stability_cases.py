"""Bounded deterministic independent corpus, shared by Python/JS/Kotlin checks."""
from pathlib import Path
import random
SOURCE=(Path(__file__).parent/'fixtures/stability_boundaries.sdr').read_text(encoding='utf-8')

def steps(seed=107):
    # A fixed prefix guarantees capacity, missing identity, int32 and rollback
    # coverage independently of the random suffix. No unbounded fuzzing in CI.
    result=[('input','title','</script><img src=x onerror=alert(1)> 😀'),('action','add')]*4
    result += [('action','overflow'),('action','invariant'),('action','missing_min'),('input','selected',1),('action','remove'),('action','add'),('roundtrip',)]
    rng=random.Random(seed)
    for _ in range(40):
        result.append(rng.choice([
            ('input','title',''),('input','title','e\u0301\u202e😀\x00'),
            ('input','title','😀'*1025),('input','selected',-2147483648),
            ('input','selected',2147483648),('input','selected',2),
            ('action','add'),('action','remove'),('action','overflow'),
            ('action','invariant'),('action','minimum'),('roundtrip',)]))
    return result
