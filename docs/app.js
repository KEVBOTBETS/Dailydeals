const boot = document.createElement('script');
boot.src='./deal-logic.js?v=20261110-v4';boot.onload=start;
boot.onerror=()=>{document.getElementById('cards').textContent='Could not load the deal finder. Please reload.';};document.head.append(boot);
async function start(){
 const L=window.DealLogic,$=id=>document.getElementById(id);
 const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
 const safe=url=>{try{const u=new URL(url);return u.protocol==='https:'?u.href:'#';}catch{return '#';}};
 const money=n=>'$'+Number(n).toFixed(2);
 const categoryLabels={meal:'Full meal / combo',main:'Main / wrap',snack:'Snack',side:'Side',dessert:'Dessert',drink:'Drink',coupon:'Coupon destination',idea:'Menu idea'};
 let persisted={};try{persisted=JSON.parse(localStorage.getItem('durham-daily')||'{}')||{};}catch{}
 const towns=Array.from($('town').options,o=>o.value);
 const state={day:L.today(),type:'meal',budget:'all',search:'',sort:'recommended',town:towns.includes(persisted.town)?persisted.town:'Durham Region',branch:'all',brand:'all',verifiedOnly:false,hideShawarma:persisted.hideShawarma!==false,saved:new Set(Array.isArray(persisted.saved)?persisted.saved:[])};
 let data;try{
   const response=await fetch('./data/deals.json',{cache:'no-store'});if(!response.ok)throw Error(response.status);
   data=await response.json();if(!Array.isArray(data.deals))throw Error('Invalid feed');data.branches||=[];
 }catch{
   $('cards').innerHTML='<div class="empty"><h3>The deal board couldn’t load.</h3><p>Please reload in a moment. Local search links are available below.</p></div>';
   $('results-title').textContent='Temporarily unavailable';renderHunt();return;
 }
 function persist(){try{localStorage.setItem('durham-daily',JSON.stringify({town:state.town,hideShawarma:state.hideShawarma,saved:[...state.saved]}));}catch{toast('Browser storage is unavailable. Saves last for this visit.');}}
 let toastTimer;function toast(message){$('toast').textContent=message;$('toast').classList.add('show');clearTimeout(toastTimer);toastTimer=setTimeout(()=>$('toast').classList.remove('show'),2400);}
 function dateLabel(date){if(!date)return 'Not checked';return new Intl.DateTimeFormat('en-CA',{timeZone:'America/Toronto',month:'short',day:'numeric',hour:'numeric',minute:'2-digit'}).format(new Date(date));}
 function near(brand,address){return 'https://www.google.com/maps/search/?api=1&query='+encodeURIComponent(address||brand+' '+place());}
 function searchURL(query){return 'https://www.google.com/search?q='+encodeURIComponent(query);}
 function place(){return state.town==='Durham Region'?'Durham Region Ontario':state.town+' Ontario';}
 function scoped(day=state.day,type='all'){return L.filter(data.deals,{...state,day,type},L.localDate(),data.branches);}
 function associated(d){return (d.branchIds||[]).map(id=>data.branches.find(b=>b.id===id)).filter(Boolean);}
 function renderControls(){
   const brands=[...new Set(data.deals.filter(d=>!state.hideShawarma||!L.isShawarma(d)).map(d=>d.brand))].sort();if(!brands.includes(state.brand))state.brand='all';
   $('restaurant').innerHTML='<option value="all">All restaurants</option>'+brands.map(b=>`<option value="${esc(b)}">${esc(b)}</option>`).join('');$('restaurant').value=state.brand;
   const branches=data.branches.filter(b=>(!state.hideShawarma||!L.isShawarma(b))&&(state.town==='Durham Region'||b.town===state.town)&&(state.brand==='all'||b.brand===state.brand));
   if(!branches.some(b=>b.id===state.branch))state.branch='all';
   $('branch').innerHTML='<option value="all">Any branch</option>'+branches.map(b=>`<option value="${esc(b.id)}">${esc(b.brand+' · '+b.address)}</option>`).join('');$('branch').value=state.branch;
   $('town').value=state.town;$('verified-only').checked=state.verifiedOnly;$('hide-shawarma').checked=state.hideShawarma;
 }
 function renderDays(){
   $('days').innerHTML=[...L.days,'Week'].map(day=>{
     const count=scoped(day,'meal').length;
     return `<button class="day ${day===L.today()?'today':''}" data-day="${day}" aria-pressed="${state.day===day}"><strong>${day==='Week'?'All week':day.slice(0,3)}</strong><small>${day==='Week'?'Next 7 days':L.nextDate(day).slice(5).replace('-','/')+' · '+count+' meals'}</small></button>`;
   }).join('');
 }
 function requirements(d){
   const r=d.requirements||{},chips=[];
   if(r.app===true)chips.push('App required');
   if(r.registration===true)chips.push('Registration required');
   if(r.membership)chips.push(r.membership+' membership');
   if(r.code)chips.push('Code: '+r.code);
   if(r.minimumPurchase>0)chips.push('Buy '+money(r.minimumPurchase)+' first');
   if(r.limitPerUser)chips.push('Limit '+r.limitPerUser+' / user');
   if(d.priceType==='menu'||d.verification==='branch-menu')chips.push('Menu price · no coupon');
   if(!chips.length&&d.kind==='coupon')chips.push('Account / offer terms vary');
   return chips.map(t=>`<span>${esc(t)}</span>`).join('');
 }
 function card(d){
   const verified=!!L.branchVerified(d,data.branches),branches=associated(d),cat=L.category(d),cost=L.cost(d);
   const status=verified?'✓ Branch menu price checked':d.kind==='lighter'?'Menu idea · no verified price':d.kind==='coupon'?'Offer destination · no price verified':!L.fresh(d)?'Needs recheck · source unavailable or stale':'Chain price · branch unconfirmed';
   const label=cat==='coupon'?'COUPON STOP':d.priceType==='menu'?'LOCAL MENU PRICE':d.days.length===7?'EVERYDAY VALUE':d.days.join(' + ').toUpperCase();
   const price=typeof d.price==='number'?(d.price===0?'FREE*':money(d.price)):cat==='idea'?'See menu':'Check offers';
   const branchInfo=branches.length?branches.map(b=>`<a href="${esc(safe(b.url))}" target="_blank" rel="noopener noreferrer">⌖ ${esc(b.address)} ↗</a>`).join(''):state.branch!=='all'?`Selected branch: ${esc(data.branches.find(b=>b.id===state.branch)?.address)}. Price still needs local confirmation.`:'Canadian offer; choose your restaurant to confirm its price.';
   return `<article class="card" id="deal-${esc(d.id)}"><div class="card-visual" style="--wash:${esc(d.color||'#e9eddf')}"><span class="visual-word" aria-hidden="true">${esc(d.brand)}</span><span class="card-tag">${esc(label)}</span><span class="food-icon" aria-hidden="true">${esc(d.icon)}</span><button class="save" data-save="${esc(d.id)}" aria-pressed="${state.saved.has(d.id)}" aria-label="${state.saved.has(d.id)?'Unsave':'Save'} ${esc(d.title)}">${state.saved.has(d.id)?'♥':'♡'}</button></div><div class="card-body"><span class="restaurant">${esc(d.brand)}</span><div class="category-line">${esc(categoryLabels[cat]||cat)}${d.serves>1?' · serves '+d.serves:''}${d.healthier?' · 🌿 plant-forward':''}</div><h3>${esc(d.title)}</h3><p class="description">${esc(d.description)}</p>${d.healthReason?'<p class="health-reason">🌿 '+esc(d.healthReason)+'</p>':''}<div class="price-row"><span class="price ${typeof d.price==='number'?'':'unknown'}">${price}</span><span class="price-caption">${typeof d.price==='number'?'advertised price · CAD':'local price varies'}</span></div>${cost!==null?`<div class="spend"><strong>${money(cost)} minimum total</strong><small>Before tax${d.serves>1?' · buy the whole '+d.serves+'-person bundle':''}${d.requirements?.minimumPurchase>0?' · required purchase included':''}</small>${d.serves>1?'<small>'+money(cost/d.serves)+' each when shared; '+money(cost)+' to pay.</small>':''}</div>`:''}<div class="requirements">${requirements(d)}</div><div class="meta"><span>${d.days.length===7?'Every day':esc(d.days.join(', '))}</span><span>${esc(d.redemption)}</span>${d.ends?'<span>Until '+esc(d.ends)+'</span>':''}</div><p class="source-state ${verified?'verified':''}">${esc(status)}<br>${d.checkedAt?'Source checked '+esc(dateLabel(d.checkedAt))+' ET':'Open the source for current details'}</p><div class="branch-info">${branchInfo}</div><div class="card-actions"><a href="${esc(safe(d.url))}" target="_blank" rel="noopener noreferrer">${d.kind==='lighter'?'Menu & nutrition':d.kind==='coupon'?'Open offers':'View price source'} ↗</a><a href="${esc(near(d.brand,branches[0]?.address))}" target="_blank" rel="noopener noreferrer">${branches.length?'Directions':'Find nearby'} ⌖</a></div><details class="terms"><summary>All requirements & price evidence</summary><p>${esc(d.requirements?.note||'Check current merchant terms.')}</p><p>${esc(d.terms)}</p>${d.evidence?'<p>Menu evidence: “'+esc(d.evidence.matchedText)+'”</p>':''}${d.posterUrl?'<p><a href="'+esc(safe(d.posterUrl))+'" target="_blank" rel="noopener noreferrer">View official daily-special poster ↗</a></p>':''}${d.dates?'<p>Eligible dates: '+esc(d.dates.join(', '))+'</p>':''}<p>Prices are published website quotes, not a completed checkout. Tax, extras, delivery and final availability must be confirmed.</p></details></div></article>`;
 }
 function renderPicks(){
   const p=L.highlights(data.deals,state,data.branches);const thai=scoped().filter(d=>d.brand==='Thai Express'&&d.isDailySpecial&&L.fresh(d)).sort((a,b)=>L.cost(a)-L.cost(b))[0];const first=p.meal||thai;const items=[
     [p.meal?'Cheapest full meal':'Thai Express daily special',first,first?L.cost(first):null,p.meal?(p.meal.serves>1?'Whole '+p.meal.serves+'-person combo':'Full meal / combo'):'Official Discovery Menu · confirm branch'],
     ['Best healthier value',p.healthy,p.healthy?L.cost(p.healthy):null,'Lowest-priced plant-forward main'],
     ['Best meal for two',p.pair?.deal,p.pair?.total,p.pair?.quantity===2?'Buy 2 × the listed main':'Whole two-person bundle']
   ];
   $('best-picks').innerHTML=items.map(([title,d,total,note],i)=>`<article class="best-pick"><span class="pick-index">0${i+1} / ${esc(title.toUpperCase())}</span>${d?`<h3>${esc(d.title)}</h3><strong>${money(total)} <small>total before tax</small></strong><p>${esc(note)} · ${esc(associated(d)[0]?.address||d.brand)}</p><button data-pick="${esc(d.id)}">${d.verification==='branch-menu'?'See checked menu':'See advertised special'} ↗</button>`:'<h3>No checked match yet</h3><p>No fresh branch-menu price fits this category and your filters. Try another town or a larger budget.</p>'}</article>`).join('');
 }
 function renderBranches(){
   const branches=data.branches.filter(b=>(!state.hideShawarma||!L.isShawarma(b))&&(state.town==='Durham Region'||b.town===state.town)&&(state.brand==='all'||b.brand===state.brand));
   const priced=new Set(data.deals.filter(d=>L.branchVerified(d,data.branches)).flatMap(d=>d.branchIds));
   $('branch-summary').textContent=branches.filter(b=>priced.has(b.id)).length+' branches with checked menu prices';
   $('branch-grid').innerHTML=branches.length?branches.map(b=>`<article class="branch-tile"><span class="restaurant">${esc(b.brand)}</span><h3>${esc(b.address)}</h3><p>${priced.has(b.id)?'✓ Branch menu prices checked':b.addressVerified?'Address checked · deal prices unconfirmed':'Address source needs a recheck'}</p><small>${b.checkedAt?'Checked '+esc(dateLabel(b.checkedAt))+' ET':'No successful source check this run'}</small><div><a href="${esc(safe(b.url))}" target="_blank" rel="noopener noreferrer">Official branch / menu ↗</a>${b.phone?'<a href="tel:'+esc(b.phone)+'">Call branch</a>':''}<button data-branch="${esc(b.id)}">Show this branch</button></div></article>`).join(''):'<div class="empty"><h3>No branch records here yet.</h3><p>Use the nearby links to find a restaurant. No location-specific price is being claimed for this town.</p></div>';
 }
 function render(){
   renderControls();renderDays();const visible=scoped(state.day,state.type);
   $('saved-count').textContent=state.saved.size;$('types').querySelectorAll('button').forEach(b=>b.setAttribute('aria-pressed',b.dataset.type===state.type));
   $('location-note').textContent=`${state.town}, Ontario · Green checks identify a price on a specific branch’s menu. Chain offers still need local confirmation. Budget filters use the whole minimum spend before tax.`;
   $('results-title').textContent=`${visible.length} ${state.type==='lighter'?'healthier options':'matches'} · ${state.day==='Week'?'next 7 days':state.day+' '+L.nextDate(state.day).slice(5).replace('-','/')}`;
   $('cards').innerHTML=visible.length?visible.map(card).join(''):'<div class="empty"><h3>No matches for these filters.</h3><p>Try a larger budget, Mains & wraps, Everything, or another town. Branch prices checked only excludes unconfirmed chain offers. Unknown prices never pass a budget cap.</p></div>';
   $('updated').textContent='Feed updated '+dateLabel(data.generatedAt)+' ET';
   const stale=(Date.now()-new Date(data.generatedAt))/86400000>2;
   $('freshness').hidden=!stale;if(stale)$('freshness').textContent='This feed has not refreshed in over 48 hours. Check merchant sources for current prices.';
   renderPicks();renderBranches();renderHunt();renderWeek();
 }
 function renderHunt(){
   const q=place()+' fast food coupons deals';$('web-search').href=searchURL(q);
   const links=[['Local deal hunt',q+' '+L.today(),'Search current deals in '+state.town],['RedFlagDeals','site:forums.redflagdeals.com '+place()+' food coupons','Community leads; merchant confirmation required.'],['SmartCanucks','site:smartcanucks.ca restaurant coupons Ontario','Canadian coupons, flyers and offers.'],['Healthier for less',place()+' vegetarian wraps bowls lunch specials prices','Find local wraps, bowls and vegetable options.']];
   $('hunt-links').innerHTML=links.map(([name,query,note])=>`<a href="${esc(searchURL(query))}" target="_blank" rel="noopener noreferrer"><strong>${esc(name)} ↗</strong><small>${esc(note)}</small></a>`).join('');if(!data)return;
   const leads=(data.leads||[]).filter(l=>!state.hideShawarma||!L.isShawarma({brand:l.title,title:l.query}));$('lead-count').textContent=' · '+leads.length+' leads';
   $('discovery').innerHTML=leads.length?leads.map(l=>`<div class="lead"><span class="lead-status">${l.status==='merchant-match'?'Product & price matched to merchant':l.status==='official-link'?'Official merchant link · offer needs inspection':'Unverified coupon lead'}</span><a href="${esc(safe(l.url))}" target="_blank" rel="noopener noreferrer">${esc(l.title)} ↗</a><p>${esc(l.snippet)}</p>${l.matchedDealId?'<a href="'+esc(safe(l.merchantUrl))+'" target="_blank" rel="noopener noreferrer">View matching merchant source ↗</a>':''}<small>${esc(l.query)} · found ${esc(dateLabel(l.foundAt))}</small></div>`).join(''):'<p>No new leads this run. Use local search above.</p>';
   $('source-health').innerHTML='<h4>Automated search coverage</h4><p>Official menus, offer pages, branch pages and Canadian coupon feeds are checked twice daily. New coupon leads require a matching merchant product and price before they get a merchant-match label. Branch verification requires separate address-specific menu evidence.</p><div class="source-list">'+(data.sources||[]).map(s=>`<span>${esc(s.name)} · ${s.ok?'page read':'unavailable / unreadable'}</span>`).join('')+'</div>';
 }
 function renderWeek(){
   $('week-grid').innerHTML=L.days.map(day=>{const ds=scoped(day,'meal'),price=Math.min(...ds.map(d=>L.cost(d)).filter(n=>n!==null));return `<button class="week-box ${day===L.today()?'today':''}" data-weekday="${day}"><strong>${day} ${day===L.today()?'<em>TODAY</em>':''}</strong><b>${Number.isFinite(price)?'From '+money(price):'No priced meal'}</b><small>${L.nextDate(day).slice(5).replace('-','/')} · ${ds.length} full meals / combos<br>Whole spend before tax</small></button>`;}).join('');
 }
 function clearSearch(){state.search='';$('search').value='';}
 function reset(){Object.assign(state,{day:L.today(),type:'meal',budget:'all',search:'',sort:'recommended',branch:'all',brand:'all',verifiedOnly:false});$('search').value='';$('budget').value='all';$('sort').value='recommended';render();}
 $('days').addEventListener('click',e=>{const b=e.target.closest('[data-day]');if(b){state.day=b.dataset.day;render();}});
 $('types').addEventListener('click',e=>{const b=e.target.closest('[data-type]');if(b){state.type=b.dataset.type;render();}});
 $('cards').addEventListener('click',e=>{const b=e.target.closest('[data-save]');if(b){const id=b.dataset.save;state.saved.has(id)?state.saved.delete(id):state.saved.add(id);persist();render();toast(state.saved.has(id)?'Saved for your next food run.':'Removed from saved deals.');}});
 $('town').addEventListener('change',()=>{state.town=$('town').value;state.branch='all';persist();render();});
 $('restaurant').addEventListener('change',()=>{state.brand=$('restaurant').value;state.branch='all';state.type='all';render();});
 $('branch').addEventListener('change',()=>{state.branch=$('branch').value;render();});
 $('verified-only').addEventListener('change',()=>{state.verifiedOnly=$('verified-only').checked;render();});
 $('hide-shawarma').addEventListener('change',()=>{state.hideShawarma=$('hide-shawarma').checked;persist();render();});
 $('search').addEventListener('input',()=>{state.search=$('search').value;render();});
 ['budget','sort'].forEach(id=>$(id).addEventListener('change',()=>{state[id]=$(id).value;render();}));
 $('reset').addEventListener('click',reset);
 $('saved-nav').addEventListener('click',()=>{reset();state.type='saved';state.day='Week';render();$('deals').scrollIntoView();});
 $('healthy-cta').addEventListener('click',()=>{reset();state.type='lighter';state.day='Week';render();$('deals').scrollIntoView();});
 $('week-grid').addEventListener('click',e=>{const b=e.target.closest('[data-weekday]');if(b){state.day=b.dataset.weekday;state.type='meal';clearSearch();render();$('deals').scrollIntoView();}});
 $('best-picks').addEventListener('click',e=>{const b=e.target.closest('[data-pick]');if(b){state.type='all';clearSearch();render();$('deal-'+b.dataset.pick)?.scrollIntoView({block:'center'});}});
 $('branch-grid').addEventListener('click',e=>{const b=e.target.closest('[data-branch]');if(b){state.branch=b.dataset.branch;state.type='all';clearSearch();render();$('deals').scrollIntoView();}});
 render();
}
