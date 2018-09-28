CREATE TABLE comments (num INTEGER primary key autoincrement, writer varchar(20), content varchar(244), p_num int, date timestamp default (datetime('now','localtime')));
