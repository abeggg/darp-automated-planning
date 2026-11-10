from functools import lru_cache
from math import inf
from benchmark_solver_v2 import instances, distances, floyd_warshall


def single_vehicle_subset_cost(I, SP, v, subset_mask):
    n=len(I.origins)
    cap=I.capacities[v]
    start=I.vehicle_locs[v]
    if subset_mask==0:
        return 0, []

    # state: current location, picked mask, delivered mask (only subset bits matter)
    @lru_cache(None)
    def dp(loc, picked, delivered):
        if delivered == subset_mask:
            return 0, ()
        best=(inf, ())
        load=(picked & ~delivered).bit_count()
        # pickup an unpicked request in subset if capacity available
        if load < cap:
            todo=subset_mask & ~picked
            p=0
            while todo:
                lsb=todo & -todo; p=(lsb.bit_length()-1); todo-=lsb
                dst=I.origins[p]
                rest, seq=dp(dst, picked|lsb, delivered)
                val=SP[loc][dst]+rest
                if val < best[0]: best=(val, (('pickup',p,dst),)+seq)
        # deliver any onboard request
        onboard=(picked & ~delivered)
        while onboard:
            lsb=onboard & -onboard; p=(lsb.bit_length()-1); onboard-=lsb
            dst=I.dests[p]
            rest, seq=dp(dst, picked, delivered|lsb)
            val=SP[loc][dst]+rest
            if val < best[0]: best=(val, (('dropoff',p,dst),)+seq)
        return best
    return dp(start,0,0)


def exact_multi_vehicle(I):
    D=distances(I.coords); SP=floyd_warshall(D)
    n=len(I.origins); k=len(I.vehicle_locs); full=(1<<n)-1
    costs=[]; seqs=[]
    for v in range(k):
        vc=[]; vs=[]
        for mask in range(1<<n):
            c,s=single_vehicle_subset_cost(I,SP,v,mask)
            vc.append(c); vs.append(s)
        costs.append(vc); seqs.append(vs)
    # partition requests among vehicles; each request assigned exactly once
    @lru_cache(None)
    def part(v, remaining):
        if v==k:
            return (0, ()) if remaining==0 else (inf, ())
        best=(inf, ())
        sub=remaining
        while True:
            c=costs[v][sub]
            rest, assign=part(v+1, remaining^sub)
            val=c+rest
            if val<best[0]: best=(val,(sub,)+assign)
            if sub==0: break
            sub=(sub-1)&remaining
        return best
    val, assignment=part(0,full)
    return val, assignment, [seqs[v][assignment[v]] for v in range(k)], SP

if __name__=='__main__':
    for I in instances:
        val,assign,seqs,SP=exact_multi_vehicle(I)
        print(I.name, 'OPT=',val, 'assignment=',assign)
        for v,(m,seq) in enumerate(zip(assign,seqs)):
            ps=[i+1 for i in range(len(I.origins)) if m>>i & 1]
            print(' v'+str(v+1),'passengers',ps,'sequence',seq)
