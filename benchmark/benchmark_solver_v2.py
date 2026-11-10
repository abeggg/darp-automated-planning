from dataclasses import dataclass
from math import hypot, inf
from collections import deque
from heapq import heappush, heappop
from itertools import count
import time, csv

@dataclass(frozen=True)
class Instance:
    name: str
    coords: tuple
    vehicle_locs: tuple
    capacities: tuple
    origins: tuple
    dests: tuple

def distances(coords):
    return tuple(tuple(0 if i == j else max(1, round(hypot(coords[i][0]-coords[j][0], coords[i][1]-coords[j][1]))) for j in range(len(coords))) for i in range(len(coords)))

def successors(I, D, state):
    vehicle_locs, status = state
    onboard_count = [0] * len(vehicle_locs)
    for s in status:
        if s >= 0:
            onboard_count[s] += 1
    for v, loc in enumerate(vehicle_locs):
        # Drop-offs first (zero-cost and often goal-progressing)
        for p, s in enumerate(status):
            if s == v and I.dests[p] == loc:
                ns = list(status); ns[p] = -2
                yield (vehicle_locs, tuple(ns)), ('dropoff', v, p, loc), 0
        # Pick-ups when capacity permits
        if onboard_count[v] < I.capacities[v]:
            for p, s in enumerate(status):
                if s == -1 and I.origins[p] == loc:
                    ns = list(status); ns[p] = v
                    yield (vehicle_locs, tuple(ns)), ('pickup', v, p, loc), 0
        # PDDL allows driving to every connected location. The synthetic instances use complete graphs.
        for dst in range(len(I.coords)):
            if dst == loc:
                continue
            nv = list(vehicle_locs); nv[v] = dst
            yield (tuple(nv), status), ('drive', v, loc, dst), D[loc][dst]

def floyd_warshall(D):
    dist=[list(r) for r in D]
    n=len(dist)
    for k in range(n):
        for i in range(n):
            dik=dist[i][k]
            for j in range(n):
                nd=dik+dist[k][j]
                if nd<dist[i][j]: dist[i][j]=nd
    return tuple(tuple(r) for r in dist)

def h(I, D, state):
    # Admissible lower bound using all-pairs shortest paths: each remaining passenger needs
    # at least vehicle->origin + origin->destination if waiting, or vehicle->destination if onboard.
    SP=floyd_warshall(D)
    vehicle_locs, status = state
    bounds=[]
    for p,s in enumerate(status):
        if s == -2: continue
        if s == -1:
            bounds.append(min(SP[vehicle_locs[v]][I.origins[p]] for v in range(len(vehicle_locs))) + SP[I.origins[p]][I.dests[p]])
        else:
            bounds.append(SP[vehicle_locs[s]][I.dests[p]])
    return max(bounds, default=0)

def goal(s): return all(x == -2 for x in s[1])

def solve(I, algorithm, timeout=5.0):
    D=distances(I.coords); s0=(I.vehicle_locs, tuple([-1]*len(I.origins)))
    parent={s0:(None,None)}; g={s0:0}; expanded=generated=0; t0=time.perf_counter()
    def plan(st):
        a=[]
        while parent[st][0] is not None:
            prev,act=parent[st]; a.append(act); st=prev
        return list(reversed(a))
    if algorithm == 'BFS':
        q=deque([s0]); seen={s0}
        while q:
            if time.perf_counter()-t0 > timeout: return None, expanded, generated, timeout, None
            st=q.popleft(); expanded += 1
            if goal(st):
                p=plan(st); return p, expanded, generated, time.perf_counter()-t0, sum(D[a[2]][a[3]] for a in p if a[0]=='drive')
            for ns,act,c in successors(I,D,st):
                generated += 1
                if ns not in seen:
                    seen.add(ns); parent[ns]=(st,act); q.append(ns)
        return None,expanded,generated,time.perf_counter()-t0,None
    pq=[]; serial=count(); closed=set()
    h0=0 if algorithm=='UCS' else h(I,D,s0)
    heappush(pq, (h0, 0, next(serial), s0))
    while pq:
        if time.perf_counter()-t0 > timeout: return None, expanded, generated, timeout, None
        pri, gs, _, st = heappop(pq)
        if st in closed: continue
        closed.add(st); expanded += 1
        if goal(st): return plan(st), expanded, generated, time.perf_counter()-t0, g[st]
        for ns,act,c in successors(I,D,st):
            generated += 1; ng=g[st]+c
            if ng < g.get(ns, inf):
                g[ns]=ng; parent[ns]=(st,act)
                hv=h(I,D,ns)
                priority = ng if algorithm=='UCS' else (ng+hv if algorithm=='A*' else hv)
                heappush(pq,(priority,ng,next(serial),ns))
    return None,expanded,generated,time.perf_counter()-t0,None

instances=[
Instance('Facil', ((0,0),(3,0),(3,4)), (0,), (1,), (1,), (2,)),
Instance('Medio', ((0,0),(2,1),(5,1),(6,4),(1,5)), (0,), (2,), (1,2,4), (3,4,1)),
Instance('Dificil', ((0,0),(1,0),(2,0),(8,0),(9,0),(10,0),(5,3)), (0,5), (1,2), (1,2,4,5,3), (2,1,5,4,6)),
Instance('Muito dificil', ((0,0),(2,0),(5,0),(8,1),(8,5),(5,7),(2,7),(0,5),(4,3)), (0,3,7), (1,2,2), (1,2,5,6,8,4,7,1), (5,6,3,2,0,7,4,8)),
]

if __name__ == '__main__':
    print('instance,algorithm,solved,actions,cost,expanded,generated,time_s')
    for I in instances:
        for alg in ['BFS','UCS','A*','GBFS']:
            p,e,g,t,c=solve(I,alg)
            print(f'{I.name},{alg},{p is not None},{len(p) if p else ""},{c if c is not None else ""},{e},{g},{t:.6f}')
