--
-- PostgreSQL database dump
--

\restrict 3HlxZV0JnUZiZPvPBFCOfTuV3eeJfYZFxHwdxdodTiTNutAk8YPz3Zk4eoF7H7x

-- Dumped from database version 18.6
-- Dumped by pg_dump version 18.6

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: public; Type: SCHEMA; Schema: -; Owner: -
--

CREATE SCHEMA IF NOT EXISTS public;


--
-- Name: SCHEMA public; Type: COMMENT; Schema: -; Owner: -
--

COMMENT ON SCHEMA public IS 'standard public schema';


--
-- Name: estado_adopcion; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.estado_adopcion AS ENUM (
    'EN_PROCESO',
    'COMPLETADA'
);


--
-- Name: estado_categoria; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.estado_categoria AS ENUM (
    'ACTIVA',
    'INACTIVA'
);


--
-- Name: estado_planta; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.estado_planta AS ENUM (
    'DISPONIBLE',
    'SOLICITADA',
    'ADOPTADA'
);


--
-- Name: estado_reporte; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.estado_reporte AS ENUM (
    'EN_REVISION',
    'RESUELTO'
);


--
-- Name: estado_solicitud; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.estado_solicitud AS ENUM (
    'PENDIENTE',
    'ACEPTADA',
    'RECHAZADA'
);


--
-- Name: estado_usuario; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.estado_usuario AS ENUM (
    'ACTIVO',
    'BLOQUEADO'
);


SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: administrador; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.administrador (
    id_administrador integer NOT NULL,
    id_usuario integer NOT NULL
);


--
-- Name: administrador_id_administrador_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.administrador_id_administrador_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: administrador_id_administrador_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.administrador_id_administrador_seq OWNED BY public.administrador.id_administrador;


--
-- Name: adopcion; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.adopcion (
    id_adopcion integer NOT NULL,
    estado public.estado_adopcion DEFAULT 'EN_PROCESO'::public.estado_adopcion NOT NULL,
    fecha_entrega timestamp with time zone,
    fecha_recepcion timestamp with time zone,
    id_solicitud integer NOT NULL,
    id_planta integer NOT NULL,
    id_donante integer NOT NULL,
    id_adoptante integer NOT NULL,
    CONSTRAINT chk_adopcion_confirmaciones CHECK ((((estado = 'COMPLETADA'::public.estado_adopcion) AND (fecha_entrega IS NOT NULL) AND (fecha_recepcion IS NOT NULL)) OR ((estado = 'EN_PROCESO'::public.estado_adopcion) AND ((fecha_entrega IS NULL) OR (fecha_recepcion IS NULL))))),
    CONSTRAINT chk_adopcion_distintos_usuarios CHECK ((id_donante <> id_adoptante))
);


--
-- Name: adopcion_id_adopcion_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.adopcion_id_adopcion_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: adopcion_id_adopcion_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.adopcion_id_adopcion_seq OWNED BY public.adopcion.id_adopcion;


--
-- Name: categoria; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.categoria (
    id_categoria integer NOT NULL,
    nombre character varying(100) NOT NULL,
    estado public.estado_categoria DEFAULT 'ACTIVA'::public.estado_categoria NOT NULL,
    CONSTRAINT categoria_nombre_check CHECK ((btrim((nombre)::text) <> ''::text))
);


--
-- Name: categoria_id_categoria_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.categoria_id_categoria_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: categoria_id_categoria_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.categoria_id_categoria_seq OWNED BY public.categoria.id_categoria;


--
-- Name: chat; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.chat (
    id_chat integer NOT NULL,
    fecha_creacion timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    id_planta integer NOT NULL
);


--
-- Name: chat_id_chat_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.chat_id_chat_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: chat_id_chat_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.chat_id_chat_seq OWNED BY public.chat.id_chat;


