"""Reproducible KNN/mean experiment. All output stays beside this script on D:."""
from pathlib import Path
import argparse, csv, json, hashlib
import numpy as np
from PIL import Image
from numpy.lib.stride_tricks import sliding_window_view
ROOT=Path(__file__).resolve().parent

def filters(y,w,ks):
    # Channel-wise intensity KNN, unchanged input, replicated borders, stable ties.
    if y.ndim==2:y=y[:,:,None]
    out={k:np.empty_like(y) for k in ks}; avg=np.empty_like(y)
    for c in range(y.shape[2]):
        padded=np.pad(y[:,:,c],w//2,mode='edge')
        for start in range(0,y.shape[0],32):
            end=min(start+32,y.shape[0])
            windows=sliding_window_view(padded[start:end+w-1],(w,w)).reshape(end-start,y.shape[1],w*w)
            avg[start:end,:,c]=windows.mean(-1)
            order=np.argsort((windows-y[start:end,:,c,None])**2,axis=-1,kind='stable')
            sums=np.cumsum(np.take_along_axis(windows,order,-1),axis=-1)
            for k in ks:out[k][start:end,:,c]=sums[:,:,k-1]/k
    return out,avg

def noise(x,p,seed):
    # Independent RGB samples; sigma defined per original channel mean.
    sigma=p*x.mean(axis=(0,1),keepdims=True)
    return x+np.random.default_rng(seed).uniform(-1,1,x.shape)*np.sqrt(3)*sigma

def mse(x,y):return float(np.mean((x-y)**2))
def save_csv(path,rows):
    with path.open('w',newline='',encoding='utf-8') as f:
        wr=csv.DictWriter(f,rows[0].keys());wr.writeheader();wr.writerows(rows)
def png(path,a):
    a=np.uint8(np.clip(np.rint(a),0,255))
    Image.fromarray(a.squeeze() if a.shape[-1]==1 else a).save(path)

def verify():
    from core_manual import smooth_both
    a=np.random.default_rng(3).integers(0,30,(8,9)).astype(float)
    for w in (3,5,7):
        for k in (1,w*w//2,w*w):
            out,avg=filters(a,w,[k]); ref,mean=smooth_both(a.tolist(),w,k)
            np.testing.assert_allclose(out[k][:,:,0],ref,atol=1e-12)
            np.testing.assert_allclose(avg[:,:,0],mean,atol=1e-12)
    print('9 manual-reference equivalence checks passed.',flush=True)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--k',type=int);ap.add_argument('--window',type=int,default=5)
    args=ap.parse_args()
    if args.k is not None and (args.window<1 or args.window%2==0 or not 1<=args.k<=args.window**2):ap.error('Require odd positive window and 1 <= k <= window squared.')
    folder=ROOT/('results' if args.k is None else f'results_w{args.window}_k{args.k}');folder.mkdir(exist_ok=True)
    verify(); allrows=[]; sweeps=[]; settings=[];manifest=[]
    for name in ('farmland','urban'):
        path=ROOT/'data'/f'{name}.png'; x=np.array(Image.open(path),dtype=float)
        if x.ndim==2:x=x[:,:,None]
        manifest.append({'name':name,'shape':list(x.shape),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'channel_means':x.mean((0,1)).tolist()})
        for pct in (5,10,20):
            if args.k is None:
                y=noise(x,pct/100,60700)
                candidates=[]
                for w in (3,5,7):
                    ks=sorted(set([max(2,round(w*w*f)) for f in (.35,.55,.75,.9)]))
                    outs,avg=filters(y,w,ks)
                    for k in ks:
                        r={'image':name,'noise_percent':pct,'window':w,'k':k,'knn_mse':mse(x,outs[k]),'mean_mse':mse(x,avg)}
                        candidates.append(r);sweeps.append(r)
                # Same window for both, neutral joint reconstruction objective.
                best=min(candidates,key=lambda r:(r['knn_mse']+r['mean_mse'])/2)
                w,k=best['window'],best['k']
            else:w,k=args.window,args.k
            settings.append({'image':name,'noise_percent':pct,'window':w,'k':k})
            for trial in (1,2,3):
                y=noise(x,pct/100,60700+trial);out,avg=filters(y,w,[k]);knn=out[k]
                baseline,_=filters(y,5,[9])
                r={'image':name,'noise_percent':pct,'trial':trial,'seed':60700+trial,'window':w,'k':k,'noisy_mse':mse(x,y),'knn_mse':mse(x,knn),'mean_mse':mse(x,avg),'old_setting_knn_mse':mse(x,baseline[9])}
                allrows.append(r)
                if trial==1:
                    prefix=f'{name}_{pct}'
                    np.savez_compressed(folder/f'{prefix}.npz',original=x,noisy=y,knn=knn,mean=avg)
                    for method,arr in [('original',x),('noisy',y),('knn',knn),('mean',avg)]:
                        png(folder/f'{prefix}_{method}.png',arr)
                        # Fixed central 192x192 detail region for all methods/levels.
                        png(folder/f'{prefix}_{method}_crop.png',arr[288:480,288:480])
            print(name,pct,'window',w,'k',k,flush=True)
    save_csv(folder/'trials.csv',allrows)
    if sweeps:save_csv(folder/'parameter_sweep.csv',sweeps)
    summary=[]
    for setting in settings:
        subset=[r for r in allrows if r['image']==setting['image'] and r['noise_percent']==setting['noise_percent']]
        row=dict(setting)
        for method in ('noisy','knn','mean','old_setting_knn'):
            scores=[r[method+'_mse'] for r in subset];row[method+'_mse']=float(np.mean(scores));row[method+'_sd']=float(np.std(scores,ddof=1))
        summary.append(row)
    save_csv(folder/'summary.csv',summary)
    (folder/'manifest.json').write_text(json.dumps({'images':manifest,'selection':'Minimum average of KNN and mean validation MSE; paired window; per image and noise level. Validation seed 60700. Test seeds 60701,60702,60703. Same images, independent noise; not unseen-scene validation.','display':'Fixed 0..255; clipping/rounding only PNG export. NPZ arrays and MSE unmodified.','settings':settings},indent=2))
    print(json.dumps(summary,indent=2),flush=True)
if __name__=='__main__':main()
