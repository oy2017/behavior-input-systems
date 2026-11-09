"""Exploratory audit of the sketch condition: items where the model moves a described group the wrong way. No API calls."""
import sys, json, warnings; sys.path.insert(0,'scripts/suite'); sys.path.insert(0,'src')
import numpy as np
from roundtrip import stats, K, NAME
warnings.filterwarnings("ignore")
DS=["npas","riasec","mach","dass","fti","nis","gss2022","wvs7"]
print("Exploratory audit of the sketch condition: items where the model moves a described group the wrong way (groups departing > 0.3 sd)\n")
tot_bad=tot=0
for ds in DS:
    S=stats(ds); I=S["I"]; keys=S["keys"]; mu,sd,G=S["mu"],S["sd"],S["G"]
    rows=[json.loads(l) for l in open(f"outputs/type_table/search/{ds}/roundtrip__prose12.jsonl")]
    d={}
    for r in rows:
        if r["choice"] is not None: d.setdefault((r["cluster"],r["item"]),[]).append(r["choice"])
    R=np.full((K,I),np.nan)
    for (c,k),v in d.items(): R[c,S["idx"][k]]=np.median(v)
    zR=(R-mu)/sd; zG=(G-mu)/sd; big=(np.abs(zG)>0.3)&~np.isnan(zR)
    wrong=(np.sign(zR)!=np.sign(zG))&big
    tot_bad+=wrong.sum(); tot+=big.sum()
    per=[(wrong[:,i].sum()/max(1,big[:,i].sum()), big[:,i].sum(), i) for i in range(I) if big[:,i].sum()>=5]
    per.sort(reverse=True)
    print(f"**{NAME[ds]}** ({100*wrong.sum()/big.sum():.0f}% of group-item departures go the wrong way)")
    for frac,n,i in per[:3]:
        k=keys[i]; txt=S["rep"][k]["items"][k]["text"]; 
        # direction summary: groups where humans go up but model goes down, vs the reverse
        up_dn=((zG[:,i]>0)&(zR[:,i]<0)&big[:,i]).sum(); dn_up=((zG[:,i]<0)&(zR[:,i]>0)&big[:,i]).sum()
        print(f"- {100*frac:.0f}% wrong of {n} groups: \"{txt[:110]}\" (humans higher but model lower: {up_dn}; humans lower but model higher: {dn_up})")
    print()
print(f"Overall: {100*tot_bad/tot:.0f}% of {tot} group-item departures go the wrong way.")