--
-- Name: chat_participante; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.chat_participante (
    id_chat integer NOT NULL,
    id_usuario integer NOT NULL,
    posicion smallint NOT NULL,
    CONSTRAINT chat_participante_posicion_check CHECK ((posicion = ANY (ARRAY[1, 2])))
);


--
-- Name: fotografia; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.fotografia (
    id_foto integer NOT NULL,
    url character varying(500) NOT NULL,
    fecha_carga timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    id_planta integer NOT NULL,
    CONSTRAINT fotografia_url_check CHECK ((btrim((url)::text) <> ''::text))
);


--
-- Name: fotografia_id_foto_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.fotografia_id_foto_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: fotografia_id_foto_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.fotografia_id_foto_seq OWNED BY public.fotografia.id_foto;


--
-- Name: mensaje; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.mensaje (
    id_mensaje integer NOT NULL,
    contenido text,
    fecha_hora timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    tipo character varying(20) DEFAULT 'TEXTO'::character varying NOT NULL,
    id_chat integer NOT NULL,
    id_usuario integer NOT NULL,
    CONSTRAINT chk_mensaje_contenido CHECK ((((tipo)::text = 'UBICACION'::text) OR ((contenido IS NOT NULL) AND (btrim(contenido) <> ''::text)))),
    CONSTRAINT mensaje_tipo_check CHECK (((tipo)::text = ANY ((ARRAY['TEXTO'::character varying, 'UBICACION'::character varying])::text[])))
);


--
-- Name: mensaje_id_mensaje_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.mensaje_id_mensaje_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: mensaje_id_mensaje_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.mensaje_id_mensaje_seq OWNED BY public.mensaje.id_mensaje;


--
-- Name: notificacion; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.notificacion (
    id_notificacion integer NOT NULL,
    tipo character varying(100) NOT NULL,
    mensaje text NOT NULL,
    fecha_hora timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    leida boolean DEFAULT false NOT NULL,
    id_usuario integer NOT NULL,
    id_solicitud integer,
    id_planta integer,
    CONSTRAINT notificacion_mensaje_check CHECK ((btrim(mensaje) <> ''::text)),
    CONSTRAINT notificacion_tipo_check CHECK ((btrim((tipo)::text) <> ''::text))
);


--
-- Name: notificacion_id_notificacion_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.notificacion_id_notificacion_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: notificacion_id_notificacion_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.notificacion_id_notificacion_seq OWNED BY public.notificacion.id_notificacion;


--
-- Name: planta; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.planta (
    id_planta integer NOT NULL,
    nombre character varying(100) NOT NULL,
    tamano character varying(50) NOT NULL,
    nivel_cuidado character varying(50) NOT NULL,
    estado_salud character varying(100) NOT NULL,
    necesidad_luz character varying(100) NOT NULL,
    necesidad_agua character varying(100) NOT NULL,
    descripcion text,
    ubicacion character varying(255) NOT NULL,
    estado public.estado_planta DEFAULT 'DISPONIBLE'::public.estado_planta NOT NULL,
    fecha_publicacion timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    visible boolean DEFAULT true NOT NULL,
    eliminada boolean DEFAULT false NOT NULL,
    motivo_moderacion text,
    fecha_moderacion timestamp with time zone,
    id_administrador_moderador integer,
    id_usuario integer NOT NULL,
    id_categoria integer NOT NULL,
    CONSTRAINT chk_eliminada_no_visible CHECK (((NOT eliminada) OR (NOT visible))),
    CONSTRAINT chk_moderacion_con_motivo CHECK (((id_administrador_moderador IS NULL) OR ((motivo_moderacion IS NOT NULL) AND (btrim(motivo_moderacion) <> ''::text) AND (fecha_moderacion IS NOT NULL)))),
    CONSTRAINT planta_estado_salud_check CHECK ((btrim((estado_salud)::text) <> ''::text)),
    CONSTRAINT planta_necesidad_agua_check CHECK ((btrim((necesidad_agua)::text) <> ''::text)),
    CONSTRAINT planta_necesidad_luz_check CHECK ((btrim((necesidad_luz)::text) <> ''::text)),
    CONSTRAINT planta_nivel_cuidado_check CHECK ((btrim((nivel_cuidado)::text) <> ''::text)),
    CONSTRAINT planta_nombre_check CHECK ((btrim((nombre)::text) <> ''::text)),
    CONSTRAINT planta_tamano_check CHECK ((btrim((tamano)::text) <> ''::text)),
    CONSTRAINT planta_ubicacion_check CHECK ((btrim((ubicacion)::text) <> ''::text))
);


