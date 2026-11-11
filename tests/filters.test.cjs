const {test}=require('node:test');const assert=require('node:assert/strict');const L=require('../docs/deal-logic.js');
const deals=[{id:'one',kind:'meal',brand:'B',title:'Cheap meal',description:'',terms:'',days:L.days,price:5},{id:'two',kind:'coupon',brand:'A',title:'Coupons',description:'',terms:'',days:L.days,price:null},{id:'three',kind:'meal',brand:'C',title:'Tuesday',description:'',terms:'',days:['Tuesday'],price:9.99},{id:'old',kind:'meal',brand:'D',title:'Old',description:'',terms:'',days:L.days,price:1,ends:'2026-11-09'}];
const state={day:'Monday',type:'all',budget:'all',search:'',sort:'price',saved:new Set()};
test('budget excludes unpriced coupons and expired offers',()=>assert.deepEqual(L.filter(deals,{...state,budget:'5'},'2026-11-10').map(d=>d.id),['one']));
test('weekday-specific offers appear only on the correct day',()=>{assert.equal(L.filter(deals,state,'2026-11-10').length,2);assert.equal(L.filter(deals,{...state,day:'Tuesday'},'2026-11-10').length,3);});
test('saved filter intersects budget and day',()=>assert.deepEqual(L.filter(deals,{...state,type:'saved',saved:new Set(['two'])},'2026-11-10').map(d=>d.id),['two']));
test('Toronto date remains Tuesday after midnight UTC',()=>{assert.equal(L.today(new Date('2026-11-11T02:00:00Z')),'Tuesday');assert.equal(L.localDate(new Date('2026-11-11T02:00:00Z')),'2026-11-10');});
test('search is case insensitive',()=>assert.deepEqual(L.filter(deals,{...state,search:'CHEAP'},'2026-11-10').map(d=>d.id),['one']));
