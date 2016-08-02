--
-- PostgreSQL database dump
--

SET statement_timeout = 0;
SET lock_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;

--
-- Name: plpgsql; Type: EXTENSION; Schema: -; Owner: 
--

CREATE EXTENSION IF NOT EXISTS plpgsql WITH SCHEMA pg_catalog;


--
-- Name: EXTENSION plpgsql; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION plpgsql IS 'PL/pgSQL procedural language';


SET search_path = public, pg_catalog;

--
-- Name: create_uuid(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION create_uuid() RETURNS character varying
    LANGUAGE plpgsql
    AS $$DECLARE
    local_time double precision := EXTRACT(EPOCH FROM localtimestamp)::double precision;
    server_id character(3) := '001';
BEGIN
   -- f47ac10b-58cc-4372-a567-0e02b2c3d479

   return lpad(to_hex(floor(local_time)::int), 8, '0') || '-' ||
             lpad(to_hex(floor((local_time - floor(local_time))*100000)::int), 4, '0') || '-' ||
             '4' || server_id || '-' ||
             overlay(
                     to_hex((floor(random() * 65535)::int | (x'8000'::int) ) &  (x'bfff'::int)  ) ||
                     lpad(to_hex(floor(random() * 65535)::bigint),4,'0') || lpad(to_hex(floor(random() * 65535)::bigint),4,'0') || lpad(to_hex(floor(random() * 65535)::bigint),4,'0')
                  placing '-' from 5 for 0);

END$$;


ALTER FUNCTION public.create_uuid() OWNER TO postgres;

--
-- Name: row_cr_md(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION row_cr_md() RETURNS trigger
    LANGUAGE plpgsql
    AS $$BEGIN

   NEW.cr_tm = clock_timestamp();
   NEW.md_tm = NEW.cr_tm;

   return NEW;

END$$;


ALTER FUNCTION public.row_cr_md() OWNER TO postgres;

--
-- Name: row_id_cr_tm_md_tm(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION row_id_cr_tm_md_tm() RETURNS trigger
    LANGUAGE plpgsql
    AS $$BEGIN
   NEW.id = create_uuid();

   NEW.cr_tm = clock_timestamp();
   NEW.md_tm = NEW.cr_tm;

   return NEW;

END$$;


ALTER FUNCTION public.row_id_cr_tm_md_tm() OWNER TO postgres;

--
-- Name: row_md_tm(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION row_md_tm() RETURNS trigger
    LANGUAGE plpgsql
    AS $$BEGIN

NEW.md_tm = clock_timestamp();
RETURN NEW;

END$$;


ALTER FUNCTION public.row_md_tm() OWNER TO postgres;

SET default_tablespace = '';

SET default_with_oids = false;

--
-- Name: connection; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE connection (
    follower_id character varying(36) NOT NULL,
    followee_id character varying(36) NOT NULL
);


ALTER TABLE connection OWNER TO postgres;

--
-- Name: listener; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE listener (
    id character varying(63) NOT NULL,
    name character varying(1000),
    last_error character varying(1000),
    cr_tm timestamp with time zone NOT NULL,
    md_tm timestamp without time zone NOT NULL,
    connection_followers integer DEFAULT 0,
    connection_followees integer DEFAULT 0
);


ALTER TABLE listener OWNER TO postgres;

--
-- Name: progress; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE progress (
    id character varying(36) NOT NULL,
    cr_tm timestamp without time zone,
    md_tm timestamp without time zone,
    action character varying(50),
    comment character varying(50),
    data jsonb
);


ALTER TABLE progress OWNER TO postgres;

--
-- Name: state; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE state (
    var character varying(100) NOT NULL,
    val text NOT NULL,
    type character varying(100) DEFAULT 'string'::character varying NOT NULL
);


ALTER TABLE state OWNER TO postgres;

--
-- Name: pk_listener_id; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY listener
    ADD CONSTRAINT pk_listener_id PRIMARY KEY (id);


--
-- Name: listener_id_cr_tm; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER listener_id_cr_tm BEFORE INSERT ON listener FOR EACH ROW EXECUTE PROCEDURE row_id_cr_tm_md_tm();

ALTER TABLE listener DISABLE TRIGGER listener_id_cr_tm;


--
-- Name: listener_md; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER listener_md BEFORE UPDATE ON listener FOR EACH ROW EXECUTE PROCEDURE row_md_tm();


--
-- Name: tr_c; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER tr_c BEFORE INSERT ON listener FOR EACH ROW EXECUTE PROCEDURE row_cr_md();


--
-- Name: tr_progress_in; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER tr_progress_in BEFORE INSERT ON progress FOR EACH ROW EXECUTE PROCEDURE row_id_cr_tm_md_tm();


--
-- Name: tr_progress_up; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER tr_progress_up BEFORE UPDATE ON progress FOR EACH ROW EXECUTE PROCEDURE row_md_tm();


--
-- Name: fk_connection_followee; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY connection
    ADD CONSTRAINT fk_connection_followee FOREIGN KEY (followee_id) REFERENCES listener(id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: fk_connection_follower; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY connection
    ADD CONSTRAINT fk_connection_follower FOREIGN KEY (follower_id) REFERENCES listener(id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: public; Type: ACL; Schema: -; Owner: postgres
--

REVOKE ALL ON SCHEMA public FROM PUBLIC;
REVOKE ALL ON SCHEMA public FROM postgres;
GRANT ALL ON SCHEMA public TO postgres;
GRANT ALL ON SCHEMA public TO PUBLIC;


--
-- PostgreSQL database dump complete
--
