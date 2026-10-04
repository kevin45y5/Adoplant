const {test}=require('node:test');
const assert=require('node:assert/strict');
const vm=require('node:vm');
const fs=require('node:fs');
const path=require('node:path');
function setup(failure=false, publishedId=null){
 const elements=new Map(), calls=[];
 function element(){return {value:'',children:[],options:[{}],hidden:false,handlers:{},append(...nodes){this.children.push(...nodes);},replaceChildren(...nodes){this.children=nodes;},addEventListener(k,v){this.handlers[k]=v;},remove(){this.options.pop();},showModal(){},close(){}};}
 const el=id=>{if(!elements.has(id))elements.set(id,element());return elements.get(id);};
 const plants=[{id_planta:1,nombre:'Monstera',tamano:'Grande',nivel_cuidado:'Bajo',ubicacion:'San Salvador',categoria:{nombre:'Interior'}},{id_planta:2,nombre:'Cactus',tamano:'Pequeña',nivel_cuidado:'Bajo',ubicacion:'Santa Ana',categoria:{nombre:'Exterior'}}];
 const context={document:{getElementById:el,createElement:element,querySelectorAll:()=>[]},window:{ADOPPLANT_API_URL:'https://api.example/api'},sessionStorage:{getItem:key=>key==='token'?'token':publishedId,removeItem(){publishedId=null;}},URL,AbortController,setTimeout,clearTimeout,logout(){},async fetch(url){calls.push(url);return {ok:!failure,status:failure?500:200,json:async()=>({total:2,plantas:plants})};}};
 vm.createContext(context);vm.runInContext(fs.readFileSync(path.join(__dirname,'../views/catalogo.js'),'utf8'),context);return {context,el,calls};
}
test('carga plantas reales y filtra por nombre y tamaño',async()=>{const s=setup();await s.context.window.loadPlantCatalog();assert.match(s.calls[0],/estado=DISPONIBLE/);assert.equal(s.el('plantGrid').children.length,2);s.el('search').value='monstera';s.el('search').handlers.input();assert.equal(s.el('plantGrid').children.length,1);s.el('size').value='Pequeña';s.el('size').handlers.change();assert.equal(s.el('plantGrid').children.length,0);assert.match(s.el('catalogStatus').textContent,/No encontramos/);s.el('clear').handlers.click();assert.equal(s.el('plantGrid').children.length,2);});
test('error de API ofrece reintento sin inventar publicaciones',async()=>{const s=setup(true);await s.context.window.loadPlantCatalog();assert.equal(s.el('retryCatalog').hidden,false);assert.match(s.el('catalogStatus').textContent,/No se pudo/);assert.equal(s.el('plantGrid').children.length,0);});

test('al volver de publicar limpia filtros y muestra la planta guardada primero',async()=>{const s=setup(false,'1');s.el('search').value='Cactus';s.el('size').value='Pequeña';await s.context.window.loadPlantCatalog();assert.equal(s.el('search').value,'');assert.equal(s.el('size').value,'');assert.equal(s.el('plantGrid').children.length,2);assert.equal(s.el('plantGrid').children[0].children[1].children[1].textContent,'Monstera');assert.equal(s.context.sessionStorage.getItem('catalogPublishedPlant'),null);});
