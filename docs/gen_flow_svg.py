#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""第四节的「从刷机到生效」对比图（SVG），中英双语输出。

取代原本 mermaid 两条流水线：4 个阶段并排、两家各一行，
同一阶段落同一列，最后一行点明「编译期定死 vs 运行期选择」。

输出：docs/img/flow-compare.svg（中文）· flow-compare.en.svg（英文）
"""
import pathlib

W = 900
H_BASE = 430
M_LEFT, M_RIGHT = 104, 20
GAP = 12
COL_W = (W - M_LEFT - M_RIGHT - GAP * 3) / 4

FONT = "'PingFang SC','Hiragino Sans GB','Microsoft YaHei',-apple-system,Arial,sans-serif"
C_TEXT, C_SUB, C_MUTED = '#12181f', '#57636f', '#94a1ad'
C_STRK, C_HDR = '#c9d2da', '#8c9aa8'
C_ACC, C_ACC_FILL = '#0f9d8a', '#e9f8f5'
C_OPPO, C_VIVO = '#1565c0', '#2e7d32'
C_ROW = '#f6f8f9'


def esc(s):
    return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def text(x, y, s, size=11.5, fill=C_TEXT, weight='normal', anchor='start'):
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="{FONT}" font-size="{size}" fill="{fill}" '
            f'font-weight="{weight}" text-anchor="{anchor}">{esc(s)}</text>')


def _tw(t, size):
    return sum(size if ord(c) > 0x2E80 else size * (0.3 if c in 'il.,:;|! ' else 0.55) for c in t)


def wrap(s, size, max_w):
    """先按空格断词，单个词过长才按字符切；中文无空格，走字符切。"""
    lines, cur = [], ''
    for word in s.split(' '):
        cand = word if not cur else cur + ' ' + word
        if _tw(cand, size) <= max_w:
            cur = cand
            continue
        if cur:
            lines.append(cur)
        if _tw(word, size) > max_w:
            piece = ''
            for ch in word:
                if _tw(piece + ch, size) > max_w and piece:
                    lines.append(piece); piece = ch
                else:
                    piece += ch
            cur = piece
        else:
            cur = word
    if cur:
        lines.append(cur)
    return lines


def col_x(i):
    return M_LEFT + i * (COL_W + GAP)


SPEC = {
    'zh': dict(
        out='flow-compare.svg',
        title='从刷机到生效：同一件事，四个阶段',
        sub='上为 OPPO（Android 11 · K7），下为 vivo（Android 12 · iQOO Z1x）',
        cols=['① 刷入', '② 装载', '③ 定版', '④ 生效'],
        rows=[
            dict(name='OPPO', sub='Android 11 · K7', color=C_OPPO,
                 cells=[['OTA 刷入 10 个', 'my_* 分区'],
                        ['init 挂载分区，', 'overlay 叠到 /product'],
                        ['overlay 优先级', '编译期已定死'],
                        ['SystemServer 反射', '插件起定制服务']]),
            dict(name='vivo', sub='Android 12 · Z1x', color=C_VIVO,
                 cells=[['OTA 刷入 vgc 分区', '+ cota_vgc.img（A/B）'],
                        ['VivoVgcService 读', 'XML / prop'],
                        ['按 carrier / SIM', '选配置集'],
                        ['加载配置与定制 APK', '插拔卡即时重载']]),
        ],
        concl_head='同一件事，两种时点',
        concl_body='OPPO 把结果在编译期定死 —— 改内容就是重刷分区、重新开机；'
                   'vivo 把选择留到运行期 —— 改内容等于换配置或换卡，不必重刷。',
    ),
    'en': dict(
        out='flow-compare.en.svg',
        title='From flash to effect: same job, four stages',
        sub='Top: OPPO (Android 11 · K7) — bottom: vivo (Android 12 · iQOO Z1x)',
        cols=['① Flash', '② Load', '③ Decide', '④ Effect'],
        rows=[
            dict(name='OPPO', sub='Android 11 · K7', color=C_OPPO,
                 cells=[['OTA writes 10', 'my_* partitions'],
                        ['init mounts them,', 'overlay onto /product'],
                        ['Overlay priority', 'fixed at build time'],
                        ['SystemServer plugin', 'starts custom services']]),
            dict(name='vivo', sub='Android 12 · Z1x', color=C_VIVO,
                 cells=[['OTA writes vgc', '+ cota_vgc.img (A/B)'],
                        ['VivoVgcService reads', 'XML / prop'],
                        ['Picks a config set', 'by carrier / SIM'],
                        ['Loads config + APKs', 'SIM swap reloads']]),
        ],
        concl_head='Same job, two different moments',
        concl_body='OPPO fixes the result at build time — changing content means re-flashing a '
                   'partition; vivo keeps the choice at runtime — changing content means swapping '
                   'config or the SIM.',
    ),
}


def render(spec):
    body = []
    for i, c in enumerate(spec['cols']):
        x = col_x(i)
        body.append(text(x + COL_W / 2, 88, c, 10.5, C_HDR, '600', 'middle'))
        body.append(f'<line x1="{x}" y1="95" x2="{x+COL_W}" y2="95" stroke="{C_STRK}"/>')

    row_y = 104
    ROW_H = 92
    for r in spec['rows']:
        y = row_y
        body.append(f'<rect x="20" y="{y}" width="{W-40}" height="{ROW_H}" rx="8" fill="{C_ROW}" '
                    f'stroke="{C_STRK}"/>')
        body.append(f'<rect x="20" y="{y}" width="4" height="{ROW_H}" rx="2" fill="{r["color"]}"/>')
        body.append(text(38, y + 36, r['name'], 14, r['color'], '700'))
        body.append(text(38, y + 55, r['sub'], 9.5, C_MUTED))
        for i, cell in enumerate(r['cells']):
            x = col_x(i)
            body.append(f'<rect x="{x}" y="{y+14}" width="{COL_W}" height="{ROW_H-28}" rx="6" fill="#ffffff" '
                        f'stroke="{C_STRK}"/>')
            ty = y + 36
            for j, ln in enumerate(cell):
                for k, w in enumerate(wrap(ln, 11, COL_W - 20)):
                    body.append(text(x + 10, ty, w, 11, C_TEXT, '600' if j == 0 and k == 0 else 'normal'))
                    ty += 15
                ty += 1
            if i < 3:
                ax = x + COL_W + 1
                body.append(f'<path d="M {ax} {y+ROW_H/2:.1f} h {GAP-4}" stroke="{C_STRK}" stroke-width="1.4"/>')
                body.append(f'<path d="M {ax+GAP-7} {y+ROW_H/2-3:.1f} l 3 3 l -3 3" fill="none" '
                            f'stroke="{C_STRK}" stroke-width="1.4"/>')
        row_y += ROW_H + 12

    # 结论条：按实际换行行数定高（英文一行放唔落）
    cy = row_y + 6
    c_lines = wrap(spec['concl_body'], 10.8, W - 40 - 40)
    bar_h = 26 + len(c_lines) * 15 + 10
    body.append(f'<rect x="20" y="{cy}" width="{W-40}" height="{bar_h}" rx="8" fill="{C_ACC_FILL}" '
                f'stroke="{C_ACC}"/>')
    body.append(text(38, cy + 24, spec['concl_head'], 11.5, C_ACC, '700'))
    ty = cy + 43
    for ln in c_lines:
        body.append(text(38, ty, ln, 10.8, C_TEXT))
        ty += 15

    H = int(cy + bar_h + 18)
    head = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
            f'role="img" aria-label="{esc(spec["title"])}">',
            f'<rect width="{W}" height="{H}" fill="#ffffff"/>',
            f'<rect x="0" y="0" width="{W}" height="3" fill="{C_ACC}"/>',
            text(20, 36, spec['title'], 16.5, C_TEXT, '700'),
            text(20, 55, spec['sub'], 10.5, C_SUB),
            f'<line x1="20" y1="68" x2="{W-20}" y2="68" stroke="{C_STRK}"/>']
    return '\n'.join(head + body + ['</svg>'])


outdir = pathlib.Path(__file__).resolve().parent / 'img'
outdir.mkdir(parents=True, exist_ok=True)
for lang, spec in SPEC.items():
    p = outdir / spec['out']
    p.write_text(render(spec), encoding='utf-8')
    print(f'[{lang}] {p.name} {p.stat().st_size} bytes; col_w {COL_W:.1f}')
