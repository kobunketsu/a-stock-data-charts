const fs=require('fs'),vm=require('vm'),assert=require('assert');
(async()=>{
 const els={};const el=id=>els[id]||(els[id]={value:'all',style:{},hidden:false,disabled:false,setAttribute(){}});el('prior-window').value='60';
 const old={all:{metadata:{window:60}},recent:{metadata:{window:60}}};const waiting={},events=[];let renders=0;
 const c={window:{RESEARCH_DATASETS:old,STABILITY_DATA:{},dispatchEvent:e=>events.push(e.type)},document:{getElementById:el,querySelectorAll:()=>[]},Map,Promise,Error,Event,D:null,S:null,compare:[],clearMiniHover:null,render(){renders++;},fetch:p=>new Promise(resolve=>waiting[p]=resolve)};
 vm.runInNewContext(fs.readFileSync('dist/prior.js','utf8'),c);
 el('prior-window').value='10';const slow=el('prior-window').onchange();assert.equal(c.window.PRIOR_RESEARCH.pending,true);assert.equal(el('matrix-panel').style.visibility,'hidden');
 el('prior-window').value='120';const fast=el('prior-window').onchange();
 const finish=n=>{for(const kind of ['all','recent','stability'])waiting[`prior/${n}/${kind}.json`]({ok:true,json:async()=>kind==='stability'?{series:[],window:n,metadata:{lookback_market_days:n}}:{curves:Array(162).fill({}),metadata:{window:n,lookback_market_days:n}}});};
 finish(120);await fast;assert.equal(c.window.PRIOR_RESEARCH.days,120);assert.equal(c.D.metadata.window,120);finish(10);await slow;assert.equal(c.window.PRIOR_RESEARCH.days,120);assert.equal(renders,1);assert.equal(el('matrix-panel').style.visibility,'');
 el('prior-window').value='60';await el('prior-window').onchange();assert.strictEqual(c.D,old.all);assert.equal(c.window.PRIOR_RESEARCH.days,60);
 console.log('PASS atomic prior-window loading, 10→120 out-of-order protection, cached60 exact original, old panel hidden during request');
})().catch(e=>{console.error(e);process.exit(1)});
