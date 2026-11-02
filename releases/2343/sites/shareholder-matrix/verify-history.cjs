const fs=require('fs'),vm=require('vm'),assert=require('assert'),crypto=require('crypto');
const ctx={window:{}};vm.runInNewContext(fs.readFileSync('dist/data.js','utf8'),ctx);
for(const k of ['all','recent'])assert.equal(JSON.stringify(ctx.window.RESEARCH_DATASETS[k]),JSON.stringify(JSON.parse(fs.readFileSync('fixtures/'+k+'.json'))));
const S=JSON.parse(JSON.stringify(ctx.window.STABILITY_DATA));assert.equal(JSON.stringify(S),JSON.stringify(JSON.parse(fs.readFileSync('fixtures/stability.json'))));
assert.equal(S.series.length,1296);const keys=new Set();
for(const c of S.series){const key=[c.sample_mode,c.period,c.anchor,c.row_id,c.column_id].join('|');assert(!keys.has(key));keys.add(key);assert.deepEqual(c.horizons,[20,60,120,250]);assert.equal(c.small_sample,c.count_events<50||c.count_stocks<10);for(const stat of ['mean','median','equal_stock_mean']){assert.equal(c[stat].length,4);assert(c[stat].every(v=>c.count_events===0?v===null:Number.isFinite(v)));}}
assert.equal(S.yearly_coverage.filter(y=>y.year<2012).reduce((n,y)=>n+y.both_complete250_nonzero_records,0),0);
assert.equal(S.periods.filter(p=>p.sample_mode==='all_events').reduce((n,p)=>n+p.source_events,0),125732);
for(const k of ['all','recent'])for(const a of ['public_nextopen','stat_close']){let d=ctx.window.RESEARCH_DATASETS[k];assert.equal(d.curves.filter(c=>c.anchor===a).length,81);assert.equal(d.curves.filter(c=>c.anchor===a).reduce((n,c)=>n+c.count_events,0),d.metadata[a].main_grid_events);}
const sha=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');assert.equal(sha('fixtures/all.json'),'700b1693fbc6e5010e459b360bd1b24ddcc8d662a5a3e01464674a1465a13abe');assert.equal(sha('fixtures/recent.json'),'14c75734783cefa7ca8f19ba4b715fa363823953e197b5ec9aeda81d29212cdc');
console.log('PASS historical/recent datasets exact audited hashes; 1296 unique stability series, four horizons/nulls/counts; both81 grids; early years0; synchronous data bundling');

assert.equal(sha('fixtures/stability.json'),'d50c3315eb08d5bae4f224a7bc4a34ed327dfe75ae9ea10877eeb907c120fe42');
for(const d of Object.values(ctx.window.RESEARCH_DATASETS)){assert.equal(d.metadata.pool.pool_count,2343);assert.equal(d.metadata.stock_pool_screening_dates.complete_three_month_windows,131);assert.equal(d.metadata.stock_pool_screening_dates.start,'2015-10-01');}
