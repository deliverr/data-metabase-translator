create table report_card_error
(
	card_id int not null
		constraint pk_report_card_error
			primary key,
	dashboard_id int null,
	pulse_id int null,
	object_name varchar(256) null,
	error varchar(512) not null,
	created_at timestamp with time zone not null,
	updated_at timestamp with time zone not null
);
