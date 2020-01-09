create table report_card_migration
(
	card_id int not null
		constraint pk_report_card_migration
			primary key,
	source_database_id integer,
	target_database_id integer,
	original_query text not null,
	query text not null,
	dataset_query text not null,
	created_at timestamp with time zone not null,
	updated_at timestamp with time zone not null
);
