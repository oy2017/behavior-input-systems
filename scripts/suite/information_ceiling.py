"""Information ceiling, independent of grouping: a supervised model predicts a test person's held-out answer from their
other answers directly (HistGradientBoosting, trained on the training half with every observed answer masked in turn as
a label; the item id is a feature). Compared with the floor (most common answer) and the group ceiling (27 k-means
groups' most common answer) on the same test half. The gap between the two ceilings is the cost of reducing a person to
one of 27 kinds, a design choice, not the data's limit. No API calls."""
import sys, json, warnings; sys.path.insert(0,'scripts/suite'); sys.path.insert(0,'src')
import numpy as np
from sklearn.ensemble import HistGradientBoostingClassifier
from roundtrip import stats, K, NAME
warnings.filterwarnings("ignore")
rng=np.random.default_rng(0)
print("| Questionnaire | Floor | Group ceiling (27 groups) | Information ceiling (supervised, all other answers) | Pairwise corr of target with other items, mean abs |\n|---|---|---|---|---|")
out={}
for ds in ["npas","riasec","mach","dass","fti","nis","gss2022","wvs7"]:
    S=stats(ds); ans,tgt,truth,A,B,km,I=S["ans"],S["tgt"],S["truth"],S["A"],S["B"],S["km"],S["I"]
    Aidx=np.where(A)[0]; Bi=np.where(B)[0]; obs=ans>=0
    mode=np.array([np.bincount(ans[A,i][ans[A,i]>=0]).argmax() for i in range(I)])
    floor=100*np.mean(mode[tgt[Bi]]==truth[Bi])
    C=km.cluster_centers_; X=S["X"]
    lab=np.array([np.nanargmin([np.nanmean(np.where(obs[n]&(np.arange(I)!=tgt[n]),(X[n]-C[k])**2,np.nan)) for k in range(K)]) for n in Bi])
    gpred=[]
    for j,n in enumerate(Bi):
        v=ans[Aidx[km.labels_==lab[j]],tgt[n]]; v=v[v>=0]; gpred.append(np.bincount(v).argmax() if len(v) else mode[tgt[n]])
    gceil=100*np.mean(np.array(gpred)==truth[Bi])
    # supervised: training rows = (person in A, item j observed) with j masked
    rows=[]; labels=[]
    for n in Aidx:
        for j in np.where(obs[n])[0]:
            x=ans[n].astype(float).copy(); x[~obs[n]]=np.nan; x[j]=np.nan; rows.append(np.concatenate([[j],x])); labels.append(ans[n,j])
    rows=np.array(rows); labels=np.array(labels)
    if len(rows)>120000: sel=rng.choice(len(rows),120000,replace=False); rows,labels=rows[sel],labels[sel]
    clf=HistGradientBoostingClassifier(max_iter=300,learning_rate=0.08,categorical_features=[0],random_state=0).fit(rows,labels)
    Xb=[]
    for n in Bi:
        x=ans[n].astype(float).copy(); x[~obs[n]]=np.nan; x[tgt[n]]=np.nan; Xb.append(np.concatenate([[tgt[n]],x]))
    sceil=100*np.mean(clf.predict(np.array(Xb))==truth[Bi])
    # population level without having asked: mean predicted probability vector per item vs the real test distribution
    lo=np.array([S["rep"][k]["scale"]["min"] for k in S["keys"]]); hi=np.array([S["rep"][k]["scale"]["max"] for k in S["keys"]])
    Wp=[]; SR=[]
    for i in range(I):
        real=ans[Bi,i]; real=real[real>=0]
        if len(real)<5: continue
        who=Bi[obs[Bi,i]]; Xi=[]
        for n in who:
            x=ans[n].astype(float).copy(); x[~obs[n]]=np.nan; x[i]=np.nan; Xi.append(np.concatenate([[i],x]))
        P=clf.predict_proba(np.array(Xi)); cls=clf.classes_
        vals=np.arange(lo[i],hi[i]+1); synth=np.zeros(len(vals))
        for j,cv in enumerate(cls):
            if lo[i]<=cv<=hi[i]: synth[int(cv)-lo[i]]+=P[:,j].sum()
        synth/=synth.sum(); rh=np.bincount(real,minlength=hi[i]+1)[lo[i]:hi[i]+1]/len(real)
        Wp.append(100*np.abs(np.cumsum(rh)-np.cumsum(synth)).sum()/max(1,hi[i]-lo[i]))
        m=lambda q:(vals*q).sum(); sd=lambda q:np.sqrt(((vals-m(q))**2*q).sum()); SR.append(sd(synth)/sd(rh))
    popW=float(np.mean(Wp)); popSR=float(np.mean(SR))
    # pairwise correlation of each item with the others (training half), mean abs, averaged over target items weighted by B counts
    H=ans[A].astype(float); H[ans[A]<0]=np.nan
    cm=np.ma.corrcoef(np.ma.masked_invalid(H),rowvar=False).filled(np.nan); np.fill_diagonal(cm,np.nan)
    w=np.bincount(tgt[Bi],minlength=I); corr=np.nansum(np.nanmean(np.abs(cm),1)*w)/w.sum()
    out[ds]=dict(floor=floor,group_ceiling=gceil,info_ceiling=sceil,mean_abs_corr=corr,pop_W_info=popW,pop_sd_info=popSR)
    print(f"| {NAME[ds]} | {floor:.1f} | {gceil:.1f} | {sceil:.1f} | {corr:.2f} | population W without asking {popW:.1f} [{popSR:.2f}] |")
json.dump(out,open("outputs/information_ceiling.json","w"),indent=1)
