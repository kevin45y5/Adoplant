const {test}=require('node:test'),assert=require('node:assert/strict'),vm=require('node:vm'),fs=require('node:fs'),path=require('node:path');
function setup(rol='donante',failure=false){
 const nodes=new Map(),calls=[];const node=()=>({hidden:false,disabled:false,handlers:{},addEventListener(k,v){this.handlers[k]=v},replaceChildren(){},append(){},showModal(){this.open=true},close(){this.open=false}});
 const el=id=>{if(!nodes.has(id))nodes.set(id,node());return nodes.get(id)};
 const a={id_adopcion:1,id_planta:7,id_solicitud:8,rol,estado:'EN_PROCESO',fecha_entrega:null,fecha_recepcion:null,donante:'Ana',adoptante:'Luis',planta:{nombre:'Monstera'}};
 const context={document:{getElementById:el,createElement:node,visibilityState:'visible'},window:{ADOPPLANT_API_URL:'https://api.test',location:{search:'?id=1',replace(){}}},sessionStorage:{getItem:()=> 'token'},URL,URLSearchParams,AbortController,setTimeout,clearTimeout,setInterval(){},fetch:async(url,options)=>{calls.push({url,options});const post=options.method==='POST';if(post&&!failure)a[rol==='donante'?'fecha_entrega':'fecha_recepcion']='2026-10-03T12:00:00Z';return {ok:!post||!failure,status:post&&failure?503:200,json:async()=>post&&failure?{detail:'No se pudo guardar'}:{...a}}}};
 vm.createContext(context);vm.runInContext(fs.readFileSync(path.join(__dirname,'../views/adopciones.js'),'utf8'),context);return {el,calls};
}
const tick=()=>new Promise(resolve=>setImmediate(resolve));
test('cada participante ve su acción y solo guarda al confirmar',async()=>{
 for(const rol of ['donante','adoptante']){const s=setup(rol);await tick();assert.equal(s.el('confirmDelivery').textContent,rol==='donante'?'Marcar como entregada':'Marcar como recibida');s.el('confirmDelivery').onclick();assert.equal(s.calls.length,1);assert.equal(s.el('deliveryDialog').open,true);await s.el('saveDelivery').onclick();assert.match(s.calls.at(-1).url,/\/1\/confirmar$/);assert.equal(s.el('confirmDelivery').disabled,true);assert.match(s.el('deliveryState').textContent,/Esperando/);await s.el('saveDelivery').onclick();assert.equal(s.calls.length,2);}
});
test('cancelar y error de servidor no anuncian una entrega guardada',async()=>{
 const s=setup('adoptante',true);await tick();s.el('confirmDelivery').onclick();s.el('cancelDelivery').onclick();assert.equal(s.calls.length,1);s.el('confirmDelivery').onclick();await s.el('saveDelivery').onclick();assert.match(s.el('deliveryFeedback').textContent,/No se pudo/);assert.equal(s.el('confirmDelivery').disabled,false);assert.match(s.el('adopterConfirmation').textContent,/Pendiente/);
});
