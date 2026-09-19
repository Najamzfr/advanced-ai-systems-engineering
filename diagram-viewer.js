(()=>{'use strict';
fetch('/diagrams.json').then(r=>{if(!r.ok)throw Error();return r.json();}).then(data=>{
 document.querySelectorAll('[data-diagram]').forEach(fig=>{
 const d=data[fig.dataset.diagram],viewport=fig.querySelector('.diagram-scroll'),svg=viewport?.querySelector('svg');if(!d||!svg)return;
 const detail=fig.querySelector('.diagram-detail'),controls=fig.querySelector('.node-controls');
 function inspect(i){const c=d.contracts[i];if(!c)return;fig.querySelectorAll('[data-node]').forEach(g=>g.setAttribute('aria-pressed',String(Number(g.dataset.node)===i)));controls.querySelectorAll('button').forEach((b,j)=>b.setAttribute('aria-pressed',String(i===j)));detail.replaceChildren();const h=document.createElement('h4');h.textContent=d.nodes[i][0];detail.append(h);for(const[label,value]of Object.entries(c)){const p=document.createElement('p'),b=document.createElement('strong');b.textContent=({role:'Role',input:'Receives from',output:'Passes to',failure:'Failure to test'}[label]||label)+'. ';p.append(b,document.createTextNode(value));detail.append(p);}}
 d.nodes.forEach((n,i)=>{const b=document.createElement('button');b.type='button';b.textContent=n[0];b.setAttribute('aria-pressed','false');b.addEventListener('click',()=>inspect(i));controls.append(b);});
 svg.querySelectorAll('[data-node]').forEach(g=>{g.addEventListener('click',()=>inspect(Number(g.dataset.node)));g.addEventListener('keydown',e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();inspect(Number(g.dataset.node));}});});
 const dialog=fig.querySelector('.diagram-dialog'),expand=fig.querySelector('[data-expand-diagram]'),host=fig.querySelector('.diagram-host'),modal=dialog.querySelector('.diagram-modal-body');let zoom=1;
 function applyZoom(){const width=Number(svg.dataset.naturalWidth);svg.style.width=zoom===1?'100%':(width*1.1*zoom)+'px';svg.style.maxWidth=zoom===1?(width*1.1)+'px':'none';svg.style.minWidth=(width*zoom)+'px';fig.querySelector('[data-diagram-scale]').textContent=Math.round(zoom*100)+'%';}
 fig.querySelector('[data-zoom-in]').addEventListener('click',()=>{zoom=Math.min(2.5,zoom+.25);applyZoom();});fig.querySelector('[data-zoom-out]').addEventListener('click',()=>{zoom=Math.max(.5,zoom-.25);applyZoom();});fig.querySelector('[data-zoom-reset]').addEventListener('click',()=>{zoom=1;applyZoom();});
 const toolbar=fig.querySelector('.diagram-toolbar');expand.addEventListener('click',()=>{expand.hidden=true;modal.append(toolbar,viewport,detail);dialog.showModal();});dialog.querySelector('[data-close-diagram]').addEventListener('click',()=>dialog.close());dialog.addEventListener('close',()=>{fig.insertBefore(toolbar,host);host.append(viewport);controls.after(detail);expand.hidden=false;expand.focus();});applyZoom();
 });
}).catch(()=>document.querySelectorAll('.diagram-detail').forEach(e=>{e.textContent='The component notes could not load. The diagram and connection descriptions remain available. Reload to retry.';}));
})();
