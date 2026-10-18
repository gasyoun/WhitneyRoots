# -*- coding: utf-8 -*-
"""H6980 fixture: a builder that is NOT one of the twelve H2892 scripts.

It asks the guard about the path it is about to write, exactly as a newly
written agent builder should. The guard must refuse a protected target without
``ALLOW_OVERLAY_WIPE=1`` and must let an unprotected target through.
"""
import argparse
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / 'scripts'))

from overlay_guard import refuse_unless_hatched  # noqa: E402


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--target', required=True,
                        help='repo-relative path this builder writes')
    parser.add_argument('--registry', default=None,
                        help='protected-paths TSV override (tests only)')
    parser.add_argument('--content', default='fixture\n')
    args = parser.parse_args()

    refuse_unless_hatched(__file__, targets=(args.target,),
                          registry=args.registry)

    target = REPO / args.target
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(args.content, encoding='utf-8')


if __name__ == '__main__':
    main()
