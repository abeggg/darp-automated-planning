from exact_oracle import exact_multi_vehicle
from benchmark_solver_v2 import instances, distances
import os
from pathlib import Path

def fw_with_next(D):
    n=len(D); dist=[list(r) for r in D]; nxt=[[None]*n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            if i!=j: nxt[i][j]=j
    for k in range(n):
        for i in range(n):
            for j in range(n):
                nd=dist[i][k]+dist[k][j]
                if nd<dist[i][j]:
                    dist[i][j]=nd; nxt[i][j]=nxt[i][k]
    return dist,nxt

def path(u,v,nxt):
    if u==v: return [u]
    if nxt[u][v] is None: raise ValueError('no path')
    p=[u]
    while u!=v:
        u=nxt[u][v]; p.append(u)
    return p

def plan_for_instance(I):
    opt,assign,seqs,SP=exact_multi_vehicle(I)
    D=distances(I.coords); _,nxt=fw_with_next(D)
    all_actions=[]; total=0
    for v,seq in enumerate(seqs):
        loc=I.vehicle_locs[v]
        free=[f's{v+1}_{i+1}' for i in range(I.capacities[v])]
        seat_of={}
        for typ,p,target in seq:
            pp=path(loc,target,nxt)
            for a,b in zip(pp,pp[1:]):
                all_actions.append(f'(drive v{v+1} l{a} l{b})')
                total+=D[a][b]; loc=b
            if typ=='pickup':
                s=free.pop(0); seat_of[p]=s
                all_actions.append(f'(pickup p{p+1} v{v+1} l{target} {s})')
            else:
                s=seat_of.pop(p); free.append(s); free.sort()
                all_actions.append(f'(dropoff p{p+1} v{v+1} l{target} {s})')
    return opt,total,all_actions,assign

BASE = Path(__file__).resolve().parent.parent
PLANS = BASE / 'plans'
PLANS.mkdir(parents=True, exist_ok=True)
for I in instances:
    opt,total,acts,assign=plan_for_instance(I)
    fn=I.name.lower().replace(' ','-').replace('í','i').replace('é','e').replace('á','a')+'.plan'
    with open(PLANS / fn,'w') as f:
        f.write('\n'.join(acts)+'\n')
    print(I.name, 'opt',opt,'expanded plan cost',total,'actions',len(acts),'assign',assign,'file',fn)
    print('\n'.join(acts[:12]), '\n...')
