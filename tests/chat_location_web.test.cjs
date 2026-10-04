const {test}=require('node:test');
const assert=require('node:assert/strict');
const vm=require('node:vm');
const fs=require('node:fs');
const path=require('node:path');
const location=require('../views/chat-location.js');
const point={kind:'live',session:'one',lat:13.7,lng:-89.2,at:Date.now(),until:Date.now()+900000,label:'Parque'};
test('valida coordenadas y distingue ubicación actual de señal vencida',()=>{
  assert.equal(location.decode(location.encode({...point,lat:99})),null);
  assert.equal(location.decode(location.encode({...point,lng:'javascript:alert(1)'})),null);
  assert.equal(location.active(point,point.at+20000),true);
  assert.equal(location.active(point,point.at+46000),false);
  assert.equal(location.active({...point,until:point.at},point.at+1),false);
  assert.equal(new URL(location.mapUrl(point)).hostname,'www.openstreetmap.org');
});
test('detener reemplaza actualizaciones del mismo remitente sin afectar al otro',()=>{
  const rows=[{id_mensaje:1,id_usuario:1,contenido:location.encode(point)},{id_mensaje:2,id_usuario:2,contenido:location.encode(point)},{id_mensaje:3,id_usuario:1,contenido:location.encode({kind:'stop',session:'one'})}];
  assert.deepEqual(location.latest(rows).map(r=>r.id_mensaje),[2,3]);
});
function setup(userId=2, sharedRows=[]){
  const nodes=new Map(),sent=[],intervals=[],cleared=[];let success,failure,watchSuccess,watchCount=0;
  function node(){return {hidden:false,disabled:false,value:'',checked:false,children:[],handlers:{},scrollHeight:0,scrollTop:0,clientHeight:0,append(...n){for(const child of n){child.remove();child.parent=this;this.children.push(child)}},insertBefore(child,before){child.remove();child.parent=this;const index=before?this.children.indexOf(before):this.children.length;this.children.splice(index,0,child)},remove(){if(this.parent){const siblings=this.parent.children;siblings.splice(siblings.indexOf(this),1);this.parent=null;}},replaceChildren(...n){for(const child of [...this.children])child.remove();this.children=[];this.append(...n)},addEventListener(n,fn){this.handlers[n]=fn},showModal(){this.open=true},close(){this.open=false}};}
  const el=id=>{if(!nodes.has(id))nodes.set(id,node());return nodes.get(id);};
  const user={id_usuario:userId},chat={id_chat:8,id_planta:7},rows=sharedRows;
  const context={ChatLocation:location,URL,URLSearchParams,AbortController,crypto:{randomUUID:()=> 'session-id'},Date,setTimeout:()=>1,clearTimeout(){},setInterval:fn=>{intervals.push(fn);return intervals.length},clearInterval(){},document:{getElementById:el,createElement:node,visibilityState:'visible'},window:{ADOPPLANT_API_URL:'https://example.test/api',isSecureContext:true,location:{search:'?planta=7',replace(){}},addEventListener(){}},sessionStorage:{getItem:()=> 'token',removeItem(){}},navigator:{geolocation:{getCurrentPosition(fn,err){success=fn;failure=err},watchPosition(fn){watchSuccess=fn;watchCount++;return 77},clearWatch(id){cleared.push(id)}}},fetch:async(url,opts)=>{
    let data=url.endsWith('/usuarios/me')?user:url.endsWith('/chats')?(opts.method==='POST'?chat:[chat]):url.includes('/plantas/')?{nombre:'Monstera'}:{total:rows.length,mensajes:rows};
    if(url.endsWith('/mensajes')&&opts.method==='POST'){const contenido=JSON.parse(opts.body).contenido;sent.push({url,contenido});data={id_mensaje:rows.length+1,id_usuario:userId,contenido,fecha_hora:new Date().toISOString()};const ubicacion=location.decode(contenido);if(ubicacion){data.ubicacion=ubicacion;data.contenido='Ubicación compartida';}rows.push(data);}
    return {ok:true,status:200,json:async()=>data};
  }};
  vm.createContext(context);vm.runInContext(fs.readFileSync(path.join(__dirname,'../views/mensajes.js'),'utf8'),context);
  return {el,sent,cleared,poll:()=>intervals[0](),update:()=>intervals[1](),move:(lat,lng)=>watchSuccess({coords:{latitude:lat,longitude:lng},timestamp:Date.now()}),watchCount:()=>watchCount,position:()=>success({coords:{latitude:13.7,longitude:-89.2,accuracy:20},timestamp:Date.now()}),deny:()=>failure({code:1})};
}
const tick=()=>new Promise(resolve=>setImmediate(resolve));
test('solo comparte después de confirmar y detiene el GPS y el aviso del chat',async()=>{
  const s=setup();await tick();s.el('openLocation').onclick();s.el('locateMe').onclick();s.position();
  assert.equal(s.sent.length,0);assert.equal(s.watchCount(),0);
  s.el('liveOption').checked=true;await s.el('sendLocation').onclick();
  assert.equal(location.decode(s.sent[0].contenido).kind,'live');assert.equal(s.watchCount(),1);
  assert.match(s.sent[0].url,/\/chats\/8\/mensajes$/);
  await s.el('stopLocation').onclick();assert.deepEqual(s.cleared,[77]);assert.equal(location.decode(s.sent.at(-1).contenido).kind,'stop');
});
test('permiso denegado no envía coordenadas y un punto fijo no activa seguimiento',async()=>{
  const s=setup();await tick();s.el('openLocation').onclick();s.el('locateMe').onclick();s.deny();
  assert.equal(s.sent.length,0);assert.equal(s.el('sendLocation').disabled,true);assert.match(s.el('locationStatus').textContent,/Permite/);
  s.el('locateMe').onclick();s.position();await s.el('sendLocation').onclick();assert.equal(location.decode(s.sent[0].contenido).kind,'point');assert.equal(s.watchCount(),0);
});


