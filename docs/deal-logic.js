/* Shared pure filtering rules for the page and regression checks. */
(function(root){
  const days=['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday'];
  function localDate(now=new Date()){return new Intl.DateTimeFormat('en-CA',{timeZone:'America/Toronto',year:'numeric',month:'2-digit',day:'2-digit'}).format(now);}
  function today(now=new Date()){return new Intl.DateTimeFormat('en-CA',{timeZone:'America/Toronto',weekday:'long'}).format(now);}
  function active(d,date=localDate()){return (!d.starts||d.starts<=date)&&(!d.ends||d.ends>=date);}
  function nextDate(day,date=localDate()){
    const dateObj=new Date(date+'T12:00:00Z');
    const weekday=(dateObj.getUTCDay()+6)%7;
    dateObj.setUTCDate(dateObj.getUTCDate()+(days.indexOf(day)-weekday+7)%7);
    return dateObj.toISOString().slice(0,10);
  }
  function scheduled(d,day,date=localDate()){
    if(day==='Week')return days.some(name=>scheduled(d,name,date));
    const occurrence=nextDate(day,date);
    return d.days.includes(day)&&active(d,occurrence)&&(!d.dates||d.dates.includes(occurrence));
  }
  function category(d){return d.category||(d.kind==='meal'?'meal':d.kind==='lighter'?'idea':'coupon');}
  function cost(d){return typeof d.minimumSpend==='number'?d.minimumSpend:typeof d.price==='number'?d.price:null;}
  function fresh(d,now=new Date()){return !d.sourceUnavailable&&!!d.checkedAt&&now-new Date(d.checkedAt)<=3*86400000&&now-new Date(d.checkedAt)>=-86400000;}
  function branchVerified(d,branches=[],now=new Date()){
    return d.verification==='branch-menu'&&fresh(d,now)&&d.evidence?.url===d.url&&d.evidence?.matchedText&&d.branchIds?.some(id=>branches.some(b=>b.id===id&&b.addressVerified&&fresh(b,now)));
  }
  function inArea(d,s,branches=[]){
    const ids=d.branchIds||[];
    if(ids.length&&s.town&&s.town!=='Durham Region'&&!ids.some(id=>branches.some(b=>b.id===id&&b.town===s.town)))return false;
    if(s.branch&&s.branch!=='all'){
      const branch=branches.find(b=>b.id===s.branch);
      if(!branch)return false;
      if(ids.length?!ids.includes(branch.id):d.brand!==branch.brand)return false;
    }
    return !s.brand||s.brand==='all'||d.brand===s.brand;
  }
  function filter(deals,s,date=localDate(),branches=[]){
    let result=deals.filter(d=>scheduled(d,s.day,date)&&inArea(d,s,branches));
    if(s.type==='saved') result=result.filter(d=>s.saved.has(d.id));
    else if(s.type==='lighter')result=result.filter(d=>d.healthier||d.kind==='lighter');
    else if(s.type==='snacks')result=result.filter(d=>['snack','side','dessert'].includes(category(d)));
    else if(s.type!=='all') result=result.filter(d=>category(d)===s.type);
    if(s.verifiedOnly)result=result.filter(d=>branchVerified(d,branches));
    if(s.budget!=='all') result=result.filter(d=>cost(d)!==null&&cost(d)<=Number(s.budget));
    if(s.search.trim()) {const q=s.search.trim().toLowerCase();result=result.filter(d=>[d.brand,d.title,d.description,d.terms,...(d.branchIds||[]).map(id=>branches.find(b=>b.id===id)?.address||'')].join(' ').toLowerCase().includes(q));}
    const rank={meal:0,main:1,snack:2,side:2,dessert:3,drink:4,coupon:5,idea:6};
    result.sort((a,b)=>s.sort==='brand'?a.brand.localeCompare(b.brand):s.sort==='price'?(cost(a)??Infinity)-(cost(b)??Infinity):(rank[category(a)]??6)-(rank[category(b)]??6)||(cost(a)??Infinity)-(cost(b)??Infinity));
    return result;
  }
  function highlights(deals,s,branches=[],date=localDate()){
    const eligible=filter(deals,{...s,type:'all',verifiedOnly:true},date,branches).filter(d=>cost(d)!==null);
    const cheapest=ds=>ds.sort((a,b)=>cost(a)-cost(b))[0]||null;
    const meal=cheapest(eligible.filter(d=>category(d)==='meal'));
    const healthy=cheapest(eligible.filter(d=>d.healthier&&['main','meal'].includes(category(d))));
    const pairs=eligible.filter(d=>['meal','main'].includes(category(d))&&[1,2].includes(d.serves)&&!(d.requirements?.limitPerUser===1)&&!d.requirements?.minimumPurchase).map(d=>({deal:d,quantity:d.serves===2?1:2,total:Math.round(cost(d)*(d.serves===2?1:2)*100)/100})).filter(p=>s.budget==='all'||p.total<=Number(s.budget)).sort((a,b)=>a.total-b.total);
    return {meal,healthy,pair:pairs[0]||null};
  }
  const api={days,localDate,today,nextDate,active,scheduled,category,cost,fresh,branchVerified,inArea,filter,highlights};
  if(typeof module!=='undefined')module.exports=api;else root.DealLogic=api;
})(typeof window!=='undefined'?window:globalThis);
