(()=>{'use strict';
const api=window.CourseAPI;if(!api)return;
const lesson=document.querySelector('[data-lesson-id]'),id=lesson?.dataset.lessonId;
const answers=api.state.answers;
const priorReviewed=Boolean(id&&api.state.completed['unit-v3-'+id]===true);
const sheet=document.querySelector('.cheat-sheet');let sheetTrigger;
document.querySelectorAll('[data-open-sheet]').forEach(button=>button.addEventListener('click',()=>{sheetTrigger=button;if(!sheet.open)sheet.showModal();}));
document.querySelectorAll('[data-close-sheet]').forEach(button=>button.addEventListener('click',()=>sheet?.close()));
sheet?.addEventListener('click',e=>{if(e.target===sheet){const r=sheet.getBoundingClientRect();if(e.clientX<r.left||e.clientX>r.right||e.clientY<r.top||e.clientY>r.bottom)sheet.close();}});
sheet?.addEventListener('close',()=>sheetTrigger?.focus());
const returnKey='ase-reading-return';
document.querySelectorAll('[data-reading-return]').forEach(a=>a.addEventListener('click',()=>{try{sessionStorage.setItem(returnKey,JSON.stringify({lesson:location.pathname,reading:new URL(a.href,location.href).pathname,y:window.scrollY}));}catch{}}));
let savedReturn;try{savedReturn=JSON.parse(sessionStorage.getItem(returnKey)||'null');}catch{}
if(savedReturn&&/^\/(?:lessons\/\d+-\d+|weeks\/\d+|projects\/[12]|resources|progress|curriculum|readings\/[a-z0-9-]+|papers\/[a-z0-9-]+)\/$/.test(savedReturn.lesson)&&savedReturn.reading===location.pathname){document.querySelectorAll('[data-return-lesson]').forEach(a=>{a.href=savedReturn.lesson+'?return=reading';a.textContent=savedReturn.lesson.startsWith('/lessons/')?'Back to lesson':savedReturn.lesson.startsWith('/weeks/')?'Back to week':savedReturn.lesson.startsWith('/projects/')?'Back to project':'Back to reading list';});}
if(savedReturn?.lesson===location.pathname&&new URLSearchParams(location.search).get('return')==='reading'){
 requestAnimationFrame(()=>{window.scrollTo(0,Number.isFinite(savedReturn.y)?Math.max(0,savedReturn.y):0);});
 history.replaceState(null,'',location.pathname+location.hash);
}
function getRecord(){try{const r=JSON.parse(answers['v4-lesson-'+id]||'{}');return r&&typeof r==='object'&&!Array.isArray(r)?r:{};}catch{return {};}}
function putRecord(record){if(priorReviewed)record.legacyComplete=true;answers['v4-lesson-'+id]=JSON.stringify(record);api.save();}
function refreshLesson(){if(!id)return;const r=getRecord(),legacy=priorReviewed||r.legacyComplete===true;
 lesson.querySelectorAll('[data-evidence]').forEach(e=>{e.checked=Boolean(r[e.dataset.evidence]);});
 const complete=Boolean(r.practice&&r.passed);
 if(r.started)api.setComplete('unit-v3-'+id,complete||legacy);
 const status=lesson.querySelector('.completion-status');
 status.textContent=complete?'Lesson complete. Continue to the next activity.':legacy?'Lesson complete. Your earlier progress is preserved.':'Review your exercise answer and pass the quiz to complete this lesson.';

 window.CourseJourney?.updateJourney();
}
if(id){lesson.querySelectorAll('[data-evidence]').forEach(e=>e.addEventListener('change',()=>{const r=getRecord();r.started=true;r[e.dataset.evidence]=e.checked;putRecord(r);refreshLesson();}));refreshLesson();}

const quiz=document.querySelector('[data-formative]');
if(quiz){fetch('/formative.json').then(r=>{if(!r.ok)throw Error('Quiz unavailable');return r.json();}).then(data=>{
 const q=data.find(x=>x.id===quiz.dataset.formative);if(!q)throw Error('Quiz unavailable');const form=quiz.querySelector('form'),feedback=quiz.querySelector('.formative-feedback'),attempt=quiz.querySelector('[data-quiz-attempt]');
 function showAttempt(r){attempt.textContent=r.attempts?.length?`${r.attempts.length} recorded attempt${r.attempts.length===1?'':'s'}. Latest score: ${r.attempts.at(-1).passed?'1 / 1':'0 / 1'}.`:'';}
 const initial=getRecord();showAttempt(initial);if(initial.selection!==undefined){const input=form.querySelector(`input[value="${Number(initial.selection)}"]`);if(input)input.checked=true;}if(initial.passed)feedback.textContent='You passed this check. '+q.explanation;
 form.addEventListener('submit',e=>{e.preventDefault();const selected=form.querySelector('input:checked');if(!selected){feedback.textContent='Choose an answer first.';return;}const index=Number(selected.value),passed=q.options[index]?.correct===true,r=getRecord();r.started=true;r.selection=index;r.passed=passed;r.attempts=Array.isArray(r.attempts)?r.attempts:[];r.attempts.push({selection:index,passed,at:new Date().toISOString()});putRecord(r);feedback.replaceChildren();const title=document.createElement('h3');title.textContent=passed?'Correct':'Review the explanation';const p=document.createElement('p');p.textContent=q.explanation;feedback.append(title,p);if(!passed){const a=document.createElement('a');a.href=q.review;a.textContent='Review this topic';feedback.append(a);}showAttempt(r);refreshLesson();});
 quiz.querySelector('[data-retry-formative]').addEventListener('click',()=>{form.reset();feedback.textContent='Choose an answer after reviewing the explanation. Earlier attempts remain in your learning record.';const r=getRecord();delete r.selection;putRecord(r);form.querySelector('input')?.focus();});
}).catch(()=>{quiz.querySelector('.formative-feedback').textContent='The quiz could not load. Reload this page to retry. Your saved work remains available.';});}
// Retain earlier completion keys. Report them without implying automatic certification.
document.querySelectorAll('[data-unit-state]').forEach(e=>{if(api.state.completed['unit-v3-'+e.dataset.unitState]===true)e.textContent='Reviewed';});
})();

