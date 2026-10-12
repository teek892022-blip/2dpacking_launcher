#!/usr/bin/env python3
"""Unofficial local 2D launcher for yoheinakajima/soft-to-rigid.
Generated with OpenAI ChatGPT under human direction. Standard library only.
"""
import argparse
import datetime as dt
import json
import math
import os
from pathlib import Path
import secrets
import shutil
import subprocess
import sys
import uuid
import time
import webbrowser

FAMILIES = ('squ-in-squ', 'squ-in-cir', 'squ-in-tri', 'tri-in-tri',
            'tri-in-squ', 'hex-in-squ', 'cir-in-squ')
METHODS = ('harden', 'grow', 'rigid', 'sa', 'pc')

VIEWER = r'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Soft-to-Rigid — Local 2D Replay</title><style>
:root{font:16px system-ui,Segoe UI,sans-serif;color:#e7ebf7;background:#101724}body{margin:0 auto;padding:24px;max-width:1050px}h1{font-size:1.5rem;margin:0}p{color:#a9b7d0}
main{background:#182235;border:1px solid #30435d;padding:18px;border-radius:16px;margin-top:16px}canvas{display:block;width:100%;aspect-ratio:1.4;background:#0b1320;border-radius:10px}
.controls{display:flex;gap:12px;align-items:center;margin-top:15px;flex-wrap:wrap}input[type=range]{flex:1;min-width:180px}button{background:#3b82f6;color:white;border:0;border-radius:8px;padding:9px 17px;cursor:pointer}#meta{color:#bfd2f2;font-variant-numeric:tabular-nums}small{color:#9db0ce}
</style></head><body><h1>Soft-to-Rigid — Local 2D Replay</h1><p id="info"></p><main><canvas id="view" width="1000" height="710"></canvas><div class="controls"><button id="play">Play</button><input id="seek" type="range" min="0" value="0"><span id="meta"></span></div></main><p><small>Frames are embedded locally; no server or external JavaScript library is needed. Drag the timeline to scrub.</small></p>
<script id="data" type="application/json">__DATA__</script><script>
'use strict';const D=JSON.parse(document.getElementById('data').textContent),C=document.getElementById('view'),ctx=C.getContext('2d');
const seek=document.getElementById('seek'),meta=document.getElementById('meta'),btn=document.getElementById('play');
let at=0,playing=false,last=0,progress=0;
const FPS=60, FRAME_MS=1000/FPS, SEGMENT_MS=90;
const fr=D.frames||[];seek.max=Math.max(fr.length-1,0);document.getElementById('info').textContent=`${D.family} · ${D.method} · n=${D.n} · seed=${D.seed} · certified L=${Number(D.L).toFixed(9)} · ${fr.length} frames`;
function usable(f){return f&&Array.isArray(f.p)&&f.p.length>=D.n*3&&f.p.some((v,i)=>i%3!==2&&Number.isFinite(v));}
function visibleScale(f){
 // During harden/compress, the upstream soft-body radius may collapse to zero.
 // Keep a display-only minimum so the pieces remain visible; do not alter simulation data.
 const raw=Number(f.g);
 return Number.isFinite(raw)?Math.max(Math.abs(raw),0.22):1;
}
function findValid(i,dir){while(i>=0&&i<fr.length){if(usable(fr[i]))return fr[i];i+=dir;}return null;}
function interpolate(a,b,t){if(!a)return b;if(!b)return a;
 const p=a.p.map((v,i)=>{if(i%3===2){let delta=((b.p[i]-v+Math.PI)%(2*Math.PI)+2*Math.PI)%(2*Math.PI)-Math.PI;return v+delta*t;}return v+(b.p[i]-v)*t;});
 return {...a,p,L:(a.L??b.L)+((b.L??a.L)-(a.L??b.L))*t,g:(a.g??1)+((b.g??1)-(a.g??1))*t,u:(a.u??0)+((b.u??0)-(a.u??0))*t};}
function draw(){
 const a=findValid(at,-1)||findValid(at,1);
 const b=findValid(at+1,1)||a;
 const f=interpolate(a,b,playing?progress:0);
 if(!f)return;const W=C.width,H=C.height;ctx.clearRect(0,0,W,H);let L=Math.max(Number.isFinite(Number(f.L))?Number(f.L):1,0.1);const scale=Math.min(W*.78,H*.78)/(D.container==='circle'?2*L:L);const ox=W/2,oy=H/2;
const point=(x,y)=>[ox+x*scale,oy-y*scale];
ctx.strokeStyle='#d9e4fc';ctx.lineWidth=2.3;ctx.beginPath();
if(D.container==='circle'){ctx.arc(ox,oy,L*scale,0,2*Math.PI)}else if(D.container==='square'){const [x,y]=point(-L/2,L/2);ctx.rect(x,y,L*scale,L*scale)}else{const h=L*Math.sqrt(3)/2;let pts=[[0,2*h/3],[-L/2,-h/3],[L/2,-h/3]];pts.forEach(([x,y],i)=>{let p=point(x,y);i?ctx.lineTo(...p):ctx.moveTo(...p)});ctx.closePath()}ctx.stroke();
const k={circle:0,triangle:3,square:4,pentagon:5,hexagon:6,octagon:8}[D.piece]??4;
for(let i=0;i<D.n;i++){let x=f.p[3*i],y=f.p[3*i+1],a=f.p[3*i+2],gamma=visibleScale(f),tau=Number.isFinite(Number(f.u))?Math.max(0,Math.min(1,Number(f.u))):0; if(!Number.isFinite(x)||!Number.isFinite(y))continue;
 const [px,py]=point(x,y);const color=i%2?'#f472b6':'#60a5fa';ctx.fillStyle=color;ctx.strokeStyle='#f5f7ff';ctx.lineWidth=1.15;
 if(k===0 || tau>=0.999999){
  // A fully softened polygon is a disk. A zero-length polygon path with a
  // thick stroke renders NOTHING on Canvas, so draw the disk explicitly.
  const radius=k===0 ? .5*gamma : gamma/(2*Math.tan(Math.PI/k));
  ctx.beginPath();ctx.arc(px,py,scale*radius,0,2*Math.PI);
  ctx.fill();ctx.stroke();continue;
 }
 const rho=1/(2*Math.tan(Math.PI/k)),R=1/(2*Math.sin(Math.PI/k)); const core=gamma*(1-tau),r=gamma*tau*rho;
 ctx.beginPath();for(let j=0;j<k;j++){let ang=-Math.PI/2-Math.PI/k+j*2*Math.PI/k+a;let xx=px+scale*core*R*Math.cos(ang),yy=py-scale*core*R*Math.sin(ang);if(j===0)ctx.moveTo(xx,yy);else ctx.lineTo(xx,yy)}ctx.closePath();
 if(r>0){ctx.lineJoin='round';ctx.lineCap='round';ctx.strokeStyle=color;ctx.lineWidth=2*r*scale;ctx.stroke();ctx.fill();ctx.strokeStyle='#f5f7ff';ctx.lineWidth=1;ctx.stroke()}else{ctx.fill();ctx.stroke()}
}
meta.textContent=`${at+1}/${fr.length} · ${f.ph} · step ${f.s} · L=${Number(f.L).toFixed(5)}`;seek.value=at;
}
seek.addEventListener('input',()=>{at=+seek.value;progress=0;draw()});
btn.addEventListener('click',()=>{playing=!playing;btn.textContent=playing?'Pause':'Play';last=0;if(playing)requestAnimationFrame(tick)});
function tick(t){if(!playing)return;if(last){progress+=(t-last)/SEGMENT_MS;while(progress>=1){progress-=1;at=(at+1)%fr.length;}}last=t;draw();requestAnimationFrame(tick)}draw();
</script></body></html>'''


def parse_args():
    p = argparse.ArgumentParser(description='Run 2D soft-to-rigid packing and open a local replay.')
    p.add_argument('--family', choices=FAMILIES, default='squ-in-squ', help='piece-in-container code')
    p.add_argument('--n', type=int, default=11, help='number of congruent pieces (default: 11)')
    p.add_argument('--method', choices=METHODS, default='harden')
    p.add_argument('--budget', type=float, default=1.0, help='positive scale for engine iteration budget')
    p.add_argument('--seed', type=int, default=17, help='unsigned 32-bit seed')
    p.add_argument('--random-seed', action='store_true', help='generate unpredictable seed(s), overriding --seed')
    p.add_argument('--trials', type=int, default=1, help='number of seeds to run (default: 1)')
    p.add_argument('--clean', action='store_true', help='remove launcher2d-* experiment folders and exit')
    p.add_argument('--clean-days', type=float, default=None, help='with --clean, remove only runs older than N days')
    p.add_argument('--no-browser', action='store_true', help='do not open local HTML replay')
    p.add_argument('--repo', type=Path, default=None, help='path to upstream repository (default: script directory)')
    args = p.parse_args()
    if args.clean_days is not None and (args.clean_days < 0 or not math.isfinite(args.clean_days)): p.error('--clean-days must be finite and >= 0')
    if args.clean_days is not None and not args.clean: p.error('--clean-days requires --clean')
    if args.n < 1 or args.n > 1000: p.error('--n must be 1..1000; large cases can be very slow')
    if args.budget <= 0 or not math.isfinite(args.budget): p.error('--budget must be finite and > 0')
    if args.trials < 1 or args.trials > 10000: p.error('--trials must be 1..10000')
    if not 0 <= args.seed <= 4294967295: p.error('--seed must be 0..4294967295')
    return args


def main():
    a = parse_args()
    root = (a.repo or Path(__file__).resolve().parent).resolve()
    if a.clean:
        campaigns = root / 'campaigns'
        if not campaigns.is_dir(): sys.exit(f'ERROR: Missing campaigns directory: {campaigns}')
        cutoff = time.time() - a.clean_days*86400 if a.clean_days is not None else None
        removed = 0
        for folder in sorted(campaigns.glob('launcher2d-*')):
            if not folder.is_dir() or folder.is_symlink(): continue
            if cutoff is not None and folder.stat().st_mtime >= cutoff: continue
            # Only launcher-owned experiment folders; never remove upstream campaigns.
            if not (folder/'plan.json').is_file(): continue
            try:
                plan_data=json.loads((folder/'plan.json').read_text(encoding='utf-8'))
            except (OSError, ValueError): continue
            if plan_data.get('id') != folder.name or plan_data.get('title') != 'Unofficial 2D launcher experiment': continue
            shutil.rmtree(folder)
            print('Removed:', folder)
            removed += 1
        print(f'Clean complete: {removed} launcher run folder(s) removed.')
        return
    for item in ('engine/run.js', 'engine/engine2d.js', 'catalog', 'methods', 'campaigns'):
        if not (root / item).exists():
            sys.exit(f'ERROR: {item} not found in {root}. Put the launcher in the upstream repository root, or use --repo PATH.')
    if not shutil.which('node'): sys.exit('ERROR: Node.js was not found in PATH.')
    catalog_path = root / 'catalog' / (a.family + '.json')
    if not catalog_path.is_file(): sys.exit(f'ERROR: Missing upstream catalog: {catalog_path}')
    family = json.loads(catalog_path.read_text(encoding='utf-8'))
    if family.get('dim') != 2: sys.exit('ERROR: This launcher supports 2D families only.')
    seeds = ([secrets.randbits(32) for _ in range(a.trials)] if a.random_seed else
             [((a.seed + i) & 0xffffffff) for i in range(a.trials)])
    # Upstream job IDs contain the seed. Duplicates could be skipped, so ensure distinct values.
    if len(set(seeds)) != len(seeds):
        seen = set()
        for i, seed in enumerate(seeds):
            while seed in seen: seed = (seed + 1) & 0xffffffff
            seeds[i] = seed; seen.add(seed)
    runid = dt.datetime.now().strftime('%Y%m%d-%H%M%S') + '-' + uuid.uuid4().hex[:8]
    folder = root / 'campaigns' / ('launcher2d-' + runid)
    folder.mkdir(parents=True, exist_ok=False)
    # Engine expects plan under campaigns/<campaign>/plan.json.
    plan = {'id': folder.name, 'title': 'Unofficial 2D launcher experiment',
            'instances': [{'family': a.family, 'ns': [a.n]}],
            'methods': [a.method], 'arms': [{'budget': a.budget, 'seeds': seeds}]}
    (folder / 'plan.json').write_text(json.dumps(plan, indent=2), encoding='utf-8')
    print('Family:', a.family, '| n:', a.n, '| method:', a.method, '| budget:', a.budget, flush=True)
    print('Seeds:', ', '.join(map(str, seeds)), flush=True)
    print('Run output:', folder, flush=True)
    cmd = ['node', str(root / 'engine' / 'run.js'), str(folder / 'plan.json'), '--worker', '0', '--of', '1']
    rc = subprocess.call(cmd, cwd=root)
    if rc: sys.exit(f'ERROR: upstream Node runner exited with status {rc}. Partial files remain in {folder}')
    results_file = folder / 'runs-w0.jsonl'
    if not results_file.exists(): sys.exit('ERROR: No run results created.')
    rows = [json.loads(l) for l in results_file.read_text(encoding='utf-8').splitlines() if l.strip()]
    ok = [r for r in rows if isinstance(r.get('L'), (float, int)) and math.isfinite(r['L'])]
    for r in rows:
        print(f"  seed {r['seed']}: " + (f"L={r['L']:.10f}" if 'L' in r else f"ERROR {r.get('error', 'unknown')}"))
    if not ok: sys.exit('ERROR: All trials failed; inspect runs-w0.jsonl')
    best = min(ok, key=lambda r: r['L'])
    print(f"BEST: seed={best['seed']} L={best['L']:.10f}")
    replay_dir = folder / 'replays'
    replays = list(replay_dir.glob('*.json'))
    if not replays: sys.exit('ERROR: Upstream runner did not write a replay.')
    # The upstream runner keeps the best replay per family/n/method/budget/config.
    replay = min((json.loads(f.read_text(encoding='utf-8')) for f in replays), key=lambda x: x['L'])
    if replay.get('seed') != best['seed']:
        print('WARNING: Best replay seed differs from lowest scored run.')
    html = VIEWER.replace('__DATA__', json.dumps(replay, separators=(',', ':'), ensure_ascii=False).replace('<', '\\u003c'))
    page = folder / 'replay.html'
    page.write_text(html, encoding='utf-8')
    print('Replay:', page)
    if not a.no_browser: webbrowser.open(page.as_uri())
    print('Done. This is an experimental numerical search, not a proof of optimality.')

if __name__ == '__main__':
    main()
