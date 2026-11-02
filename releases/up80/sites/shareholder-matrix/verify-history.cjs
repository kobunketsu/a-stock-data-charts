const fs=require('fs'),vm=require('vm'),assert=require('assert'),crypto=require('crypto');
const ctx={window:{}};vm.runInNewContext(fs.readFileSync('dist/data.js','utf8'),ctx);
for(const k of ['all','recent'])assert.equal(JSON.stringify(ctx.window.RESEARCH_DATASETS[k]),JSON.stringify(JSON.parse(fs.readFileSync('fixtures/'+k+'.json'))));
const S=JSON.parse(JSON.stringify(ctx.window.STABILITY_DATA));assert.equal(JSON.stringify(S),JSON.stringify(JSON.parse(fs.readFileSync('fixtures/stability.json'))));
assert.equal(S.series.length,1296);const keys=new Set();
for(const c of S.series){const key=[c.sample_mode,c.period,c.anchor,c.row_id,c.column_id].join('|');assert(!keys.has(key));keys.add(key);assert.deepEqual(c.horizons,[20,60,120,250]);assert.equal(c.small_sample,c.count_events<50||c.count_stocks<10);for(const stat of ['mean','median','equal_stock_mean']){assert.equal(c[stat].length,4);assert(c[stat].every(v=>c.count_events===0?v===null:Number.isFinite(v)));}}
assert.equal(S.yearly_coverage.filter(y=>y.year<2012).reduce((n,y)=>n+y.both_complete250_nonzero_records,0),0);
assert.equal(S.periods.filter(p=>p.sample_mode==='all_events').reduce((n,p)=>n+p.source_events,0),102238);
for(const k of ['all','recent'])for(const a of ['public_nextopen','stat_close']){let d=ctx.window.RESEARCH_DATASETS[k];assert.equal(d.curves.filter(c=>c.anchor===a).length,81);assert.equal(d.curves.filter(c=>c.anchor===a).reduce((n,c)=>n+c.count_events,0),d.metadata[a].main_grid_events);}
const sha=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');assert.equal(sha('fixtures/all.json'),'e04041e0e5e04d488d5f0634e18c1ba11ab8d2464c0907b05ccd93b618cde46e');assert.equal(sha('fixtures/recent.json'),'f36a3bc867be58e4f3e056263740e1183b7c39061ce342d1ad408dc728f16118');
console.log('PASS historical/recent datasets exact audited hashes; 1296 unique stability series, four horizons/nulls/counts; both81 grids; early years0; synchronous data bundling');

assert.equal(sha('fixtures/stability.json'),'379f04a2b2e0b1c4056f8476034d6003242d9b1411b489373598af97a57427a9');
for(const d of Object.values(ctx.window.RESEARCH_DATASETS)){assert.equal(d.metadata.pool.pool_count,1494);assert.equal(d.metadata.stock_pool_screening_dates.complete_three_month_windows,23);assert.equal(d.metadata.stock_pool_screening_dates.start,'2024-10-01');}
