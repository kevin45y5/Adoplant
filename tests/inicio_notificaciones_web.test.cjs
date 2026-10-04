const {test}=require('node:test');
const assert=require('node:assert/strict');
const vm=require('node:vm');
const fs=require('node:fs');
const path=require('node:path');

function setup(rows,notifications=[]){
  const elements=new Map(),calls=[];
  function node(){return {value:'',hidden:false,children:[],handlers:{},append(...items){this.children.push(...items);},replaceChildren(...items){this.children=items;},addEventListener(name,handler){this.handlers[name]=handler;},setAttribute(){},focus(){}};}
  const el=id=>{if(!elements.has(id))elements.set(id,node());return elements.get(id);};
  const context={document:{getElementById:el,createElement:node,addEventListener(){},visibilityState:'visible'},window:{ADOPPLANT_API_URL:'https://api.example/api',addEventListener(){},location:{replace(){}}},sessionStorage:{getItem:key=>key==='token'?'token':null,removeItem(){}},localStorage:{removeItem(){}},URL,AbortController,setTimeout,clearTimeout,Date,fetch:async (url,options={})=>{calls.push(url);if(url.includes('/usuarios/me'))return {ok:true,status:200,json:async()=>({nombre:'María',correo:'maria@example.com',telefono:'7000'})};if(url.endsWith('/notificaciones'))return {ok:true,status:200,json:async()=>notifications};if(url.includes('/solicitudes?'))return {ok:true,status:200,json:async()=>rows};return {ok:true,status:200,json:async()=>({nombre:'Monstera deliciosa',fotografia_url:'https://cdn.example/monstera.jpg'})};}};
  vm.createContext(context);vm.runInContext(fs.readFileSync(path.join(__dirname,'../views/inicio.js'),'utf8'),context);
  return {context,el,calls};
}
const tick=()=>new Promise(resolve=>setImmediate(resolve));

test('muestra en inicio si una solicitud fue aceptada o rechazada',async()=>{
  const s=setup([
    {id_solicitud:12,id_planta:7,estado:'ACEPTADA',fecha_solicitud:'2026-10-03T12:00:00Z',nombre_planta:'Monstera deliciosa'},
    {id_solicitud:11,id_planta:8,estado:'RECHAZADA',fecha_solicitud:'2026-10-02T12:00:00Z',nombre_planta:'Calathea'},
  ]);
  await tick(); await s.context.window.loadAdoptionNotifications();
  assert.equal(s.el('notifications').hidden,true);
  assert.equal(s.el('notificationDot').hidden,false);
  s.el('notificationsNav').handlers.click({preventDefault(){}});
  assert.equal(s.el('notifications').hidden,false);
  assert.equal(s.el('notificationFeed').children.length,2);
  assert.match(s.el('notificationFeed').children[0].className,/accepted/);
  assert.match(s.el('notificationFeed').children[1].className,/rejected/);
  assert.match(s.el('notificationFeed').children[0].children[3].href,/id=12/);
});

test('oculta el apartado cuando todavía no hay solicitudes enviadas',async()=>{
  const s=setup([]); await tick(); await s.context.window.loadAdoptionNotifications();
  assert.equal(s.el('notifications').hidden,true);
  assert.equal(s.el('notificationFeed').children.length,1);
  assert.match(s.el('notificationFeed').children[0].textContent,/Todavía/);
});

test('marca con punto rojo una decisión no leída',async()=>{
  const s=setup([{id_solicitud:12,id_planta:7,estado:'ACEPTADA',fecha_solicitud:'2026-10-03T12:00:00Z',nombre_planta:'Monstera deliciosa'}],[{id_notificacion:40,tipo:'SOLICITUD_ACEPTADA',leida:false}]);
  await tick(); await s.context.window.loadAdoptionNotifications();
  assert.equal(s.el('notificationDot').hidden,false);
});

test('marca con punto rojo una solicitud rechazada aunque no exista aviso separado',async()=>{
  const s=setup([{id_solicitud:15,id_planta:8,estado:'RECHAZADA',fecha_solicitud:'2026-10-03T12:00:00Z',nombre_planta:'Calathea'}]);
  await tick(); await s.context.window.loadAdoptionNotifications();
  assert.equal(s.el('notificationDot').hidden,false);
  s.el('notificationsNav').handlers.click({preventDefault(){}});
  assert.equal(s.el('notificationDot').hidden,true);
});
