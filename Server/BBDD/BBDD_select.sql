USE TED;

select * from usuarios;

select * from charlas;

select * from calificaciones;

select * from tags;

select * from calificacion_charla;

select * from tag_charla;

select count(*) from calificacion_charla;

select * from usuario_charla;

SELECT COUNT(*) FROM charla;

select count(*) from charla where transcripcion is NULL;

select * from usuario;

select * from usuario_charla;

SELECT * FROM charlas WHERE id_charla=1;

select * from usuarios where nombre="axiel";

select * from eventos;

select * from ponentes;

select * from ocupaciones;

select * from ocupacion_ponente;

select nombre from eventos where id_evento=0;

select * from usuario_charla;

ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'root';

FLUSH hosts