// An exact probability experiment for lesson 1.2. No model calls or simulated accuracy.
(()=>{const box=document.querySelector('[data-sampling]');if(!box)return;
const temperature=box.querySelector('[data-temperature]'),nucleus=box.querySelector('[data-nucleus]');
function update(){const t=Number(temperature.value),p=Number(nucleus.value),weights=[2,1,0].map(z=>Math.exp((z-2)/t)),sum=weights.reduce((a,b)=>a+b,0),probs=weights.map(x=>x/sum);let mass=0;const keep=probs.map(prob=>{const selected=mass<p;if(selected)mass+=prob;return selected;});
box.querySelector('[data-temperature-value]').textContent=t.toFixed(2);box.querySelector('[data-nucleus-value]').textContent=p.toFixed(2);
const result=box.querySelector('[data-sampling-result]');result.replaceChildren();probs.forEach((prob,i)=>{const row=document.createElement('div');row.className='probability-row';const title=document.createElement('strong');title.textContent='Token '+String.fromCharCode(65+i);const bar=document.createElement('meter');bar.min=0;bar.max=1;bar.value=keep[i]?prob/mass:0;bar.setAttribute('aria-label',title.textContent+' final sampling probability');const value=document.createElement('span');value.textContent=(prob*100).toFixed(1)+'% before filtering; '+(keep[i]?(prob/mass*100).toFixed(1)+'% after filtering':'excluded');row.append(title,bar,value);result.append(row);});}
temperature.addEventListener('input',update);nucleus.addEventListener('input',update);update();})();
