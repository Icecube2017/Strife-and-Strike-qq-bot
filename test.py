# -*- coding:utf-8 -*-

import assets

ANTI_MAP: dict = {}
for _k,_v in assets.MAP.items():
    ANTI_MAP[_v] = _k

TAG = assets.TAG

with open(assets.__ASSETS_PATH / "test.txt", 'w+', encoding='utf-8') as f:
    for _k, _v in TAG.items():
        _w = ''
        for _s in _v:
            _w += f'{ANTI_MAP[_s]},'
        _w = _w.strip(',')
        f.write(f'{ANTI_MAP[_k]},{_w}\n')