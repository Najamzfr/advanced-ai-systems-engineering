(async()=>{'use strict';const root=document.querySelector('[data-paper-id]');if(!root)return;
const status=root.querySelector('.paper-status'),container=root.querySelector('.paper-canvas'),input=root.querySelector('[data-paper-page]'),prev=root.querySelector('[data-paper-prev]'),next=root.querySelector('[data-paper-next]'),zoom=root.querySelector('[data-paper-zoom]'),key='paper-page-'+root.dataset.paperId;
let pdf,pageNumber=1,request=0,renderTask;
try{
 const lib=await import('/pdfjs/pdf.mjs');lib.GlobalWorkerOptions.workerSrc='/pdfjs/pdf.worker.mjs';
 pdf=await lib.getDocument({url:root.dataset.pdfUrl,wasmUrl:'/pdfjs/wasm/',standardFontDataUrl:'/pdfjs/standard_fonts/',isEvalSupported:false}).promise;
 const api=window.CourseAPI,stored=Number(api?.state.answers[key]),linked=Number(new URLSearchParams(location.search).get('page'));
 pageNumber=linked||stored||Number(root.dataset.defaultPage)||1;pageNumber=Math.max(1,Math.min(pdf.numPages,Math.floor(pageNumber)));
 input.max=String(pdf.numPages);root.querySelector('[data-paper-count]').textContent='of '+pdf.numPages;
 async function render(n){const ticket=++request;renderTask?.cancel();pageNumber=Math.max(1,Math.min(pdf.numPages,Math.floor(Number(n)||1)));input.value=String(pageNumber);prev.disabled=pageNumber===1;next.disabled=pageNumber===pdf.numPages;status.textContent='Loading page '+pageNumber+'…';
 try{const page=await pdf.getPage(pageNumber);if(ticket!==request)return;const base=page.getViewport({scale:1}),width=Math.max(240,Math.min(1000,container.clientWidth||720)),viewport=page.getViewport({scale:width/base.width*Number(zoom.value)}),pixelRatio=Math.min(window.devicePixelRatio||1,2),canvas=document.createElement('canvas');canvas.width=Math.floor(viewport.width*pixelRatio);canvas.height=Math.floor(viewport.height*pixelRatio);canvas.style.width=viewport.width+'px';canvas.style.height=viewport.height+'px';canvas.setAttribute('role','img');canvas.setAttribute('aria-label','Page '+pageNumber+' of '+pdf.numPages+'. Use Read this page as text below for accessible text.');
 container.replaceChildren(canvas);renderTask=page.render({canvasContext:canvas.getContext('2d'),viewport,transform:pixelRatio!==1?[pixelRatio,0,0,pixelRatio,0,0]:null});await renderTask.promise;if(ticket!==request)return;
 if(api){api.state.answers[key]=String(pageNumber);api.save();}status.textContent='Page '+pageNumber+' of '+pdf.numPages;
 const content=await page.getTextContent();if(ticket!==request)return;root.querySelector('[data-paper-text]').textContent=content.items.map(x=>x.str+(x.hasEOL?'\n':' ')).join('');
 }catch(e){if(e.name!=='RenderingCancelledException'&&ticket===request)status.textContent='This page could not render. Try another page or open the course PDF copy below.';}}
 prev.addEventListener('click',()=>render(pageNumber-1));next.addEventListener('click',()=>render(pageNumber+1));input.addEventListener('change',()=>render(input.value));zoom.addEventListener('change',()=>render(pageNumber));root.querySelectorAll('[data-paper-jump]').forEach(b=>b.addEventListener('click',()=>{render(b.dataset.paperJump);root.querySelector('.paper-controls').scrollIntoView({block:'start'});}));
 let timer;window.addEventListener('resize',()=>{clearTimeout(timer);timer=setTimeout(()=>render(pageNumber),200);});await render(pageNumber);
}catch{status.textContent='The reader could not load. Reload this page or open the course PDF copy below. Your saved reading progress is unchanged.';}
})();