--
-- Name: planta_id_planta_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.planta_id_planta_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: planta_id_planta_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.planta_id_planta_seq OWNED BY public.planta.id_planta;


--
-- Name: punto_encuentro; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.punto_encuentro (
    id_punto integer NOT NULL,
    latitud double precision NOT NULL,
    longitud double precision NOT NULL,
    descripcion character varying(255),
    id_mensaje integer NOT NULL,
    CONSTRAINT punto_encuentro_latitud_check CHECK (((latitud >= ('-90'::integer)::double precision) AND (latitud <= (90)::double precision))),
    CONSTRAINT punto_encuentro_longitud_check CHECK (((longitud >= ('-180'::integer)::double precision) AND (longitud <= (180)::double precision)))
);


--
-- Name: punto_encuentro_id_punto_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.punto_encuentro_id_punto_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: punto_encuentro_id_punto_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.punto_encuentro_id_punto_seq OWNED BY public.punto_encuentro.id_punto;


--
-- Name: recuperacion_contrasena; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.recuperacion_contrasena (
    id_recuperacion integer NOT NULL,
    id_usuario integer NOT NULL,
    codigo_hash character varying(255) NOT NULL,
    fecha_creacion timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    fecha_expiracion timestamp with time zone NOT NULL,
    utilizado boolean DEFAULT false NOT NULL,
    intentos smallint DEFAULT 0 NOT NULL,
    CONSTRAINT chk_recuperacion_expiracion CHECK ((fecha_expiracion > fecha_creacion)),
    CONSTRAINT recuperacion_contrasena_codigo_hash_check CHECK ((btrim((codigo_hash)::text) <> ''::text)),
    CONSTRAINT recuperacion_contrasena_intentos_check CHECK ((intentos >= 0))
);


--
-- Name: recuperacion_contrasena_id_recuperacion_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.recuperacion_contrasena_id_recuperacion_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: recuperacion_contrasena_id_recuperacion_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.recuperacion_contrasena_id_recuperacion_seq OWNED BY public.recuperacion_contrasena.id_recuperacion;


--
-- Name: reporte; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.reporte (
    id_reporte integer NOT NULL,
    motivo text NOT NULL,
    estado public.estado_reporte DEFAULT 'EN_REVISION'::public.estado_reporte NOT NULL,
    fecha_creacion timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    id_reportante integer NOT NULL,
    id_reportado integer NOT NULL,
    id_administrador integer,
    CONSTRAINT chk_no_autoreporte CHECK ((id_reportante <> id_reportado)),
    CONSTRAINT reporte_motivo_check CHECK ((btrim(motivo) <> ''::text))
);


--
-- Name: reporte_id_reporte_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.reporte_id_reporte_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: reporte_id_reporte_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.reporte_id_reporte_seq OWNED BY public.reporte.id_reporte;


--
-- Name: solicitud_adopcion; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.solicitud_adopcion (
    id_solicitud integer NOT NULL,
    mensaje character varying(500) NOT NULL,
    estado public.estado_solicitud DEFAULT 'PENDIENTE'::public.estado_solicitud NOT NULL,
    fecha_solicitud timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    id_planta integer NOT NULL,
    id_adoptante integer NOT NULL,
    CONSTRAINT solicitud_adopcion_mensaje_check CHECK ((btrim((mensaje)::text) <> ''::text))
);


