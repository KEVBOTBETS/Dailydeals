/* Shared pure filtering rules for the page and regression checks. */
(function(root){
  const days=['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday'];
  function localDate(now=new Date()){return new Intl.DateTimeFormat('en-CA',{timeZone:'America/Toronto',year:'numeric',month:'2-digit',day:'2-digit'}).format(now);}
  function today(now=new Date()){return new Intl.DateTimeFormat('en-CA',{timeZone:'America/Toronto',weekday:'long'}).format(now);}
  function active(d,date=localDate()){return (!d.starts||d.starts<=date)&&(!d.ends||d.ends>=date);}
  function scheduled(d,day){return day==='Week'||d.days.includes(day);}
  function filter(deals,s,date=localDate()){
    let result=deals.filter(d=>active(d,date)&&scheduled(d,s.day));
    if(s.type==='saved') result=result.filter(d=>s.saved.has(d.id));
    else if(s.type!=='all') result=result.filter(d=>d.kind===s.type);
    if(s.budget!=='all') result=result.filter(d=>typeof d.price==='number'&&d.price<=Number(s.budget));
    if(s.search.trim()) {const q=s.search.trim().toLowerCase();result=result.filter(d=>[d.brand,d.title,d.description,d.terms].join(' ').toLowerCase().includes(q));}
    result.sort((a,b)=>s.sort==='brand'?a.brand.localeCompare(b.brand):s.sort==='price'?(a.price??Infinity)-(b.price??Infinity):(a.kind==='meal'?0:a.kind==='coupon'?1:2)-(b.kind==='meal'?0:b.kind==='coupon'?1:2)||(a.price??Infinity)-(b.price??Infinity));
    return result;
  }
  const api={days,localDate,today,active,scheduled,filter};
  if(typeof module!=='undefined')module.exports=api;else root.DealLogic=api;
})(typeof window!=='undefined'?window:globalThis);
