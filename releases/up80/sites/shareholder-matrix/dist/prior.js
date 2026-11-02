'use strict';
// A window switch is atomic: never relabel the old window's curves as the new one.
window.PRIOR_RESEARCH={days:60,pending:false,datasets:window.RESEARCH_DATASETS,stability:window.STABILITY_DATA};
(()=>{
 const cache=new Map([[60,Promise.resolve({datasets:window.RESEARCH_DATASETS,stability:window.STABILITY_DATA})]]);let serial=0;
 const control=document.getElementById('prior-window'),status=document.getElementById('prior-status'),retry=document.getElementById('prior-retry');
 const regions=['matrix-panel','stock-chart','stock-reference-info','stock-event-info'];
 function busy(value){for(const id of regions){const e=document.getElementById(id);e.style.visibility=value?'hidden':'';e.setAttribute('aria-busy',String(value));}document.getElementById('stock-to-cell').disabled=value||document.getElementById('stock-to-cell').disabled;}
 async function json(path){const r=await fetch(path);if(!r.ok)throw Error('研究数据暂不可用');return r.json();}
 function load(n){if(!cache.has(n))cache.set(n,Promise.all(['all','recent','stability'].map(k=>json('prior/'+n+'/'+k+'.json'))).then(([all,recent,stability])=>{if(all.curves?.length!==162||recent.curves?.length!==162||!Array.isArray(stability.series)||[all,recent,stability].some(d=>d.metadata?.lookback_market_days!==n))throw Error('数据结构不完整');return {datasets:{all,recent},stability};}).catch(e=>{cache.delete(n);throw e;}));return cache.get(n);}
 async function select(){const n=+control.value,ticket=++serial;if(![10,20,30,60,120].includes(n))return;window.PRIOR_RESEARCH.pending=true;if(clearMiniHover)clearMiniHover();compare=[];busy(true);retry.hidden=true;status.textContent='正在加载此前'+n+'个市场交易日的重新分组结果…';window.dispatchEvent(new Event('prior-loading'));
  try{const result=await load(n);if(ticket!==serial)return;window.PRIOR_RESEARCH={days:n,pending:false,...result};D=result.datasets[document.getElementById('history').value];S=result.stability;document.querySelectorAll('[data-prior-days]').forEach(e=>e.textContent=n);render();busy(false);status.textContent='当前此前观察期：'+n+'个市场交易日；矩阵、分期和单股参考按此窗口匹配。';window.dispatchEvent(new Event('prior-changed'));}
  catch(e){if(ticket!==serial)return;status.textContent='此前'+n+'日数据未能加载，暂不显示旧窗口曲线；请重试或选择其他观察期。';retry.hidden=false;}
 }
 control.onchange=select;retry.onclick=select;
})();
