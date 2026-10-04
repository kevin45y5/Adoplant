const {test}=require('node:test');
const assert=require('node:assert/strict');
const vm=require('node:vm');
const fs=require('node:fs');
const path=require('node:path');
function setup({own=false,pending=false,unavailable=false,postStatus=201}={}) {
  const elements=new Map(),calls=[];
  const node=()=>({hidden:true,children:[],handlers:{},value:'Quiero darle un hogar',addEventListener(k,v){this.handlers[k]=v;},append(...children){this.children.push(...children);},replaceChildren(...children){this.children=children;},showModal(){this.open=true;},close(){this.open=false;},reportValidity(){return true;}});
  const el=id=>{if(!elements.has(id))elements.set(id,node());return elements.get(id);};
  const plant={id_planta:7,id_usuario:own?1:2,nombre:'Monstera',estado_planta:unavailable?'ADOPTADA':'DISPONIBLE',visible:true,eliminada:false,puede_solicitar:true};
  const context={document:{getElementById:el,createElement:node},window:{ADOPPLANT_API_URL:'https://api.example/api',location:{search:'?id=7',replace(){}}},sessionStorage:{getItem:()=> 'token',removeItem(){}},URL,URLSearchParams,AbortController,setTimeout,clearTimeout,
    async fetch(url,options){calls.push({url,options});const post=options.method==='POST';return {ok:!post||postStatus===201,status:post?postStatus:200,json:async()=>post?(postStatus===201?{id_solicitud:9}:{detail:'La planta no está disponible'}):url.endsWith('/usuarios/me')?{id_usuario:1}:url.includes('/solicitudes?')?(pending?[{id_solicitud:9}]:[]):plant};}};
  vm.createContext(context);vm.runInContext(fs.readFileSync(path.join(__dirname,'../views/planta.js'),'utf8'),context);
  return {context,el,calls};
}
const tick=()=>new Promise(r=>setImmediate(r));
test('planta propia no permite abrir ni enviar solicitud incluso si la API indica permiso',async()=>{const s=setup({own:true});await tick();assert.equal(s.el('requestAdoption').disabled,true);assert.match(s.el('adoptionNotice').textContent,/tú publicaste/);s.el('requestAdoption').handlers.click();await s.el('adoptionForm').handlers.submit({preventDefault(){},currentTarget:s.el('adoptionForm')});assert.equal(s.el('adoptionDialog').open,undefined);assert.equal(s.calls.filter(c=>c.options.method==='POST').length,0);});
test('otra planta permite enviar mensaje y bloquea envíos duplicados',async()=>{const s=setup();await tick();assert.equal(s.el('requestAdoption').disabled,false);s.el('requestAdoption').handlers.click();assert.equal(s.el('adoptionDialog').open,true);const event={preventDefault(){},currentTarget:s.el('adoptionForm')};await s.el('adoptionForm').handlers.submit(event);await s.el('adoptionForm').handlers.submit(event);const posts=s.calls.filter(c=>c.options.method==='POST');assert.equal(posts.length,1);assert.deepEqual(JSON.parse(posts[0].options.body),{id_planta:7,mensaje:'Quiero darle un hogar'});assert.equal(s.el('requestAdoption').disabled,true);assert.equal(s.el('adoptionDialog').open,false);});
test('solicitud pendiente y planta adoptada bloquean nuevas solicitudes',async()=>{for(const options of [{pending:true},{unavailable:true}]){const s=setup(options);await tick();assert.equal(s.el('requestAdoption').disabled,true);}});
test('fallo del servidor no anuncia solicitud enviada',async()=>{const s=setup({postStatus:409});await tick();s.el('requestAdoption').handlers.click();await s.el('adoptionForm').handlers.submit({preventDefault(){},currentTarget:s.el('adoptionForm')});assert.equal(s.el('adoptionDialog').open,true);assert.match(s.el('requestStatus').textContent,/no está disponible/);assert.notEqual(s.el('requestAdoption').textContent,'Solicitud enviada');});
