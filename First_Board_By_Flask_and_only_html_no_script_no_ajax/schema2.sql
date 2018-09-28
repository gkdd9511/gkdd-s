CREATE TABLE posts(num INTEGER primary key autoincrement, title varchar(30), writer varchar(20), content varchar(244), filename varchar(30), date timestamp default (datetime('now','localtime')));
