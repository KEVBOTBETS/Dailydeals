const boot = document.createElement('script');boot.src='./deal-logic.js';boot.onload=start;boot.onerror=()=>{document.getElementById('cards').textContent='Could not load the deal finder. Please reload.';};document.head.append(boot);
async function start(){
 const L=window.DealLogic,$=id=>document.getElementById(id),esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
 const safe=url=>{try{const u=new URL(url);return u.protocol==='https:'?u.href:'#';}catch{return '#';}};
 let persisted={};try{persisted=JSON.parse(localStorage.getItem('durham-daily')||'{}')||{};}catch{}
 const towns=Array.from($('town').options,o=>o.value);
 const state={day:L.today(),type:'all',budget:'all',search:'',sort:'recommended',town:towns.includes(persisted.town)?persisted.town:'Durham Region',saved:new Set(Array.isArray(persisted.saved)?persisted.saved:[])};
 let data;try{const response=await fetch('./data/deals.json',{cache:'no-store'});if(!response.ok)throw Error(response.status);data=await response.json();if(!Array.isArray(data.deals))throw Error('Invalid feed');}catch{ $('cards').innerHTML='<div class="empty"><h3>The deal board couldn’t load.</h3><p>Please reload in a moment. You can still use the local search links below.</p></div>';$('results-title').textContent='Temporarily unavailable';renderHunt();return;}
 function persist(){try{localStorage.setItem('durham-daily',JSON.stringify({town:state.town,saved:[...state.saved]}));}catch{toast('Browser storage is unavailable. Saves last for this visit.');}}
 let toastTimer;function toast(message){$('toast').textContent=message;$('toast').classList.add('show');clearTimeout(toastTimer);toastTimer=setTimeout(()=>$('toast').classList.remove('show'),2400);}
 function dateLabel(date){if(!date)return 'Not checked';return new Intl.DateTimeFormat('en-CA',{timeZone:'America/Toronto',month:'short',day:'numeric',hour:'numeric',minute:'2-digit'}).format(new Date(date));}
 function near(brand){return 'https://www.google.com/maps/search/?api=1&query='+encodeURIComponent(brand+' '+(state.town==='Durham Region'?'Durham Region Ontario':state.town+' Ontario'));}
 function searchURL(query){return 'https://www.google.com/search?q='+encodeURIComponent(query);}
 function place(){return state.town==='Durham Region'?'Durham Region Ontario':state.town+' Ontario';}
 function renderDays(){ $('days').innerHTML=[...L.days,'Week'].map(day=>{const count=data.deals.filter(d=>d.kind==='meal'&&L.scheduled(d,day)).length;return `<button class="day ${day===L.today()?'today':''}" data-day="${day}" aria-pressed="${state.day===day}"><strong>${day==='Week'?'All week':day.slice(0,3)}</strong><small>${day==='Week'?'Next 7 days':L.nextDate(day).slice(5).replace('-','/')+' · '+count+' offers'}</small></button>`;}).join(''); }
 function card(d){
   const age=d.checkedAt?(Date.now()-new Date(d.checkedAt))/86400000:Infinity;
   const status=d.kind==='lighter'?'Menu idea · price not verified':d.kind==='coupon'?'Coupon destination · offers vary':d.sourceUnavailable?'Source unavailable · recheck offer':age>3?'Needs a fresh check':'Published on official source';
   const price=typeof d.price==='number'?'$'+d.price.toFixed(2):d.kind==='lighter'?'See menu':'Check offers';
   return `<article class="card"><div class="card-visual" style="--wash:${esc(d.color||'#e9eddf')}"><span class="visual-word" aria-hidden="true">${esc(d.brand)}</span><span class="card-tag">${esc(d.kind==='lighter'?'HEALTHIER IDEA':d.kind==='coupon'?'COUPON STOP':d.days.length===7?'EVERYDAY VALUE':d.days.join(' + ').toUpperCase())}</span><span class="food-icon" aria-hidden="true">${esc(d.icon)}</span><button class="save" data-save="${esc(d.id)}" aria-pressed="${state.saved.has(d.id)}" aria-label="${state.saved.has(d.id)?'Unsave':'Save'} ${esc(d.title)}">${state.saved.has(d.id)?'♥':'♡'}</button></div><div class="card-body"><span class="restaurant">${esc(d.brand)}</span><h3>${esc(d.title)}</h3><p class="description">${esc(d.description)}</p><div class="price-row"><span class="price ${typeof d.price==='number'?'':'unknown'}">${price}</span><span class="price-caption">${esc(typeof d.price==='number'?(d.priceLabel||'before tax'):(d.priceLabel==='before tax'?'local price varies':d.priceLabel))}</span></div><div class="meta"><span>${d.days.length===7?'Every day':esc(d.days.join(', '))}</span><span>${esc(d.redemption)}</span>${d.ends?'<span>Until '+esc(d.ends)+'</span>':''}</div><p class="source-state">${esc(status)}<br>${d.checkedAt?'Source checked '+esc(dateLabel(d.checkedAt)):'Local availability unconfirmed'}</p><div class="card-actions"><a href="${esc(safe(d.url))}" target="_blank" rel="noopener noreferrer">${d.kind==='lighter'?'Menu & nutrition':d.kind==='coupon'?'Open coupons':'Check offer'} ↗</a><a href="${esc(near(d.brand))}" target="_blank" rel="noopener noreferrer">Find nearby ⌖</a></div><details class="terms"><summary>Details & conditions</summary><p>${esc(d.terms)}</p><p>Coverage: Canadian chain offer; participating Durham locations must be checked with the restaurant.</p></details></div></article>`;
 }
 function render(){
   renderDays();const visible=L.filter(data.deals,state);
   $('town').value=state.town;$('saved-count').textContent=state.saved.size;
   $('types').querySelectorAll('button').forEach(b=>b.setAttribute('aria-pressed',b.dataset.type===state.type));
   $('location-note').textContent=`Showing Canadian offers to check near ${state.town}, Ontario. “Find nearby” searches this area; individual branch participation is not verified.`;
   $('results-title').textContent=`${visible.length} ${state.type==='lighter'?'healthier picks':'offers & ideas'} · ${state.day==='Week'?'next 7 days':state.day+' '+L.nextDate(state.day).slice(5).replace('-','/')}`;
   $('cards').innerHTML=visible.length?visible.map(card).join(''):'<div class="empty"><h3>No matches on this menu.</h3><p>Try a higher budget, another day or reset the filters. Unpriced coupons and menu ideas are excluded by budget limits.</p></div>';
   $('updated').textContent='Feed updated '+dateLabel(data.generatedAt)+' ET';
   const stale=(Date.now()-new Date(data.generatedAt))/86400000>2;
   $('freshness').hidden=!stale;if(stale)$('freshness').textContent='This feed has not refreshed in over 48 hours. Check original sources for current offers.';
   renderHunt();renderWeek();
 }
 function renderHunt(){
   const q=place()+' fast food coupons deals';$('web-search').href=searchURL(q);
   const links=[['Local deal hunt',q+' '+L.today(),'Search today’s deals in '+state.town],['RedFlagDeals','site:forums.redflagdeals.com fast food Ontario coupons','Community finds; check dates and terms.'],['SmartCanucks','site:smartcanucks.ca restaurant coupons Ontario','Canadian coupons, flyers and offers.'],['Healthier for less',place()+' healthy takeout lunch specials cheap','Find local bowls, wraps and lunch specials.']];
   $('hunt-links').innerHTML=links.map(([name,query,note])=>`<a href="${esc(searchURL(query))}" target="_blank" rel="noopener noreferrer"><strong>${esc(name)} ↗</strong><small>${esc(note)}</small></a>`).join('');
   if(!data)return;
   const leads=data.leads||[];$('lead-count').textContent=' · '+leads.length+' leads';
   $('discovery').innerHTML=leads.length?leads.map(l=>`<div class="lead"><a href="${esc(safe(l.url))}" target="_blank" rel="noopener noreferrer">${esc(l.title)} ↗</a><p>${esc(l.snippet||'Search result — verify the offer, dates and participating locations.')}</p><small>Unverified search lead · ${esc(l.query)} · found ${esc(dateLabel(l.foundAt))}</small></div>`).join(''):'<p>No new search leads were retrieved in the latest run. Use the local search links above.</p>';
   $('source-health').innerHTML='<h4>Latest automated source checks</h4><p>A reachable page does not guarantee an offer or local availability.</p><div class="source-list">'+(data.sources||[]).map(s=>`<span>${esc(s.name)} · ${s.ok?'page reachable':'unavailable / blocked'}</span>`).join('')+'</div>';
 }
 function renderWeek(){
   $('week-grid').innerHTML=L.days.map(day=>{const ds=data.deals.filter(d=>L.scheduled(d,day)&&d.kind==='meal'),price=Math.min(...ds.filter(d=>typeof d.price==='number').map(d=>d.price));return `<button class="week-box ${day===L.today()?'today':''}" data-weekday="${day}"><strong>${day} ${day===L.today()?'<em>TODAY</em>':''}</strong><b>${Number.isFinite(price)?'From $'+price.toFixed(2):'Check offers'}</b><small>${L.nextDate(day).slice(5).replace('-','/')} · ${ds.length} meal / snack offers<br>Everyday offers included</small></button>`;}).join('');
 }
 $('days').addEventListener('click',e=>{const b=e.target.closest('[data-day]');if(b){state.day=b.dataset.day;render();}});
 $('types').addEventListener('click',e=>{const b=e.target.closest('[data-type]');if(b){state.type=b.dataset.type;render();}});
 $('cards').addEventListener('click',e=>{const b=e.target.closest('[data-save]');if(b){const id=b.dataset.save;state.saved.has(id)?state.saved.delete(id):state.saved.add(id);persist();render();toast(state.saved.has(id)?'Saved for your next food run.':'Removed from saved deals.');}});
 $('town').addEventListener('change',()=>{state.town=$('town').value;persist();render();});
 $('search').addEventListener('input',()=>{state.search=$('search').value;render();});
 ['budget','sort'].forEach(id=>$(id).addEventListener('change',()=>{state[id]=$(id).value;render();}));
 $('reset').addEventListener('click',()=>{state.type='all';state.search='';state.budget='all';state.sort='recommended';state.day=L.today();$('search').value='';$('budget').value='all';$('sort').value='recommended';render();});
 $('saved-nav').addEventListener('click',()=>{state.type='saved';state.day='Week';state.budget='all';state.search='';$('search').value='';$('budget').value='all';render();$('deals').scrollIntoView();});
 $('healthy-cta').addEventListener('click',()=>{state.type='lighter';state.day='Week';state.budget='all';state.search='';$('search').value='';$('budget').value='all';render();$('deals').scrollIntoView();});
 $('week-grid').addEventListener('click',e=>{const b=e.target.closest('[data-weekday]');if(b){state.day=b.dataset.weekday;state.type='meal';state.budget='all';state.search='';$('search').value='';$('budget').value='all';render();$('deals').scrollIntoView();}});
 render();
}