--
-- Name: solicitud_adopcion_id_solicitud_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.solicitud_adopcion_id_solicitud_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: solicitud_adopcion_id_solicitud_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.solicitud_adopcion_id_solicitud_seq OWNED BY public.solicitud_adopcion.id_solicitud;


--
-- Name: usuario; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.usuario (
    id_usuario integer NOT NULL,
    nombre character varying(100) NOT NULL,
    apellido character varying(100) NOT NULL,
    correo character varying(150) NOT NULL,
    telefono character varying(20) NOT NULL,
    contrasena character varying(255) NOT NULL,
    estado public.estado_usuario DEFAULT 'ACTIVO'::public.estado_usuario NOT NULL,
    fecha_registro timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    CONSTRAINT usuario_apellido_check CHECK ((btrim((apellido)::text) <> ''::text)),
    CONSTRAINT usuario_contrasena_check CHECK ((btrim((contrasena)::text) <> ''::text)),
    CONSTRAINT usuario_correo_check CHECK ((btrim((correo)::text) <> ''::text)),
    CONSTRAINT usuario_nombre_check CHECK ((btrim((nombre)::text) <> ''::text)),
    CONSTRAINT usuario_telefono_check CHECK (((telefono IS NULL) OR (btrim((telefono)::text) <> ''::text)))
);


--
-- Name: usuario_id_usuario_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.usuario_id_usuario_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: usuario_id_usuario_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.usuario_id_usuario_seq OWNED BY public.usuario.id_usuario;


--
-- Name: administrador id_administrador; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.administrador ALTER COLUMN id_administrador SET DEFAULT nextval('public.administrador_id_administrador_seq'::regclass);


--
-- Name: adopcion id_adopcion; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.adopcion ALTER COLUMN id_adopcion SET DEFAULT nextval('public.adopcion_id_adopcion_seq'::regclass);


--
-- Name: categoria id_categoria; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.categoria ALTER COLUMN id_categoria SET DEFAULT nextval('public.categoria_id_categoria_seq'::regclass);


--
-- Name: chat id_chat; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.chat ALTER COLUMN id_chat SET DEFAULT nextval('public.chat_id_chat_seq'::regclass);


--
-- Name: fotografia id_foto; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.fotografia ALTER COLUMN id_foto SET DEFAULT nextval('public.fotografia_id_foto_seq'::regclass);


--
-- Name: mensaje id_mensaje; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.mensaje ALTER COLUMN id_mensaje SET DEFAULT nextval('public.mensaje_id_mensaje_seq'::regclass);


--
-- Name: notificacion id_notificacion; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.notificacion ALTER COLUMN id_notificacion SET DEFAULT nextval('public.notificacion_id_notificacion_seq'::regclass);


--
-- Name: planta id_planta; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.planta ALTER COLUMN id_planta SET DEFAULT nextval('public.planta_id_planta_seq'::regclass);


--
-- Name: punto_encuentro id_punto; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.punto_encuentro ALTER COLUMN id_punto SET DEFAULT nextval('public.punto_encuentro_id_punto_seq'::regclass);


--
-- Name: recuperacion_contrasena id_recuperacion; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.recuperacion_contrasena ALTER COLUMN id_recuperacion SET DEFAULT nextval('public.recuperacion_contrasena_id_recuperacion_seq'::regclass);


--
-- Name: reporte id_reporte; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.reporte ALTER COLUMN id_reporte SET DEFAULT nextval('public.reporte_id_reporte_seq'::regclass);


--
-- Name: solicitud_adopcion id_solicitud; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.solicitud_adopcion ALTER COLUMN id_solicitud SET DEFAULT nextval('public.solicitud_adopcion_id_solicitud_seq'::regclass);


--
-- Name: usuario id_usuario; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.usuario ALTER COLUMN id_usuario SET DEFAULT nextval('public.usuario_id_usuario_seq'::regclass);


--
-- Name: administrador administrador_id_usuario_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.administrador
    ADD CONSTRAINT administrador_id_usuario_key UNIQUE (id_usuario);


