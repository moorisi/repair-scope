const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const root=path.resolve(__dirname,'..'),repo='moorisi/repair-scope';
const cases={correlation:{statuses:['CERTAIN','POSSIBLE','IMPOSSIBLE']},cardinality:{statuses:['IMPOSSIBLE','CERTAIN','CERTAIN']},unresolved:{statuses:[]}};
const rosters={assets:['asset-amber','asset-bronze','asset-copper'],holders:['holder-red','holder-blue'],sites:['site-north','site-south']};
const canonical=x=>Array.isArray(x)?x.map(canonical):x&&typeof x==='object'?Object.fromEntries(Object.keys(x).sort().map(k=>[k,canonical(x[k])])):x;
const equal=(a,b)=>JSON.stringify(canonical(a))===JSON.stringify(canonical(b)),clone=x=>JSON.parse(JSON.stringify(x));
function assert(ok,message){if(!ok)throw Error(message);}
function source(id){return JSON.parse(fs.readFileSync(path.join(root,'fixtures',id+'.json')));}
function labels(id){return JSON.parse(fs.readFileSync(path.join(root,'tests',id+'-expected.json')));}
function descriptor(id,revision){return [{url:`https://raw.githubusercontent.com/${repo}/${revision}/fixtures/${id}.json`,sha256:crypto.createHash('sha256').update(fs.readFileSync(path.join(root,'fixtures',id+'.json'))).digest('hex')}];}
function args(id,revision){const d=descriptor(id,revision)[0];return [repo,id+'-snapshot',rosters.assets,rosters.holders,rosters.sites,source(id).records.map(x=>x.id),d.url,d.sha256];}
function configuration(a){return {repository:a[0],snapshot:a[1],assets:a[2],holders:a[3],sites:a[4],records:a[5],url:a[6],sha256:a[7]};}
function initial(id,revision){return {configuration:configuration(args(id,revision)),assessment:null,database:null,answers:[]};}
function product(domains){return domains.reduce((xs,domain)=>xs.flatMap(xs=>domain.map(x=>[...xs,x])),[[]]);}
function oracle(rows){
 const facts=[...new Set(rows.filter(r=>r.status==='ASSERTED').map(r=>JSON.stringify([r.asset,r.holder,r.site])))].map(x=>JSON.parse(x)).sort((a,b)=>JSON.stringify(a).localeCompare(JSON.stringify(b)));
 const origins=facts.map(f=>rows.filter(r=>r.status==='ASSERTED'&&equal([r.asset,r.holder,r.site],f)).map(r=>r.id));
 const unknown=rows.filter(r=>r.status==='UNKNOWN').map(r=>r.id);
 if(unknown.length)return {status:'REVIEW',facts,origins,unknown,maximum_size:-1,repairs:[],certain_facts:[]};
 // Independent per-asset choices, not contract bit-mask/conflict-edge enumeration.
 const assets=[...new Set(facts.map(f=>f[0]))].sort(),candidates=[];
 for(const chosen of product(assets.map(a=>[-1,...facts.flatMap((f,i)=>f[0]===a?[i]:[])]))){
  const indices=chosen.filter(x=>x>=0).sort((a,b)=>a-b),locations=new Map();let valid=true;
  for(const i of indices){const [,h,s]=facts[i];if(locations.has(h)&&locations.get(h)!==s)valid=false;locations.set(h,s);}
  if(valid)candidates.push(indices);
 }
 const maximum_size=Math.max(...candidates.map(x=>x.length)),repairs=candidates.filter(x=>x.length===maximum_size).sort((a,b)=>{for(let i=0;i<a.length;i++)if(a[i]!==b[i])return a[i]-b[i];return 0;});
 return {status:'READY',facts,origins,unknown:[],maximum_size,repairs,certain_facts:facts.flatMap((_,i)=>repairs.every(r=>r.includes(i))?[i]:[])};
}
function queryOracle(database,atoms){
 const true_repairs=[];let witness=null,counterexample=null;
 for(const [i,repair] of database.repairs.entries()){
  let found=null;
  for(const indices of product(atoms.map(()=>repair))){
   const bindings={};let valid=true;
   for(let j=0;j<atoms.length;j++)for(let k=0;k<3;k++){const term=atoms[j][k],value=database.facts[indices[j]][k];if(term.startsWith('?')){if(Object.hasOwn(bindings,term)&&bindings[term]!==value)valid=false;bindings[term]=value;}else if(term!==value)valid=false;}
   if(valid){found={facts:indices,bindings};break;}
  }
  if(found){true_repairs.push(i);if(witness===null)witness={repair:i,assignment:found};}else if(counterexample===null)counterexample=i;
 }
 return {atoms,status:true_repairs.length===database.repairs.length?'CERTAIN':true_repairs.length?'POSSIBLE':'IMPOSSIBLE',true_repairs,repair_count:database.repairs.length,witness,counterexample};
}
function queries(id){return id==='cardinality'?[
 [['asset-amber','holder-red','?s']],
 [['asset-bronze','holder-red','site-north'],['asset-copper','holder-red','site-north']],
 [['?a','?h','site-south']]
 ]:[
 [['asset-amber','?h','site-north']],
 [['asset-amber','?h','site-north'],['asset-bronze','?h','site-north']],
 [['?a','?h','site-south']]
 ];}
