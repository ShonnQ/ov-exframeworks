#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""OPPO / vivo 两张 AOSP 改造点结构图（SVG），中英双语输出。

关键约束（上一版踩过坑）：
- README 里两张并排，各约 468px；所以画布本身就设计成 460px 宽，显示接近 1:1，
  字才唔会缩到 6px。画布画得越大字越细，同「图更详细」系相反嘅取舍。
- 两张图共用同一套行高与 y 坐标（joint layout），左右并排逐层严格对齐；
- 卡片与色条顶部对齐，同一行编号落在同一水平线。

输出：docs/img/aosp-oppo.svg · aosp-vivo.svg（中文）
      docs/img/aosp-oppo.en.svg · aosp-vivo.en.svg（英文）
"""
import pathlib

W = 460
BASE_X, BASE_W = 14, 208
CARD_X, CARD_W = 232, 214
FONT = "'PingFang SC','Hiragino Sans GB','Microsoft YaHei',-apple-system,Arial,sans-serif"

C_BG, C_BAND_FILL, C_BAND_STRK = '#ffffff', '#f4f6f8', '#c9d2da'
C_TEXT, C_SUB, C_MUTED = '#12181f', '#57636f', '#94a1ad'
C_ACC, C_ACC_FILL = '#0f9d8a', '#e9f8f5'

F_TITLE, F_SUB, F_HDR = 14.5, 9.5, 9
F_BT, F_BS, F_CARD = 11.5, 10, 10.5


def txt_w(s, size):
    return sum(size if ord(c) > 0x2E80 else size * (0.3 if c in 'il.,:;|! ' else 0.55) for c in s)


def wrap(s, size, max_w):
    """先按空格断词，单个词过长才按字符切；中文无空格，走字符切。"""
    lines, cur = [], ''
    for word in s.split(' '):
        cand = word if not cur else cur + ' ' + word
        if txt_w(cand, size) <= max_w:
            cur = cand
            continue
        if cur:
            lines.append(cur)
        if txt_w(word, size) > max_w:
            piece = ''
            for ch in word:
                if txt_w(piece + ch, size) > max_w and piece:
                    lines.append(piece); piece = ch
                else:
                    piece += ch
            cur = piece
        else:
            cur = word
    if cur:
        lines.append(cur)
    return lines


def esc(s):
    return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def text(x, y, s, size=F_CARD, fill=C_TEXT, weight='normal', anchor='start'):
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="{FONT}" font-size="{size}" fill="{fill}" '
            f'font-weight="{weight}" text-anchor="{anchor}">{esc(s)}</text>')


def badge(n):
    return (f'<circle cx="0" cy="0" r="7.5" fill="{C_ACC}"/>'
            + text(0, 3.2, str(n), 9.5, '#ffffff', '600', 'middle'))


def measure(rows):
    out = []
    for r in rows:
        b = [(t, sz, wt, col, wrap(t, sz, BASE_W - 24)) for t, sz, wt, col in r['band']]
        b_h = 12 + sum(len(ls) * (sz + 3.5) for _t, sz, _w, _c, ls in b) + 5
        cl, c_h = [], 0
        if r.get('card'):
            num, lines = r['card']
            cl = [(t, wrap(t, F_CARD, CARD_W - 34)) for t in lines]
            c_h = 13 + sum(len(ls) * 14 for _, ls in cl) + 8
        out.append(dict(band=b, card=r.get('card'), cl=cl, c_h=c_h, need=max(b_h, c_h, 36)))
    return out


def joint(rows_list):
    ms = [measure(r) for r in rows_list]
    heights = [max(m[i]['need'] for m in ms if i < len(m)) for i in range(max(len(m) for m in ms))]
    y, ys = 104, []
    for h in heights:
        ys.append(y); y += h + 7
    for m in ms:
        for i, row in enumerate(m):
            row['y'], row['h'] = ys[i], heights[i]
    return ms, y


L = lambda t, sz=F_BT, wt='normal', col=C_TEXT: (t, sz, wt, col)


def draw(title, subtitle, rows, foot, H, y_end, hdr):
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
         f'role="img" aria-label="{esc(title)}">',
         f'<rect width="{W}" height="{H}" fill="{C_BG}"/>',
         f'<rect x="0" y="0" width="{W}" height="3" fill="{C_ACC}"/>',
         text(BASE_X, 32, title, F_TITLE, C_TEXT, '700'),
         text(BASE_X, 49, subtitle, F_SUB, C_SUB),
         f'<line x1="{BASE_X}" y1="60" x2="{W-14}" y2="60" stroke="{C_BAND_STRK}"/>',
         text(BASE_X, 76, hdr[0], F_HDR, C_MUTED, '600'),
         text(CARD_X, 76, hdr[1], F_HDR, C_ACC, '600'),
         f'<line x1="{BASE_X}" y1="83" x2="{BASE_X+BASE_W}" y2="83" stroke="{C_BAND_STRK}"/>',
         f'<line x1="{CARD_X}" y1="83" x2="{CARD_X+CARD_W}" y2="83" stroke="{C_BAND_STRK}"/>']

    for row in rows:
        y, rh = row['y'], row['h']
        o.append(f'<rect x="{BASE_X}" y="{y}" width="{BASE_W}" height="{rh}" rx="5" fill="{C_BAND_FILL}" '
                 f'stroke="{C_BAND_STRK}"/>')
        ty = y + 16
        for t, sz, wt, col, ls in row['band']:
            for j, ln in enumerate(ls):
                o.append(text(BASE_X + 10, ty, ln, sz, col, wt if j == 0 else 'normal'))
                ty += sz + 3.5
            ty += 2

        if row['c_h']:
            num, _ = row['card']
            cy = y
            o.append(f'<path d="M {BASE_X+BASE_W} {y+min(rh,row["c_h"])/2:.1f} H {CARD_X-10} '
                     f'V {cy+row["c_h"]/2:.1f} H {CARD_X}" fill="none" stroke="{C_ACC}" stroke-width="1" '
                     f'stroke-dasharray="3 2.5" opacity="0.5"/>')
            o.append(f'<rect x="{CARD_X}" y="{cy}" width="{CARD_W}" height="{row["c_h"]}" rx="5" '
                     f'fill="{C_ACC_FILL}" stroke="{C_ACC}"/>')
            o.append(f'<g transform="translate({CARD_X+13},{cy+13})">{badge(num)}</g>')
            ty = cy + 17
            for t, ls in row['cl']:
                for j, ln in enumerate(ls):
                    o.append(text(CARD_X + 25, ty, ln, F_CARD, C_TEXT, '600' if j == 0 else 'normal'))
                    ty += 14

    fy = y_end + 6
    o.append(f'<line x1="{BASE_X}" y1="{fy}" x2="{W-14}" y2="{fy}" stroke="{C_BAND_STRK}"/>')
    for i, ln in enumerate(foot):
        o.append(text(BASE_X, fy + 14 + i * 13, ln, 8.8, '#6b7883'))
    o.append('</svg>')
    return '\n'.join(o)


# ---------------- 文案（中 / 英） ----------------
SPEC = {
    'zh': dict(
        hdr=('AOSP 原生架构', '改造点'),
        title_o='OPPO · AOSP 改造点', sub_o='Android 11 · OPPO K7',
        title_v='vivo · AOSP 改造点', sub_v='Android 12 · iQOO Z1x',
        foot_o=['数据取自本仓 OPPO K7（A11）固件'],
        foot_v=['数据取自本仓 iQOO Z1x（A12）固件'],
        oppo=[
            ([L('应用层'), L('第三方 · 预装 app', F_BS, 'normal', C_SUB)], None),
            ([L('Java Framework'), L('framework.jar', F_BS, 'normal', C_SUB)],
             (1, ['oplus-framework.jar 3.6MB', 'ExtImpl 扩展 AOSP 接口'])),
            ([L('系统服务'), L('services.jar · SystemServer', F_BS, 'normal', C_SUB)],
             (2, ['SystemServerExtPlugin', '反射拿 ISystemServerExt'])),
            ([L('定制服务'), L('oplus 前缀 45 / 292', F_BS, 'normal', C_SUB)],
             (3, ['oplus-services.jar 8.8MB', '与 AOSP 服务同级注册'])),
            ([L('Native / HAL'), L('init · vendor.*', F_BS, 'normal', C_SUB)], None),
            ([L('Linux Kernel'), L('binder · dm-verity', F_BS, 'normal', C_SUB)], None),
            ([L('分区层'), L('/system · /product', F_BS, 'normal', C_SUB)],
             (4, ['10 个 my_* 分区', 'overlay 叠到 /product'])),
        ],
        vivo=[
            ([L('应用层'), L('第三方 · 预装 app', F_BS, 'normal', C_SUB)], None),
            ([L('Java Framework'), L('framework.jar', F_BS, 'normal', C_SUB)],
             (1, ['vivo-framework.jar 3.8MB', '+ vgcclient.jar 42KB'])),
            ([L('系统服务'), L('services.jar · SystemServer', F_BS, 'normal', C_SUB)],
             (2, ['IVivoSystemServer', '起 vivo-services.jar'])),
            ([L('定制服务'), L('vivo 前缀 41 / 239', F_BS, 'normal', C_SUB)],
             (3, ['vivo-services.jar 5.3MB', 'VGC 按 carrier 选配置'])),
            ([L('Native / HAL'), L('init · vendor.*', F_BS, 'normal', C_SUB)], None),
            ([L('Linux Kernel'), L('binder · dm-verity', F_BS, 'normal', C_SUB)], None),
            ([L('分区层'), L('/system · /product · /vgc', F_BS, 'normal', C_SUB)],
             (4, ['/vgc 只存目录指针', '/data/vgc 运行时配置'])),
        ],
        out_o='aosp-oppo.svg', out_v='aosp-vivo.svg',
    ),
    'en': dict(
        hdr=('AOSP as shipped', 'Modification'),
        title_o='OPPO · versus AOSP', sub_o='Android 11 · OPPO K7',
        title_v='vivo · versus AOSP', sub_v='Android 12 · iQOO Z1x',
        foot_o=['Source: OPPO K7 (A11) firmware in this repo'],
        foot_v=['Source: iQOO Z1x (A12) firmware in this repo'],
        oppo=[
            ([L('Apps'), L('3rd-party · preinstalled', F_BS, 'normal', C_SUB)], None),
            ([L('Java Framework'), L('framework.jar', F_BS, 'normal', C_SUB)],
             (1, ['oplus-framework.jar 3.6MB', 'ExtImpl hooks AOSP APIs'])),
            ([L('System services'), L('services.jar · SystemServer', F_BS, 'normal', C_SUB)],
             (2, ['SystemServerExtPlugin', 'gets ISystemServerExt by reflection'])),
            ([L('Custom services'), L('45 of 292 carry oplus prefix', F_BS, 'normal', C_SUB)],
             (3, ['oplus-services.jar 8.8MB', 'registers at AOSP level'])),
            ([L('Native / HAL'), L('init · vendor.*', F_BS, 'normal', C_SUB)], None),
            ([L('Linux Kernel'), L('binder · dm-verity', F_BS, 'normal', C_SUB)], None),
            ([L('Partitions'), L('/system · /product', F_BS, 'normal', C_SUB)],
             (4, ['10 my_* partitions', 'overlay onto /product'])),
        ],
        vivo=[
            ([L('Apps'), L('3rd-party · preinstalled', F_BS, 'normal', C_SUB)], None),
            ([L('Java Framework'), L('framework.jar', F_BS, 'normal', C_SUB)],
             (1, ['vivo-framework.jar 3.8MB', '+ vgcclient.jar 42KB'])),
            ([L('System services'), L('services.jar · SystemServer', F_BS, 'normal', C_SUB)],
             (2, ['IVivoSystemServer', 'starts vivo-services.jar'])),
            ([L('Custom services'), L('41 of 239 carry vivo prefix', F_BS, 'normal', C_SUB)],
             (3, ['vivo-services.jar 5.3MB', 'VGC picks the config set'])),
            ([L('Native / HAL'), L('init · vendor.*', F_BS, 'normal', C_SUB)], None),
            ([L('Linux Kernel'), L('binder · dm-verity', F_BS, 'normal', C_SUB)], None),
            ([L('Partitions'), L('/system · /product · /vgc', F_BS, 'normal', C_SUB)],
             (4, ['/vgc holds only pointers', '/data/vgc at runtime'])),
        ],
        out_o='aosp-oppo.en.svg', out_v='aosp-vivo.en.svg',
    ),
}

outdir = pathlib.Path(__file__).resolve().parent / 'img'
outdir.mkdir(parents=True, exist_ok=True)

for lang, spec in SPEC.items():
    rows_o = [dict(band=b, card=c) for b, c in spec['oppo']]
    rows_v = [dict(band=b, card=c) for b, c in spec['vivo']]
    (om, vm), y_end = joint([rows_o, rows_v])
    H = int(y_end + 6 + 14 + 13 + 8)
    a = draw(spec['title_o'], spec['sub_o'], om, spec['foot_o'], H, y_end, spec['hdr'])
    b = draw(spec['title_v'], spec['sub_v'], vm, spec['foot_v'], H, y_end, spec['hdr'])
    (outdir / spec['out_o']).write_text(a, encoding='utf-8')
    (outdir / spec['out_v']).write_text(b, encoding='utf-8')
    print(f'[{lang}] W={W} H={H} cards={[r["c_h"] for r in om]} -> {spec["out_o"]}, {spec["out_v"]}')