--
-- Name: administrador administrador_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.administrador
    ADD CONSTRAINT administrador_pkey PRIMARY KEY (id_administrador);


--
-- Name: adopcion adopcion_id_planta_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.adopcion
    ADD CONSTRAINT adopcion_id_planta_key UNIQUE (id_planta);


--
-- Name: adopcion adopcion_id_solicitud_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.adopcion
    ADD CONSTRAINT adopcion_id_solicitud_key UNIQUE (id_solicitud);


--
-- Name: adopcion adopcion_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.adopcion
    ADD CONSTRAINT adopcion_pkey PRIMARY KEY (id_adopcion);


--
-- Name: categoria categoria_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.categoria
    ADD CONSTRAINT categoria_pkey PRIMARY KEY (id_categoria);


--
-- Name: chat_participante chat_participante_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.chat_participante
    ADD CONSTRAINT chat_participante_pkey PRIMARY KEY (id_chat, id_usuario);


--
-- Name: chat chat_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.chat
    ADD CONSTRAINT chat_pkey PRIMARY KEY (id_chat);


--
-- Name: fotografia fotografia_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.fotografia
    ADD CONSTRAINT fotografia_pkey PRIMARY KEY (id_foto);


--
-- Name: mensaje mensaje_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.mensaje
    ADD CONSTRAINT mensaje_pkey PRIMARY KEY (id_mensaje);


--
-- Name: notificacion notificacion_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.notificacion
    ADD CONSTRAINT notificacion_pkey PRIMARY KEY (id_notificacion);


--
-- Name: planta planta_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.planta
    ADD CONSTRAINT planta_pkey PRIMARY KEY (id_planta);


--
-- Name: punto_encuentro punto_encuentro_id_mensaje_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.punto_encuentro
    ADD CONSTRAINT punto_encuentro_id_mensaje_key UNIQUE (id_mensaje);


--
-- Name: punto_encuentro punto_encuentro_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.punto_encuentro
    ADD CONSTRAINT punto_encuentro_pkey PRIMARY KEY (id_punto);


--
-- Name: recuperacion_contrasena recuperacion_contrasena_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.recuperacion_contrasena
    ADD CONSTRAINT recuperacion_contrasena_pkey PRIMARY KEY (id_recuperacion);


--
-- Name: reporte reporte_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.reporte
    ADD CONSTRAINT reporte_pkey PRIMARY KEY (id_reporte);


--
-- Name: solicitud_adopcion solicitud_adopcion_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.solicitud_adopcion
    ADD CONSTRAINT solicitud_adopcion_pkey PRIMARY KEY (id_solicitud);


--
-- Name: chat_participante uq_chat_posicion; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.chat_participante
    ADD CONSTRAINT uq_chat_posicion UNIQUE (id_chat, posicion);


--
-- Name: planta uq_planta_dueno; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.planta
    ADD CONSTRAINT uq_planta_dueno UNIQUE (id_planta, id_usuario);


--
-- Name: solicitud_adopcion uq_solicitud_datos; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.solicitud_adopcion
    ADD CONSTRAINT uq_solicitud_datos UNIQUE (id_solicitud, id_planta, id_adoptante);


--
-- Name: usuario usuario_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.usuario
    ADD CONSTRAINT usuario_pkey PRIMARY KEY (id_usuario);


--
-- Name: idx_adopcion_adoptante; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_adopcion_adoptante ON public.adopcion USING btree (id_adoptante);


--
-- Name: idx_adopcion_donante; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_adopcion_donante ON public.adopcion USING btree (id_donante);


--
-- Name: idx_chat_participante_usuario; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_chat_participante_usuario ON public.chat_participante USING btree (id_usuario);


--
-- Name: idx_chat_planta; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_chat_planta ON public.chat USING btree (id_planta);


--
-- Name: idx_fotografia_planta; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_fotografia_planta ON public.fotografia USING btree (id_planta);


