/*CREATE TABLE usuario (
    id_usr INT AUTO_INCREMENT PRIMARY KEY,
    nombre_usuario VARCHAR(50) UNIQUE NOT NULL,
    correo_electronico VARCHAR(100) UNIQUE NOT NULL,
    contraseña_hash VARCHAR(255) NOT NULL,
    creado_en DATE,
    ultima_modificacion DATE
);
CREATE TABLE credencial (
    id_crd INT AUTO_INCREMENT PRIMARY KEY,
    id_usrcrd INT,
    id_ico INT,
    nombre_sitio VARCHAR(100) NOT NULL,
    url_sitio VARCHAR(255),
    nombre_usuario_sitio VARCHAR(100) NOT NULL,
    contraseña_sitio_hash VARCHAR(255) NOT NULL,
    creado_en DATE,
    ultima_modificacion DATE
);*/

/*
DELETE FROM icon WHERE id_ico > 7;
*//*
SELECT nombre_sitio, url_sitio, nombre_usuario_sitio, contraseña_sitio_hash FROM credencial WHERE id_usrcrd=1;
*/
SELECT * FROM credencial;