"""Exploratory: accuracy of data-learned groups by number of groups, and how many groups match the chosen type vector. No API calls."""
import sys, json, warnings; sys.path.insert(0,'scripts/suite'); sys.path.insert(0,'src')
import numpy as np; from sklearn.cluster import KMeans
from trait_search_greedy import load, arrays, table, predict
warnings.filterwarnings("ignore")
DS=["npas","riasec","mach","dass","fti","nis","gss2022","wvs7"]; KS=[1,2,3,4,6,9,14,27,54]
print("Accuracy on half B by number of data-learned groups (exploratory; data assignment, most common answer of the group)")
print("| Survey | "+" | ".join(f"k={k}" for k in KS)+" | Type vector | Groups needed to match the type vector |\n|---|"+"---|"*(len(KS)+2))
for ds in DS:
    people, rep, idx = load(ds); ans, tgt, truth = arrays(people, idx); A=np.arange(len(people))%2==0; B=~A; I=len(idx); keys=sorted(idx,key=idx.get)
    rngs=np.array([max(1,rep[k]["scale"]["max"]-rep[k]["scale"]["min"]) for k in keys])
    X=ans.astype(float); X[ans<0]=np.nan; cm=np.nanmean(X[A],0); X=np.where(np.isnan(X),cm,X)/rngs
    Bi=np.where(B)[0]; Aidx=np.where(A)[0]; obs=ans>=0
    mode=np.array([np.bincount(ans[A,i][ans[A,i]>=0]).argmax() for i in range(I)])
    gpath=json.load(open(f"outputs/suite/{ds}/greedy_bigfive.json")); best=tuple(max(gpath,key=lambda s:s["accA"])["subset"])
    tv=100*np.mean((predict(table(ds,"bigfive",best,rep,None),idx,rep,ans,tgt)==truth)[B])
    accs=[]
    for k in KS:
        if k==1: accs.append(100*np.mean(truth[Bi]==mode[tgt[Bi]])); continue
        km=KMeans(n_clusters=k,n_init=10,random_state=0).fit(X[A]); C=km.cluster_centers_
        lab=np.array([np.nanargmin([np.nanmean(np.where(obs[n]&(np.arange(I)!=tgt[n]),(X[n]-C[c])**2,np.nan)) for c in range(k)]) for n in Bi])
        pred=[]
        for j,n in enumerate(Bi):
            v=ans[Aidx[km.labels_==lab[j]],tgt[n]]; v=v[v>=0]; pred.append(np.bincount(v).argmax() if len(v) else mode[tgt[n]])
        accs.append(100*np.mean(np.array(pred)==truth[Bi]))
    need=next((k for k,a in zip(KS,accs) if a>=tv), None)
    print(f"| {ds} | "+" | ".join(f"{a:.1f}" for a in accs)+f" | {tv:.1f} | {need if need else '>54'} |")