--
-- Name: idx_mensaje_chat_fecha; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_mensaje_chat_fecha ON public.mensaje USING btree (id_chat, fecha_hora, id_mensaje);


--
-- Name: idx_mensaje_usuario; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_mensaje_usuario ON public.mensaje USING btree (id_usuario);


--
-- Name: idx_notificacion_usuario_fecha; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_notificacion_usuario_fecha ON public.notificacion USING btree (id_usuario, fecha_hora DESC);


--
-- Name: idx_planta_catalogo; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_planta_catalogo ON public.planta USING btree (estado, fecha_publicacion DESC) WHERE ((visible = true) AND (eliminada = false));


--
-- Name: idx_planta_categoria; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_planta_categoria ON public.planta USING btree (id_categoria);


--
-- Name: idx_planta_filtros; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_planta_filtros ON public.planta USING btree (tamano, nivel_cuidado);


--
-- Name: idx_planta_usuario; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_planta_usuario ON public.planta USING btree (id_usuario);


--
-- Name: idx_recuperacion_usuario; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_recuperacion_usuario ON public.recuperacion_contrasena USING btree (id_usuario);


--
-- Name: idx_reporte_reportado; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_reporte_reportado ON public.reporte USING btree (id_reportado);


--
-- Name: idx_solicitud_adoptante; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_solicitud_adoptante ON public.solicitud_adopcion USING btree (id_adoptante);


--
-- Name: idx_solicitud_planta; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_solicitud_planta ON public.solicitud_adopcion USING btree (id_planta);


--
-- Name: uq_categoria_nombre; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX uq_categoria_nombre ON public.categoria USING btree (lower(btrim((nombre)::text)));


--
-- Name: uq_solicitud_aceptada_por_planta; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX uq_solicitud_aceptada_por_planta ON public.solicitud_adopcion USING btree (id_planta) WHERE (estado = 'ACEPTADA'::public.estado_solicitud);


--
-- Name: uq_solicitud_activa_por_usuario; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX uq_solicitud_activa_por_usuario ON public.solicitud_adopcion USING btree (id_planta, id_adoptante) WHERE (estado = ANY (ARRAY['PENDIENTE'::public.estado_solicitud, 'ACEPTADA'::public.estado_solicitud]));


--
-- Name: uq_usuario_correo; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX uq_usuario_correo ON public.usuario USING btree (lower(btrim((correo)::text)));


--
-- Name: uq_usuario_telefono; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX uq_usuario_telefono ON public.usuario USING btree (btrim((telefono)::text));


--
-- Name: administrador administrador_id_usuario_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.administrador
    ADD CONSTRAINT administrador_id_usuario_fkey FOREIGN KEY (id_usuario) REFERENCES public.usuario(id_usuario);


--
-- Name: chat chat_id_planta_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.chat
    ADD CONSTRAINT chat_id_planta_fkey FOREIGN KEY (id_planta) REFERENCES public.planta(id_planta);


--
-- Name: chat_participante chat_participante_id_chat_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.chat_participante
    ADD CONSTRAINT chat_participante_id_chat_fkey FOREIGN KEY (id_chat) REFERENCES public.chat(id_chat) ON DELETE CASCADE;


--
-- Name: chat_participante chat_participante_id_usuario_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.chat_participante
    ADD CONSTRAINT chat_participante_id_usuario_fkey FOREIGN KEY (id_usuario) REFERENCES public.usuario(id_usuario);


--
-- Name: adopcion fk_adopcion_donante; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.adopcion
    ADD CONSTRAINT fk_adopcion_donante FOREIGN KEY (id_planta, id_donante) REFERENCES public.planta(id_planta, id_usuario);


--
-- Name: adopcion fk_adopcion_solicitud; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.adopcion
    ADD CONSTRAINT fk_adopcion_solicitud FOREIGN KEY (id_solicitud, id_planta, id_adoptante) REFERENCES public.solicitud_adopcion(id_solicitud, id_planta, id_adoptante);


