create schema top100Libros;
use top100Libros;
create table book(
	id_local int auto_increment,
    title_book varchar(70),
    url varchar(100),
    price_pesos_arg double,
    price_official_dollar double,
    price_blue_dollar double,
    date date,
    primary key (id_local) 
);

select * from book;