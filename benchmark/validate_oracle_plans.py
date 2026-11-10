import re, os
from pathlib import Path
from benchmark_solver_v2 import instances, distances

FILES={'Facil':'facil.plan','Medio':'medio.plan','Dificil':'dificil.plan','Muito dificil':'muito-dificil.plan'}

def validate(I, path):
    D=distances(I.coords)
    vloc=list(I.vehicle_locs)
    waiting={p:I.origins[p] for p in range(len(I.origins))}
    onboard={}
    served=set()
    free={v:[f's{v+1}_{i+1}' for i in range(I.capacities[v])] for v in range(len(I.vehicle_locs))}
    seat_owner={}
    cost=0
    with open(path) as f:
        acts=[line.strip() for line in f if line.strip() and not line.startswith(';')]
    for step,a in enumerate(acts,1):
        toks=a.strip('()').split(); op=toks[0]
        try:
            if op=='drive':
                _,vv,ff,tt=toks; v=int(vv[1:])-1; fr=int(ff[1:]); to=int(tt[1:])
                assert vloc[v]==fr, f'vehicle not at from: {vloc[v]} != {fr}'
                vloc[v]=to; cost+=D[fr][to]
            elif op=='pickup':
                _,pp,vv,ll,ss=toks; p=int(pp[1:])-1; v=int(vv[1:])-1; loc=int(ll[1:])
                assert waiting.get(p)==loc, 'passenger not waiting at origin'
                assert I.origins[p]==loc, 'wrong origin'
                assert vloc[v]==loc, 'vehicle not at pickup'
                assert ss in free[v], 'seat not free/owned by vehicle'
                free[v].remove(ss); seat_owner[p]=ss; del waiting[p]; onboard[p]=v
            elif op=='dropoff':
                _,pp,vv,ll,ss=toks; p=int(pp[1:])-1; v=int(vv[1:])-1; loc=int(ll[1:])
                assert onboard.get(p)==v, 'passenger not onboard this vehicle'
                assert I.dests[p]==loc, 'wrong destination'
                assert vloc[v]==loc, 'vehicle not at dropoff'
                assert seat_owner.get(p)==ss, 'wrong seat'
                del onboard[p]; del seat_owner[p]; free[v].append(ss); served.add(p)
            else: raise AssertionError('unknown action')
        except AssertionError as e:
            return False, cost, step, f'{a}: {e}'
    ok=(len(served)==len(I.origins) and not waiting and not onboard)
    return ok,cost,len(acts),'' if ok else 'goal not reached'

BASE = Path(__file__).resolve().parent.parent
for I in instances:
    p=BASE / 'plans' / FILES[I.name]
    print(I.name, validate(I,p))