--
-- Name: mensaje fk_mensaje_participante; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.mensaje
    ADD CONSTRAINT fk_mensaje_participante FOREIGN KEY (id_chat, id_usuario) REFERENCES public.chat_participante(id_chat, id_usuario) ON DELETE CASCADE;


--
-- Name: fotografia fotografia_id_planta_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.fotografia
    ADD CONSTRAINT fotografia_id_planta_fkey FOREIGN KEY (id_planta) REFERENCES public.planta(id_planta) ON DELETE CASCADE;


--
-- Name: notificacion notificacion_id_planta_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.notificacion
    ADD CONSTRAINT notificacion_id_planta_fkey FOREIGN KEY (id_planta) REFERENCES public.planta(id_planta) ON DELETE SET NULL;


--
-- Name: notificacion notificacion_id_solicitud_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.notificacion
    ADD CONSTRAINT notificacion_id_solicitud_fkey FOREIGN KEY (id_solicitud) REFERENCES public.solicitud_adopcion(id_solicitud) ON DELETE SET NULL;


--
-- Name: notificacion notificacion_id_usuario_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.notificacion
    ADD CONSTRAINT notificacion_id_usuario_fkey FOREIGN KEY (id_usuario) REFERENCES public.usuario(id_usuario) ON DELETE CASCADE;


--
-- Name: planta planta_id_administrador_moderador_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.planta
    ADD CONSTRAINT planta_id_administrador_moderador_fkey FOREIGN KEY (id_administrador_moderador) REFERENCES public.administrador(id_administrador);


--
-- Name: planta planta_id_categoria_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.planta
    ADD CONSTRAINT planta_id_categoria_fkey FOREIGN KEY (id_categoria) REFERENCES public.categoria(id_categoria);


--
-- Name: planta planta_id_usuario_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.planta
    ADD CONSTRAINT planta_id_usuario_fkey FOREIGN KEY (id_usuario) REFERENCES public.usuario(id_usuario);


--
-- Name: punto_encuentro punto_encuentro_id_mensaje_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.punto_encuentro
    ADD CONSTRAINT punto_encuentro_id_mensaje_fkey FOREIGN KEY (id_mensaje) REFERENCES public.mensaje(id_mensaje) ON DELETE CASCADE;


--
-- Name: recuperacion_contrasena recuperacion_contrasena_id_usuario_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.recuperacion_contrasena
    ADD CONSTRAINT recuperacion_contrasena_id_usuario_fkey FOREIGN KEY (id_usuario) REFERENCES public.usuario(id_usuario) ON DELETE CASCADE;


--
-- Name: reporte reporte_id_administrador_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.reporte
    ADD CONSTRAINT reporte_id_administrador_fkey FOREIGN KEY (id_administrador) REFERENCES public.administrador(id_administrador);


--
-- Name: reporte reporte_id_reportado_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.reporte
    ADD CONSTRAINT reporte_id_reportado_fkey FOREIGN KEY (id_reportado) REFERENCES public.usuario(id_usuario);


--
-- Name: reporte reporte_id_reportante_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.reporte
    ADD CONSTRAINT reporte_id_reportante_fkey FOREIGN KEY (id_reportante) REFERENCES public.usuario(id_usuario);


--
-- Name: solicitud_adopcion solicitud_adopcion_id_adoptante_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.solicitud_adopcion
    ADD CONSTRAINT solicitud_adopcion_id_adoptante_fkey FOREIGN KEY (id_adoptante) REFERENCES public.usuario(id_usuario);


--
-- Name: solicitud_adopcion solicitud_adopcion_id_planta_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.solicitud_adopcion
    ADD CONSTRAINT solicitud_adopcion_id_planta_fkey FOREIGN KEY (id_planta) REFERENCES public.planta(id_planta);


--
-- PostgreSQL database dump complete
--

\unrestrict 3HlxZV0JnUZiZPvPBFCOfTuV3eeJfYZFxHwdxdodTiTNutAk8YPz3Zk4eoF7H7x

