'use strict';
// Location updates travel through the authenticated, participant-only message API.
const ChatLocation = (() => {
  const prefix='[PlantHaven:ubicacion:1]';
  function decode(text){
    if(typeof text!=='string'||!text.startsWith(prefix))return null;
    try{
      const p=JSON.parse(text.slice(prefix.length));
      if(!['point','live','stop'].includes(p.kind)||typeof p.session!=='string'||p.session.length>100)return null;
      if(p.kind==='stop')return p;
      if(!Number.isFinite(p.lat)||Math.abs(p.lat)>90||!Number.isFinite(p.lng)||Math.abs(p.lng)>180)return null;
      if(!Number.isFinite(p.at)||!Number.isFinite(p.until)||typeof p.label!=='string'||p.label.length>255)return null;
      return p;
    }catch(_){return null;}
  }
  function active(p,now=Date.now()){return p.kind==='live'&&p.until>now&&p.at<=now+10000&&now-p.at<45000;}
  function requestBody(contenido){
    const p=decode(contenido);
    if(!p||p.kind==='stop')return {contenido};
    return {tipo:'UBICACION',contenido,latitud:p.lat,longitud:p.lng,descripcion:p.label};
  }
  function fromMessage(row){
    if(row.ubicacion)return decode(prefix+JSON.stringify(row.ubicacion));
    if(row.tipo==='UBICACION'&&row.punto){const p=row.punto;return decode(prefix+JSON.stringify({kind:'point',session:'point-'+row.id_mensaje,lat:p.latitud,lng:p.longitud,at:Date.parse(row.fecha_hora),until:0,label:p.descripcion||'Punto de encuentro'}));}
    return decode(row.contenido);
  }
  function mapUrl(p){const q=new URLSearchParams({bbox:[Math.max(-180,p.lng-.008),Math.max(-90,p.lat-.005),Math.min(180,p.lng+.008),Math.min(90,p.lat+.005)].join(','),layer:'mapnik',marker:p.lat+','+p.lng});return 'https://www.openstreetmap.org/export/embed.html?'+q;}
  function latest(rows){const groups=new Map();for(const row of rows){const p=fromMessage(row);if(p&&p.kind!=='point')groups.set(row.id_usuario+':'+p.session,Math.max(groups.get(row.id_usuario+':'+p.session)||0,row.id_mensaje));}return rows.filter(row=>{const p=fromMessage(row);return !p||p.kind==='point'||groups.get(row.id_usuario+':'+p.session)===row.id_mensaje;});}
  return {decode,fromMessage,active,mapUrl,latest,requestBody,encode:p=>prefix+JSON.stringify(p)};
})();
if(typeof module!=='undefined')module.exports=ChatLocation;