function check(s,id,revision){
 assert(Object.keys(s).sort().join(',')==='answers,assessment,configuration,database'&&equal(s.configuration,configuration(args(id,revision)))&&Array.isArray(s.answers),'Exact source-bound whole state');
 if(s.assessment===null){assert(s.database===null&&s.answers.length===0,'No repair or answer before consensus');return;}
 const a=s.assessment,report=source(id),expected=labels(id);
 assert(Object.keys(a).sort().join(',')==='observations,source'&&equal(a.source,report)&&Object.keys(a.observations).join(',')==='rows'&&a.observations.rows.length===expected.length,'Full source and complete semantic assessment');
 for(let i=0;i<expected.length;i++){const row=a.observations.rows[i];assert(Object.keys(row).sort().join(',')==='asset,holder,id,quote,site,status'&&Object.keys(expected[i]).every(k=>row[k]===expected[i][k]),'Every exact assertion, omission and uncertainty');assert(typeof row.quote==='string'&&row.quote.length>=12&&row.quote.length<=400&&report.records[i].text.includes(row.quote),'Material source-linked quote');}
 assert(equal(s.database,oracle(expected)),'Independent complete maximum-cardinality repair oracle');
 for(let i=0;i<s.answers.length;i++)assert(equal(s.answers[i],queryOracle(s.database,queries(id)[i]))&&s.answers[i].status===cases[id].statuses[i],'Correlated query witness/counterexample oracle');
}
function plan(id){return [
 {label:id+'-reject-before-compile',caller:1,method:'query',args:[queries(id)[0]],error:'[EXPECTED] Snapshot not compiled'},
 {label:id+'-compile',caller:2,method:'compile',args:[]},
 ...queries(id).map((atoms,i)=>({label:id+'-query-'+(i+1),caller:(i+1)%4,method:'query',args:[atoms],...(id==='unresolved'?{error:'[EXPECTED] Snapshot requires review'}:{})})),
 {label:id+'-reject-repeat-compile',caller:0,method:'compile',args:[],error:'[EXPECTED] Snapshot already compiled'},
 {label:id+'-reject-invalid-query',caller:3,method:'query',args:[[['?x','?x','site-north']]],error:id==='unresolved'?'[EXPECTED] Snapshot requires review':'[EXPECTED] Invalid bounded conjunctive query'}
 ];}
function replay(before,item,after,id,revision){
 check(before,id,revision);check(after,id,revision);
 if(item.error){assert(equal(before,after),'Expected rejection changed state');return;}
 const e=clone(before);
 if(item.method==='compile'){assert(e.assessment===null,'Compile fixed snapshot once');e.assessment=clone(after.assessment);e.database=oracle(labels(id));}
 else if(item.method==='query')e.answers.push(queryOracle(e.database,item.args[0]));
 else throw Error('Unknown planned method');
 assert(equal(e,after),'Independent whole-state replay: '+item.label);
}
module.exports={cases,args,descriptor,initial,plan,replay,oracle,queryOracle,check,queries};