test('el adoptante recibe el mapa del donante y sus nuevas coordenadas sin mostrar JSON',async()=>{
  const rows=[],donante=setup(1,rows),adoptante=setup(2,rows);await tick();
  donante.el('openLocation').onclick();donante.el('locateMe').onclick();donante.position();
  donante.el('liveOption').checked=true;await donante.el('sendLocation').onclick();
  const frame=()=>adoptante.el('messageList').children[0].children.find(n=>n.className==='map-frame');
  adoptante.poll();await tick();
  assert.match(frame().src,/marker=13.7%2C-89.2/);
  assert.equal(adoptante.el('messageList').children[0].className,'message location');
  assert.match(adoptante.el('messageList').children[0].children[0].textContent,/tiempo real/);
  donante.move(13.71,-89.21);await donante.update();adoptante.poll();await tick();
  assert.equal(adoptante.el('messageList').children.length,1);
  assert.match(frame().src,/marker=13.71%2C-89.21/);
  assert.doesNotMatch(JSON.stringify(adoptante.el('messageList').children,(key,value)=>key==='parent'?undefined:value),/PlantHaven:ubicacion/);
  await donante.el('stopLocation').onclick();adoptante.poll();await tick();
  assert.match(adoptante.el('messageList').children[0].children[0].textContent,/finalizada/);
  assert.equal(frame(),undefined);
});

test('también muestra los puntos de encuentro de la API y mensajes de ubicación anteriores',()=>{
  const old={contenido:location.encode(point)};
  assert.equal(location.fromMessage(old).lat,point.lat);
  const row={tipo:'UBICACION',id_mensaje:9,fecha_hora:new Date().toISOString(),punto:{latitud:13.7,longitud:-89.2,descripcion:'Parque'}};
  assert.equal(location.fromMessage(row).kind,'point');
  assert.equal(location.fromMessage(row).label,'Parque');
});


test('envía ubicación nativa que la app móvil reconoce sin interpretar el texto interno',()=>{
  for(const kind of ['point','live']){
    const body=location.requestBody(location.encode({...point,kind}));
    assert.equal(body.tipo,'UBICACION');
    assert.equal(body.latitud,13.7);
    assert.equal(body.longitud,-89.2);
    assert.equal(body.descripcion,'Parque');
    assert.equal(location.decode(body.contenido).kind,kind);
  }
  assert.deepEqual(location.requestBody('Hola'),{contenido:'Hola'});
});


test('consultar mensajes y recibir texto conserva el mapa adjunto sin recargarlo',async()=>{
  const rows=[{id_mensaje:1,id_usuario:1,contenido:location.encode(point),fecha_hora:new Date().toISOString()}];
  const s=setup(2,rows);await tick();
  const list=s.el('messageList'),bubble=list.children[0],frame=bubble.children.find(n=>n.className==='map-frame');
  let detached=0,sourceWrites=0;const originalRemove=frame.remove;
  const removeBubble=bubble.remove;bubble.remove=function(){detached++;removeBubble.call(this)};
  frame.remove=function(){detached++;originalRemove.call(this)};
  let source=frame.src;Object.defineProperty(frame,'src',{get:()=>source,set:value=>{sourceWrites++;source=value;}});
  s.poll();await tick();s.poll();await tick();
  rows.push({id_mensaje:2,id_usuario:1,contenido:'Voy llegando',fecha_hora:new Date().toISOString()});
  s.poll();await tick();
  assert.equal(list.children[0],bubble);assert.equal(list.children.length,2);
  assert.equal(detached,0);assert.equal(sourceWrites,0);
  rows.push({id_mensaje:3,id_usuario:1,contenido:location.encode({...point,at:point.at+1000}),fecha_hora:new Date().toISOString()});
  s.poll();await tick();
  assert.equal(detached,0);assert.equal(sourceWrites,0);
});
