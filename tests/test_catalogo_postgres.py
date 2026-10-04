import os
import pytest
from app.models import Planta
from tests.test_integracion_grupal_postgres import grupo
pytestmark = pytest.mark.skipif(os.getenv('SCRUM6_TEST_DB') != '1', reason='PostgreSQL local')

def test_catalogo_filtros_paginacion_y_visibilidad(grupo):
    c, db, datos, _ = grupo
    datos.pop('clave',None)
    base = db.get(Planta, datos['plantas']['disponible'])
    ids=[]
    for size, care in [('Pequeno','Bajo'),('Grande','Alto'),('Pequeno','Alto')]:
        p=Planta(nombre='CatalogoScrum10',tamano=size,nivel_cuidado=care,estado_salud='Sana',necesidad_luz='Indirecta',necesidad_agua='Semanal',ubicacion='ZonaScrum10',id_categoria=base.id_categoria,id_usuario=base.id_usuario)
        db.add(p); db.flush();ids.append(p.id_planta)
    db.commit()
    query={'busqueda':'CatalogoScrum10','limite':2}
    first=c.get('/api/plantas',params=query).json()
    second=c.get('/api/plantas',params={**query,'pagina':2}).json()
    assert first['total']==3 and first['hay_mas'] and not second['hay_mas']
    found=[p['id_planta'] for p in first['plantas']+second['plantas']]
    assert len(set(found))==3 and set(found)==set(ids)
    assert c.get('/api/plantas',params=query).json()['plantas']==first['plantas']
    r=c.get('/api/plantas',params={**query,'tamano':' pequeno ','nivel_cuidado':'alto'}).json()
    assert r['total']==1 and r['plantas'][0]['id_planta']==ids[2]
    assert 'Grande' in r['filtros']['tamano']
    assert c.get('/api/plantas',params={**query,'tamano':'Sin coincidencias'}).json()['total']==0
    invalid={datos['plantas'][k] for k in ['solicitada','adoptada','oculta','eliminada']}
    visible=c.get('/api/plantas',params={'limite':100}).json()['plantas']
    assert not invalid & {p['id_planta'] for p in visible}
    assert all(p['estado_planta']=='DISPONIBLE' for p in visible)
    for query in [{'pagina':0},{'limite':101},{'tamano':' '},{'nivel_cuidado':''},{'estado':'INVALIDO'}]:
        assert c.get('/api/plantas',params=query).status_code==422
