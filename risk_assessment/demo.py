import json
from pathlib import Path
from risk import evaluate


def example():
    return {'schema_version': '1.0', 'frame_id': 'map', 'stamp': 0., 'horizon_s': 2.,
            'safety_margin_m': .3, 'max_observation_age_s': .2,
            'robot': {'id': 'robot_0', 'radius_m': .3, 'trajectory': [
                {'t': 0., 'x': 0., 'y': 0.}, {'t': 2., 'x': 2., 'y': 0.}]},
            'obstacles': [{'id': 'obstacle_0', 'observed_at': 0., 'radius_m': .3,
                'trajectory': [{'t': 0., 'x': 2., 'y': 0.}, {'t': 2., 'x': 0., 'y': 0.}]}]}


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', type=Path)
    args = parser.parse_args()
    data = json.loads(args.input.read_text(encoding='utf-8')) if args.input else example()
    print(json.dumps(evaluate(data), ensure_ascii=False, indent=2, allow_nan=False))
