'use strict';

const panelMetricas = (() => {
  const elemento = id => document.getElementById(id);
  const actualizar = elemento('metricasActualizar');
  const meses = elemento('metricasMeses');
  const estado = elemento('metricasEstado');
  const error = elemento('metricasError');
  const datos = elemento('metricasDatos');
  let version = 0;
  let evolucion;
  let categorias;

  function nodo(tag, texto) {
    const el = document.createElement(tag);
    el.textContent = texto;
    return el;
  }

  function mostrarPares(id, pares) {
    const filas = pares.map(([etiqueta, valor]) => {
      const fila = document.createElement('div');
      fila.append(nodo('dt', etiqueta), nodo('dd', valor));
      return fila;
    });
    elemento(id).replaceChildren(...filas);
  }

  function mostrarLista(id, filas, etiqueta, vacio) {
    elemento(id).replaceChildren(
      ...(filas.length ? filas.map(fila => nodo('li', etiqueta(fila))) : [nodo('li', vacio)])
    );
  }

  function dibujar(anterior, id, type, data, options = {}) {
    if (anterior) {
      anterior.data = data;
      anterior.resize();
      anterior.update();
      return anterior;
    }
    return new Chart(elemento(id), {
      type, data,
      options: { responsive: true, maintainAspectRatio: false, ...options },
    });
  }

  function renderizar(resumen, puntos, filas, embudo, usuarios, reportes) {
    mostrarPares('metricasIndicadores', [
      ['Usuarios', resumen.usuarios.total],
      ['Usuarios activos', resumen.usuarios.activos],
      ['Nuevos (30 días)', resumen.usuarios.nuevosUltimos30Dias],
      ['Plantas', resumen.plantas.total],
      ['Disponibles', resumen.plantas.disponibles],
      ['Solicitadas', resumen.plantas.solicitadas],
      ['Adoptadas', resumen.plantas.adoptadas],
      ['Solicitudes', resumen.solicitudes.total],
      ['Pendientes', resumen.solicitudes.pendientes],
      ['Aceptadas', resumen.solicitudes.aceptadas],
      ['Adopciones completadas', resumen.adopciones.completadas],
      ['Reportes en revisión', resumen.reportes.enRevision],
    ]);
    evolucion = dibujar(evolucion, 'metricasEvolucion', 'line', {
      labels: puntos.map(p => p.periodo),
      datasets: [
        { label: 'Publicaciones', data: puntos.map(p => p.publicaciones), borderColor: '#2e7d4f' },
        { label: 'Solicitudes', data: puntos.map(p => p.solicitudes), borderColor: '#a46a32' },
        { label: 'Adopciones', data: puntos.map(p => p.adopcionesCompletadas), borderColor: '#486e94' },
        { label: 'Usuarios nuevos', data: puntos.map(p => p.usuariosNuevos), borderColor: '#77638b' },
      ],
    }, { tension: 0.25, scales: { y: { beginAtZero: true, ticks: { precision: 0 } } } });
    categorias = dibujar(categorias, 'metricasCategorias', 'bar', {
      labels: filas.map(f => f.categoria),
      datasets: [
        { label: 'Publicadas', data: filas.map(f => f.publicadas), backgroundColor: '#3a7650' },
        { label: 'Adoptadas', data: filas.map(f => f.adoptadas), backgroundColor: '#a5bb80' },
      ],
    }, { indexAxis: 'y', scales: { x: { beginAtZero: true, ticks: { precision: 0 } } } });
    mostrarPares('metricasEmbudo', [
      ['Publicadas', embudo.publicadas],
      ['Con al menos una solicitud', embudo.conSolicitud],
      ['Adoptadas', embudo.adoptadas],
      ['Tasa de conversión', embudo.tasaConversion + '%'],
    ]);
    const nombreYTotal = fila => fila.nombre + ' — ' + fila.total;
    mostrarLista('metricasDonantes', usuarios.topDonantes, nombreYTotal, 'Sin datos todavía');
    mostrarLista('metricasAdoptantes', usuarios.topAdoptantes, nombreYTotal, 'Sin datos todavía');
    mostrarLista('metricasReportesEstado', reportes.porEstado, fila => fila.estado + ': ' + fila.total, 'Sin reportes');
    mostrarLista('metricasReportesUsuarios', reportes.masReportados, nombreYTotal, 'Sin reportes');
  }

  async function cargar() {
    const solicitud = ++version;
    actualizar.disabled = true;
    error.hidden = true;
    estado.textContent = 'Cargando métricas…';
    try {
      const resultados = await Promise.all([
        adminApi('/metricas/resumen'),
        adminApi('/metricas/evolucion?meses=' + encodeURIComponent(meses.value)),
        adminApi('/metricas/plantas-por-categoria'),
        adminApi('/metricas/embudo'),
        adminApi('/metricas/usuarios?limite=5'),
        adminApi('/metricas/reportes?limite=5'),
      ]);
      if (solicitud !== version) return;
      datos.hidden = false;
      renderizar(...resultados);
      estado.textContent = 'Actualizado a las ' + new Date().toLocaleTimeString('es-SV');
    } catch (err) {
      if (solicitud !== version) return;
      datos.hidden = true;
      estado.textContent = '';
      error.textContent = err.message;
      error.hidden = false;
    } finally {
      if (solicitud === version) actualizar.disabled = false;
    }
  }

  function cancelarVista() {
    version++;
  }

  actualizar.addEventListener('click', cargar);
  meses.addEventListener('change', cargar);
  return { cargar, cancelarVista };
})();
