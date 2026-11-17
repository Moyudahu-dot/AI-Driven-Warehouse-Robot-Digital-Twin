"""Week-one risk evaluator; standard library only, no navigation side effects."""
import math


def number(value):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError('Expected finite numeric value')
    return value


def trajectory(points, now, horizon):
    if len(points) < 2:
        raise ValueError('Trajectory needs at least two points')
    result = [(number(p['t']), number(p['x']), number(p['y'])) for p in points]
    if any(b[0] <= a[0] for a, b in zip(result, result[1:])):
        raise ValueError('Timestamps must strictly increase')
    if result[0][0] > now or result[-1][0] < now + horizon:
        raise ValueError('Trajectory must cover the entire evaluation interval')
    return result


def position(points, t):
    for a, b in zip(points, points[1:]):
        if a[0] <= t <= b[0]:
            u = (t-a[0])/(b[0]-a[0])
            return (a[1]+u*(b[1]-a[1]), a[2]+u*(b[2]-a[2]))
    raise ValueError('Time outside trajectory')


def evaluate(data):
    """Fail closed as UNKNOWN on invalid inputs; callers must not interpret as clear."""
    try:
        return _evaluate(data)
    except (ValueError, KeyError, TypeError, IndexError) as error:
        return {'status': 'UNKNOWN', 'reason': str(error), 'obstacles': [],
                'min_clearance_m': None, 'first_buffer_entry_s': None}


def _evaluate(data):
    if data['schema_version'] != '1.0' or data['frame_id'] != 'map':
        raise ValueError('Unsupported schema or frame')
    now = number(data['stamp'])
    horizon = number(data['horizon_s'])
    margin = number(data['safety_margin_m'])
    age = number(data['max_observation_age_s'])
    if horizon <= 0 or margin < 0 or age < 0:
        raise ValueError('Invalid evaluation parameters')
    robot = data['robot']
    rr = number(robot['radius_m'])
    if rr <= 0:
        raise ValueError('Robot radius must be positive')
    rp = trajectory(robot['trajectory'], now, horizon)
    results, ids = [], set()
    for obstacle in data['obstacles']:
        oid = obstacle['id']
        if not isinstance(oid, str) or not oid or oid in ids:
            raise ValueError('Obstacle IDs must be unique nonempty strings')
        ids.add(oid)
        observed = number(obstacle['observed_at'])
        if not 0 <= now - observed <= age:
            raise ValueError('Stale or future observation')
        radius = number(obstacle['radius_m'])
        if radius <= 0:
            raise ValueError('Obstacle radius must be positive')
        op = trajectory(obstacle['trajectory'], now, horizon)
        knots = sorted({now, now+horizon} | {p[0] for p in rp+op if now < p[0] < now+horizon})
        best, closest, entry = math.inf, None, None
        threshold = rr + radius + margin
        for start, end in zip(knots, knots[1:]):
            ra, rb = position(rp, start), position(rp, end)
            oa, ob = position(op, start), position(op, end)
            q = (oa[0]-ra[0], oa[1]-ra[1])
            v = ((ob[0]-rb[0]-q[0])/(end-start), (ob[1]-rb[1]-q[1])/(end-start))
            vv = v[0]**2+v[1]**2
            dot = q[0]*v[0]+q[1]*v[1]
            u = min(end-start, max(0., -dot/vv)) if vv else 0.
            clearance = math.hypot(q[0]+u*v[0], q[1]+u*v[1])-rr-radius
            if clearance < best:
                best, closest = clearance, start+u-now
            c = q[0]**2+q[1]**2-threshold**2
            hit = 0. if c <= 0 else None
            discriminant = dot*dot-vv*c
            if hit is None and vv > 0 and discriminant >= 0:
                root = (-dot-math.sqrt(discriminant))/vv
                if 0 <= root <= end-start:
                    hit = root
            if hit is not None:
                candidate = start+hit-now
                entry = candidate if entry is None else min(entry, candidate)
        results.append({'id': oid, 'min_clearance_m': best, 'closest_time_s': closest,
                        'first_buffer_entry_s': entry, 'predicted_contact': best <= 0})
    return {'status': 'RISK' if any(r['first_buffer_entry_s'] is not None for r in results) else 'CLEAR',
            'min_clearance_m': min((r['min_clearance_m'] for r in results), default=None),
            'first_buffer_entry_s': min((r['first_buffer_entry_s'] for r in results if r['first_buffer_entry_s'] is not None), default=None),
            'obstacles': results}
