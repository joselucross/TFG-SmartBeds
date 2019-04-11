--Code generated by CodeSketch, version:  0.0.2

CREATE TABLE `Users` (
	`password` char(88) NOT NULL, --88 es el tamaño de un hash SHA512 con base 64
	`token` char(88) NOT NULL,
	`rol` char(5) NOT NULL,
	`nickname` varchar(50) NOT NULL,
	`IDU` int(11) UNSIGNED AUTO_INCREMENT,
	PRIMARY KEY (`IDU`),
	UNIQUE (`token`),
	UNIQUE (`nickname`)
);

CREATE TABLE `Beds` (
	`MAC` char(12),
	`bed_name` varchar(50) NOT NULL,
	`UUID` char(12),
	`port` int(11) UNSIGNED NOT NULL,
	`ip_group` char(15) NOT NULL, --12 es el tamaño de una dirección IP
	`IDB` int(11) UNSIGNED AUTO_INCREMENT ,
	PRIMARY KEY (`IDB`),
	UNIQUE (`port`, `ip_group`),
	UNIQUE (`bed_name`)
);

CREATE TABLE `Users_Beds` (
	`IDB` int(11) UNSIGNED,
	`IDU` int(11) UNSIGNED,
	PRIMARY KEY (`IDU`, `IDB`),
	FOREIGN KEY (`IDB`) REFERENCES `Beds`(`IDB`),
	FOREIGN KEY (`IDU`) REFERENCES `Users`(`IDU`)
);