drop database if exists TED;
CREATE DATABASE IF NOT EXISTS TED;
USE TED;

CREATE TABLE usuarios(
	id_usuario int unsigned NOT NULL AUTO_INCREMENT,
    nombre varchar(30) not null,
    pem mediumtext,
    primary key(id_usuario)
);

create table calificaciones(
	id_calificacion int unsigned not null,
    nombre varchar(50),
    primary key(id_calificacion)
);

create table tags(
	id_tag int unsigned not null,
    nombre varchar(50),
    primary key(id_tag)
);

create table eventos(
	id_evento int unsigned not null,
    nombre varchar(50),
    primary key(id_evento)
);

create table ponentes(
	id_ponente int unsigned not null,
    nombre varchar(100),
    primary key(id_ponente)
);

create table ocupaciones(
	id_ocupacion int unsigned not null,
    nombre varchar(100),
    primary key(id_ocupacion)
);

create table charlas(
	id_charla int unsigned NOT NULL,
    ncomentarios int NOT NULL,
    descripcion varchar(1000) NOT NULL,
    duracion int NOT NULL,
    evento int unsigned NOT NULL,
    fechaPonencia int NOT NULL,
    idiomas int NOT NULL,
    ponente int unsigned NOT NULL,
    fechaPublicacion int NOT NULL,
    titulo varchar(100) NOT NULL,
    url varchar(200) NOT NULL,
    visitas int NOT NULL,
    transcripcion mediumtext NOT NULL,
    primary key(id_charla),
    foreign key (evento) references eventos(id_evento) on delete cascade,
    foreign key (ponente) references ponentes(id_ponente) on delete cascade
);

create table usuario_charla(
	id_usuario int unsigned not null,
    id_charla int unsigned not null,
    fecha_anadido datetime,
    primary key (id_usuario,id_charla),
    foreign key (id_usuario) references usuarios(id_usuario) on delete cascade,
    foreign key (id_charla) references charlas(id_charla) on delete cascade
);


create table calificacion_charla(
	id_charla int unsigned not null,
	id_calificacion int unsigned not null,
    count int,
    primary key (id_calificacion,id_charla),
    foreign key (id_charla) references charlas(id_charla) on delete cascade,
    foreign key (id_calificacion) references calificaciones(id_calificacion) on delete cascade    
);

create table tag_charla(
	id_charla int unsigned not null,
	id_tag int unsigned not null,  
    primary key(id_charla,id_tag),
    foreign key (id_charla) references charlas(id_charla) on delete cascade,
    foreign key (id_tag) references tags(id_tag) on delete cascade
);

create table ocupacion_ponente(
	id_ocupacion int unsigned not null,
	id_ponente int unsigned not null,  
    primary key(id_ocupacion,id_ponente),
    foreign key (id_ocupacion) references ocupaciones(id_ocupacion) on delete cascade,
    foreign key (id_ponente) references ponentes(id_ponente) on delete cascade
);


